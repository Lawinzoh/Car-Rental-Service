from rest_framework import viewsets, status, permissions
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

    # 1. filtering, searching, and ordering
    filterset_class = VehicleFilter # Use django-filters for filtering vehicles
    search_fields = ['make', 'model', 'year']
    ordering_fields = ['year', 'make', 'model', 'rental_rate_per_day']

    #  2. Set permissions
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    # 3. Vehicle Availability Endpoint: GET /vehicles/availability/?rental_start=&rental_end/ [cite: 33]
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
    
    # 4. Vehicle Status Update Endpoint
    # PUT /vehicles/{id}/update_status/
    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        vehicle = self.get_object()

        # Expecting JSON data with real-time stats
        mileage = request.data.get('current_mileage')
        fuel_level = request.data.get('fuel_level')
        location = request.data.get('current_location')

        if mileage is not None:
            vehicle.current_mileage = mileage
        if fuel_level is not None:
            vehicle.fuel_level = fuel_level
        if location is not None:
            vehicle.current_location = location

        vehicle.save()

        #return standard serrializer data for verification
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data, status=status.HTTP_200_OK)