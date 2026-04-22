from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class RenewableSource(models.Model):
    """Model for renewable energy sources."""

    SOURCE_TYPES = [
        ('solar', 'Solar Panel'),
        ('wind', 'Wind Turbine'),
        ('hydro', 'Hydroelectric'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    capacity = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Capacity in kW"
    )
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class RenewableData(models.Model):
    """Model to store renewable energy generation data."""

    source = models.ForeignKey(RenewableSource, on_delete=models.CASCADE)
    power_generated = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Power generated in Watts"
    )
    efficiency = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Efficiency percentage",
        default=0
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.source.name} - {self.power_generated}W"


class CarbonSavings(models.Model):
    """Track carbon footprint reduction."""

    date = models.DateField(unique=True)
    renewable_energy_kwh = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Energy from renewable sources in kWh"
    )
    carbon_saved_kg = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="CO2 saved in kg"
    )
    cost_saved = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Cost saved in currency units"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.carbon_saved_kg}kg CO2 saved"