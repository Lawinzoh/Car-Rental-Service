from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .models import Rental
from .serializers import RentalSerializer
from users.models import User
from django.shortcuts import get_object_or_404
from vehicles.models import Vehicle
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
import stripe
from .utils import calculate_rental_cost


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

        if rental.status != 'active':
            return Response({'detail': 'This rental is not currently active.'}, status=status.HTTP_400_BAD_REQUEST)

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
        # Note: In a real app, the fronend sends a payment method ID or token to complete the payment
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
        rental.status = 'confirmed'  # Payment successful, booking confirmed
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