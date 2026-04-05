from django.db import models
from django.core.validators import MinValueValidator

class DeviceStatus(models.Model):
    device_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

class Energy(models.Model):
    voltage = models.FloatField(validators=[MinValueValidator(0)])
    current = models.FloatField(validators=[MinValueValidator(0)])
    power = models.FloatField(validators=[MinValueValidator(0)])
    # Other fields can be added here
