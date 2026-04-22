from rest_framework import serializers
from .models import RenewableSource, RenewableData, CarbonSavings

class RenewableSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenewableSource
        fields = ['id', 'name', 'source_type', 'capacity', 'location', 'is_active']

class RenewableDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenewableData
        fields = ['id', 'source', 'power_generated', 'efficiency', 'timestamp']

class CarbonSavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonSavings
        fields = ['id', 'date', 'renewable_energy_kwh', 'carbon_saved_kg', 'cost_saved']
