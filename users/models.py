from django.db import models
from django.contrib.auth.models import AbstractUser
from django_tenants.models import TenantMixin, DomainMixin

class User(AbstractUser):
    email =models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    driver_license_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username

class Client(TenantMixin):
    """reps a single car rental company (tenant)."""
    name = models.CharField(max_length=100)
    paid_until = models.DateField(null=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True

    def __str__(self):
        return self.name
    
# domain model for the tenant links a tenant(client) to a specific domain/subdomain
class Domain(DomainMixin):
    """links a tenant to a specific hostname for routing."""
    pass