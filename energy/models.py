from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
import uuid


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


# ============ NEW MODELS FOR FEATURES ============

class UserProfile(models.Model):
    """Extended user profile with contact preferences."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    enable_sms_alerts = models.BooleanField(default=True)
    enable_email_alerts = models.BooleanField(default=True)
    alert_threshold_power = models.FloatField(default=400)
    alert_threshold_voltage = models.FloatField(default=240)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class EnergyPrediction(models.Model):
    """Store AI predictions for energy usage."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    predicted_power = models.FloatField(help_text="Predicted power consumption in Watts")
    predicted_timestamp = models.DateTimeField(help_text="When this prediction is for")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), ],
        help_text="Confidence level (0-1)"
    )
    model_version = models.CharField(max_length=20, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-predicted_timestamp']
        verbose_name = "Energy Prediction"

    def __str__(self):
        return f"Prediction: {self.predicted_power}W for {self.predicted_timestamp}"


class Alert(models.Model):
    """Store system alerts and anomalies."""
    
    ALERT_TYPES = [
        ('HIGH_VOLTAGE', 'High Voltage'),
        ('LOW_VOLTAGE', 'Low Voltage'),
        ('HIGH_CURRENT', 'High Current'),
        ('HIGH_POWER', 'High Power'),
        ('ANOMALY', 'Anomaly Detected'),
        ('RENEWABLE_EVENT', 'Renewable Energy Event'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RESOLVED', 'Resolved'),
        ('ACKNOWLEDGED', 'Acknowledged'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    sms_sent = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Alert"

    def __str__(self):
        return f"{self.alert_type} - {self.message[:50]}"


class RenewableEnergyData(models.Model):
    """Model to track renewable energy generation."""
    
    RENEWABLE_TYPES = [
        ('SOLAR', 'Solar'),
        ('WIND', 'Wind'),
        ('HYDRO', 'Hydroelectric'),
        ('OTHER', 'Other'),
    ]
    
    energy_type = models.CharField(max_length=10, choices=RENEWABLE_TYPES)
    power_generated = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Power generated in Watts"
    )
    efficiency_percentage = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Generation efficiency (0-100)"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Renewable Energy Data"

    def __str__(self):
        return f"{self.energy_type}: {self.power_generated}W @ {self.timestamp}"


class EnergyTrend(models.Model):
    """Aggregated energy trends for analytics."""
    
    PERIOD_CHOICES = [
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]
    
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    average_power = models.FloatField()
    peak_power = models.FloatField()
    minimum_power = models.FloatField()
    total_energy = models.FloatField(help_text="Total energy in kWh")
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']
        unique_together = ('period', 'timestamp')
        verbose_name = "Energy Trend"

    def __str__(self):
        return f"{self.period} Trend: {self.average_power}W avg"