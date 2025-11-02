from django.db import models
from users.models import User
from vehicles.models import Vehicle

class Rental(models.Model):
    id = models.AutoField(primary_key=True)
    user =models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='rentals')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, db_column='vehicle_id', related_name='rentals')
    rental_start = models.DateTimeField()
    rental_end = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active (Unpaid/Pending)'), # Rental is active but not yet paid
        ('confirmed', 'Confirmed (Paid)'), # Rental is confirmed and paid
        ('completed', 'Completed (Returned)'),
        ('cancelled', 'Cancelled')
    ], default='active'
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Total cost of the rental
    payment_intent_id = models.CharField(max_length=50, null=True, blank=True, unique=True, help_text="Stripe Payment Intent ID") 

    def __str__(self):
        return f"{self.user.name}  - {self.vehicle.make} {self.vehicle.model}({self.rental_start} to {self.rental_end})"