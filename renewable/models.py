from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class RenewableSource(models.Model):
    SOURCE_TYPES = [
        ('SOLAR', 'Solar Panel'),
        ('WIND', 'Wind Turbine'),
        ('HYDRO', 'Hydroelectric'),
        ('OTHER', 'Other')
    ]
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    capacity = models.FloatField(validators=[MinValueValidator(0)])
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['-created_at']

class RenewableData(models.Model):
    source = models.ForeignKey(RenewableSource, on_delete=models.CASCADE, related_name='data')
    power_generated = models.FloatField(validators=[MinValueValidator(0)])
    efficiency = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.source.name} - {self.power_generated}W"

class CarbonSavings(models.Model):
    date = models.DateField(unique=True)
    renewable_energy_kwh = models.FloatField(validators=[MinValueValidator(0)])
    carbon_saved_kg = models.FloatField(validators=[MinValueValidator(0)])
    cost_saved = models.FloatField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Carbon Savings"
        verbose_name_plural = "Carbon Savings"

    def __str__(self):
        return f"{self.date} - {self.carbon_saved_kg}kg CO2"