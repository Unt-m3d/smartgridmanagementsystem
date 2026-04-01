from django.db import models

class EnergyData(models.Model):
    voltage = models.FloatField()
    current = models.FloatField()
    power = models.FloatField()
    device_on = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.power} W"    