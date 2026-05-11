from django.urls import path
from energy import views as energy_views
from analytics import views as analytics_views
from renewable import views as renewable_views
from notifications import views as notification_views

urlpatterns = [
    # LEGACY ENDPOINTS (for backward compatibility with frontend & simulators)
    path('data/', energy_views.get_data, name='data-all-legacy'),
    path('status/', energy_views.get_status, name='status-legacy'),
    path('turn-on/', energy_views.turn_on, name='turn-on-legacy'),
    path('turn-off/', energy_views.turn_off, name='turn-off-legacy'),
    
    # Real-time Data
    path('data/latest/', energy_views.get_latest_data, name='latest-data'),
    path('data/all/', energy_views.get_data, name='get-data'),
    path('data/post/', energy_views.receive_data, name='post-data'),
    
    # Device Control
    path('device/status/', energy_views.get_status, name='device-status'),
    path('device/on/', energy_views.turn_on, name='device-on'),
    path('device/off/', energy_views.turn_off, name='device-off'),
    
    # Predictions
    path('predictions/', energy_views.get_predictions, name='predictions'),
    path('predictions/trigger/', energy_views.trigger_prediction, name='trigger-prediction'),
    
    # Alert
    path('alerts/', energy_views.get_alerts, name='get-alerts'),
    path('alerts/<int:alert_id>/resolve/', energy_views.resolve_alert, name='resolve-alert'),
    
    # Energy Summary
    path('summary/', energy_views.energy_summary, name='summary'),
    
    # Analytics
    path('analytics/daily-trends/', analytics_views.get_daily_trends, name='daily-trends'),
    path('analytics/hourly-trends/', analytics_views.get_hourly_trends, name='hourly-trends'),
    path('analytics/calculate-trends/', analytics_views.calculate_trends, name='calculate-trends'),
    path('analytics/predict/', analytics_views.predict_energy, name='predict-energy'),
    path('analytics/statistics/', analytics_views.get_statistics, name='statistics'),
    
    # Renewable Energy
    path('renewable/add-source/', renewable_views.add_renewable_source, name='add-source'),
    path('renewable/sources/', renewable_views.get_renewable_sources, name='sources'),
    path('renewable/record-data/', renewable_views.record_renewable_data, name='record-data'),
    path('renewable/generation/', renewable_views.get_renewable_generation, name='generation'),
    path('renewable/carbon-savings/', renewable_views.get_carbon_savings, name='carbon-savings'),
    path('renewable/record-carbon/', renewable_views.record_carbon_savings, name='record-carbon'),
    
    # Notifications - ALL ENDPOINTS
    path('notifications/register-contact/', notification_views.register_contact, name='register-contact'),
    path('notifications/create-rule/', notification_views.create_alert_rule, name='create-rule'),
    path('notifications/get-rules/', notification_views.get_alert_rules, name='get-rules'),
    path('notifications/test-email/', notification_views.test_email_alert, name='test-email'),
    path('notifications/test-sms/', notification_views.test_sms_alert, name='test-sms'),
    path('notifications/send-bulk-email/', notification_views.send_bulk_email_alert, name='send-bulk-email'),
]
