from django.contrib import admin
from .models import EnergyData, DeviceStatus


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