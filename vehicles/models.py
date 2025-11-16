from django.db import models
from django.conf import settings

class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_vehicles', 
        null=True, 
        blank=True,
        help_text='User who owns/manages this vehicle'
    )
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    availability_status = models.BooleanField(default=True)
    rental_rate_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    current_mileage = models.IntegerField(null=True, blank=True)
    fuel_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    current_location = models.DecimalField(max_digits=255, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"
