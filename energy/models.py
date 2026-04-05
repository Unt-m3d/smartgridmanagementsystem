from django.db import models
from django.core.validators import MinValueValidator

class DeviceStatus(models.Model):
    device_id = models.CharField(max_length=255, unique=True, default='main_device')
    status = models.CharField(max_length=10, choices=[('on', 'ON'), ('off', 'OFF')], default='on')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device Status"
        verbose_name_plural = "Device Status"

    def __str__(self):
        return f"Device: {self.status.upper()}"


class EnergyData(models.Model):
    voltage = models.FloatField(validators=[MinValueValidator(0)], help_text="Voltage in Volts")
    current = models.FloatField(validators=[MinValueValidator(0)], help_text="Current in Amps")
    power = models.FloatField(validators=[MinValueValidator(0)], help_text="Power in Watts")
    device_on = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Energy Data"
        verbose_name_plural = "Energy Data"

    def __str__(self):
        return f"{self.power}W @ {self.timestamp}"