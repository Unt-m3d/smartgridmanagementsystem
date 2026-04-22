from django.db import models


class EnergyTrend(models.Model):
    """Model to store calculated energy trends."""

    date = models.DateField(unique=True)
    avg_power = models.FloatField()
    peak_power = models.FloatField()
    min_power = models.FloatField()
    total_energy = models.FloatField()  # kWh
    peak_hour = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - Avg: {self.avg_power}W"


class EnergyPrediction(models.Model):
    """Model to store AI predictions."""

    prediction_date = models.DateField()
    predicted_power = models.FloatField()
    confidence = models.FloatField()  # 0-1
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prediction_date']

    def __str__(self):
        return f"{self.prediction_date} - {self.predicted_power}W (Confidence: {self.confidence})"