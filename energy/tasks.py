from django.core.mail import send_mail
from django.conf import settings
from .models import EnergyData, EnergyPrediction, Alert, UserProfile
from .predictions import predict_energy_usage, detect_anomalies
from celery import shared_task
import logging
from datetime import datetime, timedelta
from twilio.rest import Client

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def predict_future_energy(self):
    """Predict future energy usage"""
    try:
        # Get last 7 days of data
        seven_days_ago = datetime.now() - timedelta(days=7)
        training_data = list(EnergyData.objects.filter(
            timestamp__gte=seven_days_ago
        ).values_list('power', flat=True).order_by('timestamp'))
        
        if len(training_data) < 24:
            logger.warning("Not enough data for prediction")
            return
        
        # Make predictions
        predictions = predict_energy_usage(training_data)
        
        for pred in predictions:
            EnergyPrediction.objects.create(
                predicted_power=pred['power'],
                predicted_timestamp=pred['timestamp'],
                confidence_score=pred['confidence']
            )
        
        logger.info(f"Successfully predicted {len(predictions)} data points")
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        # Retry task with exponential backoff
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def check_energy_anomalies(self):
    """Check for anomalies in recent data"""
    try:
        # Get last 100 data points
        recent_data = list(EnergyData.objects.all().order_by('-timestamp')[:100])
        recent_data.reverse()  # Reverse to chronological order
        
        powers = [d.power for d in recent_data]
        anomaly_indices = detect_anomalies(powers)
        
        if anomaly_indices:
            for idx in anomaly_indices:
                alert = Alert.objects.create(
                    user=UserProfile.objects.first().user if UserProfile.objects.exists() else None,
                    alert_type='ANOMALY',
                    message=f"Anomaly detected: Unusual power pattern at {recent_data[idx].timestamp}"
                )
                send_alert_notifications.delay(alert.id)
        
        logger.info(f"Anomaly detection complete: {len(anomaly_indices)} anomalies found")
    except Exception as e:
        logger.error(f"Anomaly detection error: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_alert_notifications(self, alert_id):
    """Send SMS and email alerts"""
    try:
        alert = Alert.objects.get(id=alert_id)
        if not alert.user:
            return
        
        user = alert.user
        try:
            profile = user.profile
        except:
            logger.warning(f"User {user.username} has no profile")
            return
        
        # Send SMS
        if profile.enable_sms_alerts and profile.phone_number:
            send_sms_alert.delay(
                phone=profile.phone_number,
                message=f"⚠️ {alert.alert_type}: {alert.message}"
            )
            alert.sms_sent = True
        
        # Send Email
        if profile.enable_email_alerts and user.email:
            send_email_alert.delay(
                email=user.email,
                subject=f"Smart Grid Alert: {alert.alert_type}",
                message=alert.message
            )
            alert.email_sent = True
        
        alert.save()
        logger.info(f"Notifications sent for alert {alert_id}")
    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
    except Exception as e:
        logger.error(f"Alert notification error: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_sms_alert(self, phone, message):
    """Send SMS using Twilio"""
    try:
        if not settings.TWILIO_ACCOUNT_SID:
            logger.warning("Twilio not configured")
            return
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        logger.info(f"SMS sent to {phone}")
    except Exception as e:
        logger.error(f"SMS sending failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_email_alert(self, email, subject, message):
    """Send email"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {email}")
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def calculate_energy_trends(self):
    """Calculate energy trends"""
    try:
        from .analytics import calculate_trends
        calculate_trends()
        logger.info("Energy trends calculated")
    except Exception as e:
        logger.error(f"Trend calculation error: {str(e)}")
        raise self.retry(exc=e, countdown=60)