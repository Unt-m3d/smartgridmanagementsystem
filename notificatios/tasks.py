import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import os

try:
    from twilio.rest import Client
except ImportError:
    Client = None

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    sendgrid = None

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_alert(self, email, subject, message, html_message=None):
    """
    Send email alert using SendGrid or Django's email backend.
    Falls back to Django email if SendGrid is not configured.
    """
    try:
        logger.info(f"Attempting to send email to {email}: {subject}")
        
        sendgrid_api_key = settings.SENDGRID_API_KEY
        
        if sendgrid_api_key and sendgrid:
            # Use SendGrid
            sg = sendgrid.SendGridAPIClient(sendgrid_api_key)
            
            from_email = Email(settings.DEFAULT_FROM_EMAIL)
            to_email = To(email)
            subject_line = subject
            plain_text = Content("text/plain", message)
            
            if html_message:
                html_content = Content("text/html", html_message)
                mail = Mail(from_email, to_email, subject_line, plain_text, html_content)
            else:
                mail = Mail(from_email, to_email, subject_line, plain_text)
            
            response = sg.client.mail.send.post(request_body=mail.get())
            logger.info(f"SendGrid response: {response.status_code}")
            return True
        else:
            # Fallback: Use Django's email backend
            logger.info("Using Django email backend (configure SendGrid for production)")
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent successfully to {email}")
            return True
            
    except Exception as exc:
        logger.error(f"Error sending email to {email}: {str(exc)}")
        # Retry after 5 seconds
        raise self.retry(exc=exc, countdown=5)


@shared_task(bind=True, max_retries=3)
def send_sms_alert(self, phone, message):
    """
    Send SMS alert using Twilio API.
    """
    try:
        twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        twilio_auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
            logger.warning("Twilio credentials not configured")
            return False
        
        if not Client:
            logger.warning("Twilio library not installed")
            return False
        
        logger.info(f"Attempting to send SMS to {phone}")
        
        client = Client(twilio_account_sid, twilio_auth_token)
        sms = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone
        )
        
        logger.info(f"SMS sent successfully. SID: {sms.sid}")
        return True
        
    except Exception as exc:
        logger.error(f"Error sending SMS to {phone}: {str(exc)}")
        # Retry after 5 seconds
        raise self.retry(exc=exc, countdown=5)


@shared_task
def check_energy_alerts():
    """
    Periodic task to check energy data against alert thresholds.
    This should be called by Celery Beat scheduler.
    """
    from energy.models import EnergyData
    from .models import AlertRule, UserContact
    from django.utils import timezone
    
    try:
        logger.info("Checking energy alerts...")
        
        # Get latest energy data
        latest_data = EnergyData.objects.latest('timestamp')
        
        # Get all active alert rules
        alert_rules = AlertRule.objects.filter(is_active=True)
        
        for rule in alert_rules:
            contact = rule.contact
            should_alert = False
            message = ""
            
            # Check voltage alerts
            if rule.alert_type == 'voltage_high' and latest_data.voltage > rule.threshold:
                should_alert = True
                message = f"⚠️ HIGH VOLTAGE ALERT: {latest_data.voltage}V exceeds threshold {rule.threshold}V"
            
            elif rule.alert_type == 'voltage_low' and latest_data.voltage < rule.threshold:
                should_alert = True
                message = f"⚠️ LOW VOLTAGE ALERT: {latest_data.voltage}V below threshold {rule.threshold}V"
            
            elif rule.alert_type == 'power_high' and latest_data.power > rule.threshold:
                should_alert = True
                message = f"⚠️ HIGH POWER ALERT: {latest_data.power}W exceeds threshold {rule.threshold}W"
            
            # Send alerts if threshold crossed
            if should_alert:
                if contact.receive_email_alerts:
                    send_email_alert.delay(
                        email=contact.user_email,
                        subject=f"Smart Grid Alert: {rule.alert_type}",
                        message=message,
                        html_message=f"<h2>{message}</h2><p>Timestamp: {latest_data.timestamp}</p>"
                    )
                
                if contact.receive_sms_alerts and contact.user_phone:
                    send_sms_alert.delay(
                        phone=contact.user_phone,
                        message=message
                    )
                
                logger.info(f"Alert sent for rule: {rule.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in check_energy_alerts: {str(e)}")
        return False