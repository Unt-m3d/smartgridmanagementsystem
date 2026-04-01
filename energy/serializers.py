from rest_framework import serializers
from .models import EnergyData
class EnergyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyData
        fields = '__all__'
    
    
