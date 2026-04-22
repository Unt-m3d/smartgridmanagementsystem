from django.urls import path
from . import views

urlpatterns = [
    path('register-contact/', views.register_contact, name='register-contact'),
    path('create-rule/', views.create_alert_rule, name='create-rule'),
    path('get-rules/', views.get_alert_rules, name='get-rules'),
    path('test-email/', views.test_email_alert, name='test-email'),
    path('test-sms/', views.test_sms_alert, name='test-sms'),
    path('trigger-check/', views.trigger_alert_check, name='trigger-check'),
]