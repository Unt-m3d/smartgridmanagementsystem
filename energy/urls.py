from django.urls import path
from . import views

urlpatterns = [
    # Existing endpoints
    path('data/', views.receive_data, name='receive_data'),
    path('data/all/', views.get_data, name='get_data'),
    path('device/on/', views.turn_on, name='turn_on'),
    path('device/off/', views.turn_off, name='turn_off'),
    path('device/status/', views.get_status, name='get_status'),
    
    # NEW: Latest energy data endpoint (for real-time dashboard)
    path('latest/', views.get_latest_data, name='latest'),
    
    # New endpoints for features
    path('predictions/', views.get_predictions, name='get_predictions'),
    path('predictions/trigger/', views.trigger_prediction, name='trigger_prediction'),
    path('alerts/', views.get_alerts, name='get_alerts'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('renewable/', views.renewable_energy, name='renewable_energy'),
    path('summary/', views.energy_summary, name='energy_summary'),
]