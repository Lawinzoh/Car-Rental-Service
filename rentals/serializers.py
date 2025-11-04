from rest_framework import serializers
from .models import Rental, DamageReport, Review
from vehicles.models import Vehicle
from django.utils import timezone
from users.models import User
from django.db import IntegrityError

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
    
class DamageReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamageReport
        fields = ['id', 'rental', 'reporter', 'photo_url', 'description', 'reported_at', 'is_resolved']
        read_only_fields = ['reporter','reported_at', 'is_resolved']

        def validate_rental(self, value):
            # Ensure the rental exists and is associated with the reporter
            if not Rental.objects.filter(pk=value.pk).exists():
                raise serializers.ValidationError('Invalid rental ID.')
            return value
        def create(self, validated_data):
            user = self.context['request'].user

            if user and user.is_authenticated:
                validated_data['reporter'] = user
            else:
                raise serializers.ValidationError({'reporter': 'Authentication is required to report damage.'})
            return super().create(validated_data)
        
class ReviewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='rental_id', read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'rental', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_rental(self, value):
            #Only allow reviews on completed rentals
        if value.status != 'completed':
            raise serializers.ValidationError('Cannot review an active or cancelled rental.')
        return value
    #prevent multiple reviews per rental
    def create(self, validated_data):
        try:
        # Attempt to create the object
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'rental':'This rental has already been reviewed.'})
        