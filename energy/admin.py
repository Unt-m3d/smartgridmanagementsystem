from django.contrib import admin
from .models import EnergyData, DeviceStatus, EnergyPrediction, Alert, RenewableEnergyData, UserProfile, EnergyTrend


@admin.register(EnergyData)
class EnergyDataAdmin(admin.ModelAdmin):
    """Admin interface for EnergyData model"""
    list_display = ['power', 'voltage', 'current', 'device_on', 'timestamp']
    list_filter = ['timestamp', 'device_on']
    search_fields = ['power']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(DeviceStatus)
class DeviceStatusAdmin(admin.ModelAdmin):
    """Admin interface for DeviceStatus model"""
    list_display = ['device_id', 'status', 'timestamp']
    list_filter = ['status']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(EnergyPrediction)
class EnergyPredictionAdmin(admin.ModelAdmin):
    """Admin interface for EnergyPrediction model"""
    list_display = ['predicted_power', 'predicted_timestamp', 'confidence_score', 'created_at']
    list_filter = ['predicted_timestamp', 'created_at']
    search_fields = ['predicted_power']
    readonly_fields = ['id', 'created_at']
    ordering = ['-predicted_timestamp']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin interface for Alert model"""
    list_display = ['user', 'alert_type', 'status', 'created_at']
    list_filter = ['alert_type', 'status', 'created_at']
    search_fields = ['message', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(RenewableEnergyData)
class RenewableEnergyDataAdmin(admin.ModelAdmin):
    """Admin interface for RenewableEnergyData model"""
    list_display = ['energy_type', 'power_generated', 'efficiency_percentage', 'timestamp']
    list_filter = ['energy_type', 'timestamp']
    search_fields = ['power_generated']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""
    list_display = ['user', 'phone_number', 'enable_sms_alerts', 'enable_email_alerts', 'created_at']
    list_filter = ['enable_sms_alerts', 'enable_email_alerts', 'created_at']
    search_fields = ['user__username', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(EnergyTrend)
class EnergyTrendAdmin(admin.ModelAdmin):
    """Admin interface for EnergyTrend model"""
    list_display = ['period', 'average_power', 'peak_power', 'total_energy', 'timestamp']
    list_filter = ['period', 'timestamp']
    search_fields = ['period']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']