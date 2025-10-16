from rest_framework import viewsets, status
from .models import Vehicle
from .serializers import VehicleSeializer
from .filters import VehicleFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rentals.models import Rental
from rest_framework.decorators import action
from rest_framework.response import Response


class VehicleListView(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all() # Retrieve all vehicles(READ)
    serializer_class = VehicleSeializer # Use the VehicleSerializer for serialization/deserialization

    #filtering, searching, and ordering
    filterset_class = VehicleFilter # Use django-filters for filtering vehicles
    search_fields = ['make', 'model', 'year'] #Fields to allow text searching
    ordering_fields = ['year', 'make', 'model', 'rental_rate_per_day'] #Fields to allow ordering/sorting

    # Set permissions
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser] # Only admins can create, update, or delete vehicles
        else:
            permission_classes = [IsAuthenticatedOrReadOnly] # Everyone can view vehicles
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        rental_start = request.query_params.get('rental_start')
        rental_end = request.query_params.get('rental_end')

        if not rental_start or not rental_end:
            return Response({'detail': 'Both rental_start and rental_end query parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Find the IDs of vehicles that are NOT available (i.e., have overlapping active rentals)
        unavailable_vehicle_ids = Rental.objects.filter(
            status='active',
            rental_start__lt=rental_end,
            rental_end__gt=rental_start
        ).values_list('vehicle_id', flat=True).distinct()

        # 2. Filter the entire vehicle list to exclude unavailable IDs
        available_vehicles = Vehicle.objects.exclude(id__in=unavailable_vehicle_ids)
        
        # Note: If you have a vehicle field 'availability_status', you can filter by that too:
        # available_vehicles = available_vehicles.filter(availability_status=True)

        serializer = self.get_serializer(available_vehicles, many=True)
        return Response(serializer.data)
