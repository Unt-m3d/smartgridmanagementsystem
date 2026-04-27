from rest_framework import serializers
from .models import RenewableSource, RenewableData, CarbonSavings

class RenewableSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenewableSource
        fields = ['id', 'name', 'source_type', 'capacity', 'location', 'is_active', 'created_at']

class RenewableDataSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    
    class Meta:
        model = RenewableData
        fields = ['id', 'source', 'source_name', 'power_generated', 'efficiency', 'timestamp']

class CarbonSavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonSavings
        fields = ['id', 'date', 'renewable_energy_kwh', 'carbon_saved_kg', 'cost_saved', 'created_at']