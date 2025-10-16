from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'driver_license_number']
        read_only_fields = ['id', 'driver_license_number'] # Make driver_license_number read-only