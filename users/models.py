from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email =models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    driver_license_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username
