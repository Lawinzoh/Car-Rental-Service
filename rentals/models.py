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
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='active'
    )

    def __str__(self):
        return f"{self.user.name}  - {self.vehicle.make} {self.vehicle.model}({self.rental_start} to {self.rental_end})"