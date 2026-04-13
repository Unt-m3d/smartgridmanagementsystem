from django.db import models
from django.core.validators import MinValueValidator


class DeviceStatus(models.Model):
    """Model to track the on/off status of the main device."""

    device_id = models.CharField(
        max_length=255,
        unique=True,
        default='main_device',
        help_text="Unique identifier for the device"
    )
    status = models.CharField(
        max_length=10,
        choices=[('on', 'ON'), ('off', 'OFF')],
        default='on',
        help_text="Current status of the device"
    )
    timestamp = models.DateTimeField(
        auto_now=True,
        help_text="Last time status was updated"
    )

    class Meta:
        verbose_name = "Device Status"
        verbose_name_plural = "Device Status"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Device {self.device_id}: {self.status.upper()}"


class EnergyData(models.Model):
    """Model to store energy consumption measurements."""

    voltage = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Voltage in Volts"
    )
    current = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Current in Amps"
    )
    power = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Power in Watts"
    )
    device_on = models.BooleanField(
        default=True,
        help_text="Whether the device was on during measurement"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the measurement was recorded"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Energy Data"
        verbose_name_plural = "Energy Data"
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.power}W @ {self.timestamp}"