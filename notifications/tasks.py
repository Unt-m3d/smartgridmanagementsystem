import logging
import os
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

try:
    from twilio.rest import Client
except ImportError:
    Client = None

logger = logging.getLogger(__name__)

# Detect if running on Windows
IS_WINDOWS = os.name == 'nt'


#  SEND EMAIL IMMEDIATELY (Works without Celery) - SINGLE OR MULTIPLE RECIPIENTS
def send_email_alert(email, subject, message, html_message=None):
    """
    Send email immediately to single or multiple recipients
    
    Args:
        email: str or list - Single email or list of emails
        subject: str - Email subject
        message: str - Plain text message
        html_message: str - HTML formatted message (optional)
    
    Returns:
        bool - True if successful, False otherwise
    """
    try:
        # Handle single email string or list of emails
        if isinstance(email, str):
            recipient_list = [email.strip()]
        elif isinstance(email, list):
            recipient_list = [e.strip() for e in email if e]
        else:
            logger.error("Email must be string or list")
            return False
        
        # Validate emails
        if not recipient_list:
            logger.error("No valid email addresses provided")
            return False
        
        if not settings.EMAIL_HOST_USER:
            logger.error("EMAIL_HOST_USER not configured in settings")
            return False
        
        # Validate email format (basic check)
        for email_addr in recipient_list:
            if '@' not in email_addr or '.' not in email_addr:
                logger.error(f"Invalid email format: {email_addr}")
                return False
        
        email_icon = "[MAIL]" if IS_WINDOWS else "gmail"
        recipients_str = ", ".join(recipient_list)
        logger.info(f"{email_icon} Sending email to {recipients_str}: {subject}")
        logger.debug(f"Email Backend: {settings.EMAIL_BACKEND}")
        logger.debug(f"Email Host: {settings.EMAIL_HOST}")
        logger.debug(f"Email Port: {settings.EMAIL_PORT}")
        logger.debug(f"From: {settings.DEFAULT_FROM_EMAIL}")
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        
        check_icon = "[OK]" if IS_WINDOWS else "yes"
        logger.info(f"{check_icon} Email sent successfully to {recipients_str}")
        return True
            
    except Exception as exc:
        error_icon = "[ERROR]" if IS_WINDOWS else "no"
        logger.error(f"{error_icon} Error sending email: {str(exc)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


# SEND EMAIL WITH ATTACHMENTS (NEW)
def send_email_with_attachment(email, subject, message, attachment_file=None, html_message=None):
    """
    Send email with optional attachment
    
    Args:
        email: str or list - Single email or list of emails
        subject: str - Email subject
        message: str - Plain text message
        attachment_file: file path - Optional attachment
        html_message: str - HTML formatted message (optional)
    
    Returns:
        bool - True if successful, False otherwise
    """
    try:
        # Handle single email string or list of emails
        if isinstance(email, str):
            recipient_list = [email.strip()]
        elif isinstance(email, list):
            recipient_list = [e.strip() for e in email if e]
        else:
            logger.error("Email must be string or list")
            return False
        
        if not recipient_list:
            logger.error("No valid email addresses provided")
            return False
        
        if not settings.EMAIL_HOST_USER:
            logger.error("EMAIL_HOST_USER not configured in settings")
            return False
        
        email_icon = "[MAIL]" if IS_WINDOWS else "gmail"
        recipients_str = ", ".join(recipient_list)
        logger.info(f"{email_icon} Sending email with attachment to {recipients_str}: {subject}")
        
        # Create email message
        msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        
        # Add HTML content if provided
        if html_message:
            msg.content_subtype = "html"
            msg.body = html_message
        
        # Add attachment if provided
        if attachment_file and os.path.exists(attachment_file):
            msg.attach_file(attachment_file)
            logger.debug(f"Attached file: {attachment_file}")
        
        msg.send(fail_silently=False)
        
        check_icon = "[OK]" if IS_WINDOWS else "yes"
        logger.info(f"{check_icon} Email with attachment sent to {recipients_str}")
        return True
            
    except Exception as exc:
        error_icon = "[ERROR]" if IS_WINDOWS else "no"
        logger.error(f"{error_icon} Error sending email: {str(exc)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


#  SEND SMS IMMEDIATELY
def send_sms_alert(phone, message):
    """Send SMS immediately"""
    try:
        twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
            logger.warning("Twilio not fully configured (missing credentials)")
            return False
        
        if not Client:
            logger.warning("Twilio library not installed")
            return False
        
        if not phone:
            logger.error("Phone number is empty")
            return False
        
        sms_icon = "[SMS]" if IS_WINDOWS else "sms"
        logger.info(f"{sms_icon} Sending SMS to {phone}")
        
        client = Client(twilio_account_sid, twilio_auth_token)
        sms = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone
        )
        
        check_icon = "[OK]" if IS_WINDOWS else "yes"
        logger.info(f"{check_icon} SMS sent successfully to {phone} (SID: {sms.sid})")
        return True
        
    except Exception as exc:
        error_icon = "[ERROR]" if IS_WINDOWS else "no"
        logger.error(f"{error_icon} Error sending SMS to {phone}: {str(exc)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


# ASYNC VERSION (for Celery - optional)
@shared_task(bind=True, max_retries=3)
def send_email_alert_async(self, email, subject, message, html_message=None):
    """Send email asynchronously"""
    try:
        return send_email_alert(email, subject, message, html_message)
    except Exception as exc:
        logger.error(f"Celery task error: {str(exc)}")
        raise self.retry(exc=exc, countdown=5, max_retries=3)


@shared_task(bind=True, max_retries=3)
def send_sms_alert_async(self, phone, message):
    """Send SMS asynchronously"""
    try:
        return send_sms_alert(phone, message)
    except Exception as exc:
        logger.error(f"Celery task error: {str(exc)}")
        raise self.retry(exc=exc, countdown=5, max_retries=3)


@shared_task
def check_energy_alerts():
    """Check energy alerts and send notifications"""
    from energy.models import EnergyData, Alert
    from django.contrib.auth.models import User
    
    try:
        search_icon = "[SEARCH]" if IS_WINDOWS else "serching"
        logger.info(f"{search_icon} Checking energy alerts...")
        
        try:
            latest_data = EnergyData.objects.latest('timestamp')
        except EnergyData.DoesNotExist:
            logger.warning("No energy data found")
            return False
        
        alert_config = getattr(settings, 'ALERT_SETTINGS', {})
        high_voltage = alert_config.get('HIGH_VOLTAGE', 240)
        low_voltage = alert_config.get('LOW_VOLTAGE', 190)
        
        alerts = []
        
        if latest_data.voltage > high_voltage:
            alerts.append({
                'type': 'HIGH_VOLTAGE',
                'message': f"HIGH VOLTAGE ALERT: {latest_data.voltage:.2f}V (Threshold: {high_voltage}V)"
            })
        
        if latest_data.voltage < low_voltage:
            alerts.append({
                'type': 'LOW_VOLTAGE',
                'message': f"LOW VOLTAGE ALERT: {latest_data.voltage:.2f}V (Threshold: {low_voltage}V)"
            })
        
        if alerts:
            try:
                users = User.objects.filter(profile__enable_email_alerts=True)
                user_emails = [user.email for user in users if user.email]
                
                if user_emails:
                    for alert in alerts:
                        # Send to all users at once
                        send_email_alert(
                            email=user_emails,
                            subject=f"ALERT: Smart Grid Alert: {alert['type']}",
                            message=alert['message']
                        )
                    check_icon = "[OK]" if IS_WINDOWS else "yes"
                    logger.info(f"{check_icon} {len(alerts)} alerts sent to {len(user_emails)} users")
                    return True
                else:
                    logger.warning("No users with email alerts enabled")
                    return False
            except Exception as e:
                logger.error(f"Error sending alerts: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return False
        
        return True
        
    except Exception as e:
        error_icon = "[ERROR]" if IS_WINDOWS else "no"
        logger.error(f"{error_icon} Error in check_energy_alerts: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False