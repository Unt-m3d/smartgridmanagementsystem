import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

try:
    from twilio.rest import Client
except ImportError:
    Client = None

logger = logging.getLogger(__name__)


# ✅ SEND EMAIL IMMEDIATELY (Works without Celery)
def send_email_alert(email, subject, message, html_message=None):
    """Send email immediately"""
    try:
        logger.info(f"📧 Sending email to {email}: {subject}")
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"✅ Email sent to {email}")
        return True
            
    except Exception as exc:
        logger.error(f"❌ Error sending email: {str(exc)}")
        return False


# ✅ SEND SMS IMMEDIATELY
def send_sms_alert(phone, message):
    """Send SMS immediately"""
    try:
        twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
            logger.warning("⚠️ Twilio not configured")
            return False
        
        if not Client:
            logger.warning("⚠️ Twilio not installed")
            return False
        
        logger.info(f"📱 Sending SMS to {phone}")
        
        client = Client(twilio_account_sid, twilio_auth_token)
        sms = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone
        )
        
        logger.info(f"✅ SMS sent to {phone}")
        return True
        
    except Exception as exc:
        logger.error(f"❌ Error sending SMS: {str(exc)}")
        return False


# ✅ ASYNC VERSION (for Celery - optional)
@shared_task(bind=True, max_retries=3)
def send_email_alert_async(self, email, subject, message, html_message=None):
    """Send email asynchronously"""
    try:
        return send_email_alert(email, subject, message, html_message)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5, max_retries=3)


@shared_task(bind=True, max_retries=3)
def send_sms_alert_async(self, phone, message):
    """Send SMS asynchronously"""
    try:
        return send_sms_alert(phone, message)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5, max_retries=3)


@shared_task
def check_energy_alerts():
    """Check energy alerts and send notifications"""
    from energy.models import EnergyData, Alert
    from django.contrib.auth.models import User
    
    try:
        logger.info("🔍 Checking energy alerts...")
        
        try:
            latest_data = EnergyData.objects.latest('timestamp')
        except EnergyData.DoesNotExist:
            return False
        
        alert_config = getattr(settings, 'ALERT_SETTINGS', {})
        high_voltage = alert_config.get('HIGH_VOLTAGE', 240)
        low_voltage = alert_config.get('LOW_VOLTAGE', 190)
        
        alerts = []
        
        if latest_data.voltage > high_voltage:
            alerts.append({
                'type': 'HIGH_VOLTAGE',
                'message': f"⚠️ HIGH VOLTAGE: {latest_data.voltage:.2f}V"
            })
        
        if latest_data.voltage < low_voltage:
            alerts.append({
                'type': 'LOW_VOLTAGE',
                'message': f"⚠️ LOW VOLTAGE: {latest_data.voltage:.2f}V"
            })
        
        if alerts:
            try:
                users = User.objects.filter(profile__enable_email_alerts=True)
                for user in users:
                    for alert in alerts:
                        send_email_alert(
                            email=user.email,
                            subject=f"Smart Grid Alert: {alert['type']}",
                            message=alert['message']
                        )
                logger.info(f"✅ {len(alerts)} alerts sent")
                return True
            except Exception as e:
                logger.error(f"Error sending alerts: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in check_energy_alerts: {str(e)}")
        return False