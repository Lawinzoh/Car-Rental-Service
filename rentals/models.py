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
        ('active', 'Active (Unpaid/Pending)'),
        ('confirmed', 'Confirmed (Paid)'),
        ('completed', 'Completed (Returned)'),
        ('cancelled', 'Cancelled')
    ], default='active'
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Total cost of the rental
    payment_intent_id = models.CharField(max_length=50, null=True, blank=True, unique=True, help_text="Stripe Payment Intent ID") 

    def __str__(self):
        return f"{self.user.name}  - {self.vehicle.make} {self.vehicle.model}({self.rental_start} to {self.rental_end})"
    
# Damage Report
class DamageReport(models.Model):
    id = models.AutoField(primary_key=True)
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, db_column='rental_id', related_name='damage_reports')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='reporter_id', related_name='damage_reporters', null=True, blank=True)
    photo_url = models.URLField(max_length=200, null=True, blank=True)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)   
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Damage Report for Rental {self.rental.id} by {self.reporter.name if self.reporter else 'Unknown'}"