from rest_framework import serializers
from .models import EnergyData, EnergyPrediction, Alert, RenewableEnergyData, UserProfile


class EnergyDataSerializer(serializers.ModelSerializer):
    """Serializer for EnergyData model"""

    class Meta:
        model = EnergyData
        fields = '__all__'
        read_only_fields = ['timestamp']


class EnergyPredictionSerializer(serializers.ModelSerializer):
    """Serializer for EnergyPrediction model"""

    class Meta:
        model = EnergyPrediction
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""

    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['created_at']


class RenewableEnergySerializer(serializers.ModelSerializer):
    """Serializer for RenewableEnergyData model"""

    class Meta:
        model = RenewableEnergyData
        fields = '__all__'
        read_only_fields = ['timestamp']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile"""

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'enable_sms_alerts', 'enable_email_alerts', 'alert_threshold_power', 'alert_threshold_voltage']