from rest_framework import serializers
from .models import EnergyData


class EnergyDataSerializer(serializers.ModelSerializer):
    """Serializer for EnergyData model with all fields."""

    class Meta:
        model = EnergyData
        fields = '__all__'
        read_only_fields = ['timestamp']