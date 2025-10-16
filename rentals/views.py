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
            raise ValueError("A 'user_id' is required for booking.")
        
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