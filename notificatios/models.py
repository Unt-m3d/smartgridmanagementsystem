from django.db import models


class UserContact(models.Model):
    """Store user contact information for alerts."""

    user_email = models.EmailField(unique=True)
    user_phone = models.CharField(max_length=20, blank=True, null=True)
    receive_email_alerts = models.BooleanField(default=True)
    receive_sms_alerts = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_email


class AlertRule(models.Model):
    """Define alert rules."""

    name = models.CharField(max_length=100)
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ('voltage_high', 'High Voltage'),
            ('voltage_low', 'Low Voltage'),
            ('power_high', 'High Power'),
        ]
    )
    threshold = models.FloatField()
    is_active = models.BooleanField(default=True)
    contact = models.ForeignKey(UserContact, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.threshold}"