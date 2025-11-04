from .models import Vehicle
from rest_framework import serializers
from rentals.models import Rental, Review
from django.db.models import Avg

class VehicleSeializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'license_plate', 'rental_rate_per_day', 'availability_status', 'current_mileage', 'fuel_level', 'current_location', 'average_rating']

    def get_average_rating(self, obj):
        #get all completed rentals for this vehicle
        rental_ids = Rental.objects.filter(vehicle=obj, status='completed').values_list('pk', flat=True)
        #calculate average rating from reviews linked to these rentals
        avg_rating = Review.objects.filter(rental__in=rental_ids).aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 2) if avg_rating is not None else 0.0