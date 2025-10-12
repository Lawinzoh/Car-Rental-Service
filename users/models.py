from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email =models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    driver_license_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
