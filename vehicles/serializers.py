from .models import Vehicle
from rest_framework import serializers


class VehicleSeializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'license_plate', 'rental_rate_per_day', 'availability_status']