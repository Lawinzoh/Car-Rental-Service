from rest_framework import viewsets
from .models import Vehicle
from .serializers import VehicleSeializer

class VehicleListView(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all() # Retrieve all vehicles(READ)
    serializer_class = VehicleSeializer # Use the VehicleSerializer for serialization/deserialization
     # Authentication will be added in Week 4 [cite: 50]
     # permission_classes = [IsAuthenticatedOrReadOnly] 
    
