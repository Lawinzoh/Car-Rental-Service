from rest_framework import serializers
from .models import User, Client, Domain

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'driver_license_number']
        read_only_fields = ['id', 'driver_license_number'] # Make driver_license_number read-only


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'domain', 'tenant', 'is_primary']


class ClientSerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True, read_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'schema_name', 'name', 'paid_until', 'on_trial', 'created_on', 'domains']
        read_only_fields = ['id', 'created_on']
    
    def create(self, validated_data):
        """Create a new client with auto_create_schema enabled"""
        client = Client.objects.create(**validated_data)
        return client