from rest_framework import serializers
from .models import UserContact, AlertRule

class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContact
        fields = ['id', 'user_email', 'user_phone', 'receive_email_alerts', 'receive_sms_alerts']

class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = ['id', 'name', 'alert_type', 'threshold', 'is_active', 'contact']
