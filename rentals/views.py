from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .models import Rental, DamageReport, Review
from .serializers import RentalSerializer, DamageReportSerializer, ReviewSerializer
from users.models import User
from django.shortcuts import get_object_or_404
from vehicles.models import Vehicle
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
import stripe
from .utils import calculate_rental_cost, is_vehicle_available_for_new_dates
from datetime import datetime
from decimal import Decimal


class RentalViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Rental.objects.all().order_by('-rental_start')
    serializer_class = RentalSerializer

    def perform_create(self, serializer):

        user_id = self.request.data.get('user_id')
        if not user_id:
            raise ValueError('A "user_id" is required for booking.')
        
        user_instance = get_object_or_404(User, pk=user_id)

        rental_instance = serializer.save(
            user=user_instance,
            status='active' # New rentals are always 'active'
         )
    
    # 1. Return Vehicle Endpoint: PUT /rentals/{id}/return/ [cite: 31]
    # detail=True means this action is on a specific instance (needs {id} in URL path)
    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated])
    def return_vehicle(self, request, pk=None):
        rental = self.get_object()

        if rental.status not in ['active', 'confirmed']:
            return Response({'detail': 'This rental is not currently active or confirmed.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update status to completed
        rental.status = 'completed'
        rental.rental_end = timezone.now() # Record the actual return time
        rental.save()

        # Optional: Update Vehicle availability if your model tracks it
        # rental.vehicle.availability_status = True
        # rental.vehicle.save()

        return Response(self.get_serializer(rental).data, status=status.HTTP_200_OK)


    # 2. Rental History Endpoint: GET /rentals/history/{user_id}/ [cite: 32]
    # detail=False means this action is on the list (no {id} needed in URL path)
    @action(detail=False, methods=['get'], url_path='history/(?P<user_pk>[^/.]+)', permission_classes=[IsAuthenticated])
    def history(self, request, user_pk=None):
        # Security Check: Users should only see their own history unless they are an Admin
        if not request.user.is_staff and str(request.user.pk) != user_pk:
             return Response({'detail': 'You do not have permission to view this history.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user_instance = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        queryset = Rental.objects.filter(user=user_instance).order_by('-rental_start')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # 3. Checkout Endpoint: POST /rentals/{id}/checkout/ [cite: 33]
    @action(detail=True, methods=['post'], url_path='checkout', permission_classes=[IsAuthenticated])
    def checkout(self, request, pk=None):
        rental = self.get_object()

        #A. Validation: only active rentals can be checked out
        if rental.status != 'active':
            return Response({'detail': f'Rental status is {rental.status}. Cannot checkout.'}, status=status.HTTP_400_BAD_REQUEST)

        #B. Calculate final cost
        try:
            rental_rate_per_day = rental.vehicle.rental_rate_per_day
            cost = calculate_rental_cost(rental.rental_start, rental.rental_end, rental_rate_per_day)
            amount_in_cents = int(cost * 100)  # Stripe works with the smallest currency unit
        except Exception as e:
            return Response({'detail': f'Error calculating rental cost: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        #C. Create Stripe Payment Intent (Simulated here)
        # Note: In a real app, the frontend sends a payment method ID or token to complete the payment
        try:
            intent = stripe.PaymentIntent.create(
                amount = amount_in_cents,
                currency = 'usd',
                payment_method_types = ['card'],
                metadata = {'rental_id': rental.id, 'user_id': rental.user.id}
            )
        except stripe.error.StripeError as e:
            return Response({'detail': f'Stripe payment failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        #D. Update Rental with payment intent details
        rental.total_cost = cost
        rental.payment_intent_id = intent.id
        rental.status = 'confirmed'
        rental.save()
        return Response({
            'detail': 'Checkout successful. Rental confirmed.',
            'total_cost': cost,
            'payment_intent_id': intent.id
        }, status=status.HTTP_200_OK)
    
    # 4. Implement refund and cancellation endpoints
    #DELETE /rentals/{id}/
    def destroy(self, request, pk=None):
        rental = self.get_object()

        if rental.status == 'completed':
            return Response({'detail': 'Cannot cancel a completed rental.'}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize message for rentals that are 'active' but not yet 'confirmed' (paid)
        refund_status_message = "No refund processed (Rental was not yet paid/confirmed)."

        # Process refund only if payment was confirmed
        if rental.status == 'confirmed' and rental.payment_intent_id:
            try:
                # 1. Initiate Refund via Stripe
                refund = stripe.Refund.create(
                    payment_intent=rental.payment_intent_id,
                    # partial refunds logic can be added here
                )
                # 2. Update message upon successful refund
                refund_status_message = f"Refund successful. Stripe Refund ID: {refund.id}"
            
            except stripe.error.InvalidRequestError as e: 
                # 3. ABORT: If refund fails (e.g., charge already refunded, or invalid intent)
                return Response({
                    'detail': 'Cancellation failed. Could not process refund through Stripe.',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # 4. Finalize: Update status and save, regardless of refund attempt outcome
        rental.status = 'cancelled'
        rental.save()
        
        # 5. Return success response with explicit refund status
        return Response({
            'detail': 'Rental successfully cancelled.',
            'rental': self.get_serializer(rental).data,
            'refund_status': refund_status_message
        }, status=status.HTTP_200_OK)
    
    #Extension logic
    #PUT /rentals/{id}/extend/
    @action(detail=True, methods=['put'], url_path='extend', permission_classes=[IsAuthenticated])
    def extend_rental(self, request, pk=None):
        rental = self.get_object()
        new_end_date_str = request.data.get('new_rental_end')

        if not new_end_date_str:
            return Response({'detail': 'New rental end date is required.'}, status=status.HTTP_400_BAD_REQUEST)
        #A. Validation and date conversion
        try:
            new_end_date = datetime.strptime(new_end_date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        except ValueError:
            return Response({'detail': 'Invalid date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SSZ).'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_end_date <= rental.rental_end:
            return Response({'detail': 'New end date must be after the current end date.'}, status=status.HTTP_400_BAD_REQUEST)
        #B. Availability check for the extension period
        if not is_vehicle_available_for_new_dates(rental.vehicle, rental.rental_end, new_end_date, exclude_rental_id=rental.id):
            return Response({'detail': 'Vehicle is already booked during the requested extension period.'}, status=status.HTTP_400_BAD_REQUEST)

        #C. Calculate additional cost for the extension
        if rental_rate_per_day is None:
            return Response({'detail': 'Vehicle rental rate is missing.'}, status=status.HTTP_400_BAD_REQUEST)
        rate_as_float = float(rental_rate_per_day)
        extension_cost = calculate_rental_cost(rental.rental_end, new_end_date, rate_as_float)
        #D. Process payment for the extension via Stripe
        amount_in_cents = int(extension_cost * 100)
        try:
            intent = stripe.PaymentIntent.create(
                amount = amount_in_cents,
                currency = 'usd',
                payment_method_types = ['card'],
                metadata = {'rental_id': rental.id, 'user_id': rental.user.id, 'extension': 'true'}
            )
        except stripe.error.StripeError as e:
            return Response({'detail': f'Stripe payment for extension failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        #E. Update rental with new end date and adjusted total cost
        current_total_cost = rental.total_cost if rental.total_cost is not None else Decimal('0.00')

        # IMPORTANT: Ensure extension_cost is also treated as Decimal for safe addition
        if not isinstance(extension_cost, Decimal):
            extension_cost = Decimal(extension_cost)
    
        rental.total_cost = current_total_cost + extension_cost
        rental.rental_end = new_end_date
        rental.save()

        return Response({
            'detail': 'Rental successfully extended.',
            'extension_cost': extension_cost,
            'new_total_cost': rental.total_cost,
            'new_rental_end': rental.rental_end
        }, status=status.HTTP_200_OK)


class DamageReportViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """Allows aunthenticated users to create new damage reports."""
    queryset = DamageReport.objects.all().order_by('-reported_at')
    serializer_class = DamageReportSerializer
    permission_classes = [IsAuthenticated]

class ReviewViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """Allows authenticated users to submit reviews for completed rentals."""
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]