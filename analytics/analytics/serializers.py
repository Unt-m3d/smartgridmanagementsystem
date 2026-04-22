from rest_framework import serializers
from .models import EnergyTrend, EnergyPrediction


class EnergyTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyTrend
        fields = ['id', 'date', 'avg_power', 'peak_power', 'min_power', 'total_energy', 'peak_hour', 'created_at']


class EnergyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyPrediction
        fields = ['id', 'prediction_date', 'predicted_power', 'confidence', 'created_at']