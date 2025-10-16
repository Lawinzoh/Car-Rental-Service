from rest_framework import serializers
from .models import Rental
from vehicles.models import Vehicle
from django.utils import timezone
from users.models import User

class RentalSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(source='vehicle', queryset=Vehicle.objects.all())

    class Meta:
        model = Rental
        fields = ['id', 'user_id', 'vehicle_id', 'rental_start', 'rental_end', 'status']
        read_only_fields = ['status'] # Status is managed by the system

    def validate(self, data):
        rental_start = data['rental_start']
        rental_end = data['rental_end']
        vehicle = data['vehicle']

        #check that rental_end is after rental_start
        if rental_start >= rental_end:
            raise serializers.ValidationError('Rental end date must be after the start date.')
        
        #check for future bookings(prevent backdated rentals)
        if rental_start < timezone.now():
            raise serializers.ValidationError('Rental start date cannot be in the past.')
        
        # Check for overlapping rentals for the same vehicle
        overlapping_rentals = Rental.objects.filter(
            vehicle=vehicle,
            status__in=['active'], # Only check against active rentals
            rental_start__lt=rental_end,
            rental_end__gt=rental_start,
        ).exists()
        if overlapping_rentals:
            raise serializers.ValidationError(f'Vehicle {vehicle.license_plate} is already booked during this period.')
        return data