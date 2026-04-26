import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime

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
    SEND EMAIL ALERTS
    Supports: Gmail (SMTP) or SendGrid
    """
    try:
        logger.info(f"Sending email to {email}: {subject}")
        
        sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        
        # Try SendGrid first if API key exists
        if sendgrid_api_key and sendgrid:
            try:
                sg = sendgrid.SendGridAPIClient(sendgrid_api_key)
                from_email = Email(getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@smartgrid.com'))
                to_email = To(email)
                subject_line = subject
                plain_text = Content("text/plain", message)
                
                if html_message:
                    html_content = Content("text/html", html_message)
                    mail = Mail(from_email, to_email, subject_line, plain_text, html_content)
                else:
                    mail = Mail(from_email, to_email, subject_line, plain_text)
                
                response = sg.client.mail.send.post(request_body=mail.get())
                logger.info(f"Email sent via SendGrid to {email} (Status: {response.status_code})")
                return True
            except Exception as sg_error:
                logger.warning(f"SendGrid failed: {str(sg_error)}. Trying Gmail...")
        
        # Fallback to Gmail/Django email backend
        logger.info(f"Using Gmail/Django email backend for {email}")
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@smartgrid.com'),
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email successfully sent to {email}")
        return True
            
    except Exception as exc:
        logger.error(f"Error sending email to {email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=5, max_retries=3)


@shared_task(bind=True, max_retries=3)
def send_sms_alert(self, phone, message):
    """
    SEND SMS ALERTS via Twilio
    Requires: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env
    """
    try:
        twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
            logger.warning("Twilio not configured. SMS skipped. Add credentials to .env")
            return False
        
        if not Client:
            logger.warning("Twilio library not installed. Run: pip install twilio")
            return False
        
        logger.info(f"Sending SMS to {phone}...")
        
        client = Client(twilio_account_sid, twilio_auth_token)
        sms = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone
        )
        
        logger.info(f"SMS sent to {phone} (SID: {sms.sid})")
        return True
        
    except Exception as exc:
        logger.error(f"Error sending SMS to {phone}: {str(exc)}")
        raise self.retry(exc=exc, countdown=5, max_retries=3)


@shared_task
def check_energy_alerts():
    """
     PERIODIC ALERT CHECK
    Monitors energy levels and sends alerts if thresholds exceeded
    Call this from Celery Beat scheduler every 60 seconds
    """
    from energy.models import EnergyData, Alert, UserProfile
    from django.contrib.auth.models import User
    from django.conf import settings
    
    try:
        logger.info("🔍 Checking energy alerts...")
        
        try:
            latest_data = EnergyData.objects.latest('timestamp')
        except EnergyData.DoesNotExist:
            logger.info("No energy data available for alert check")
            return False
        
        alert_config = getattr(settings, 'ALERT_SETTINGS', {})
        high_voltage_threshold = alert_config.get('HIGH_VOLTAGE', 240)
        low_voltage_threshold = alert_config.get('LOW_VOLTAGE', 190)
        high_power_threshold = alert_config.get('HIGH_POWER', 400)
        high_current_threshold = alert_config.get('HIGH_CURRENT', 2.0)
        
        alerts_triggered = []
        
        # Check High Voltage
        if latest_data.voltage > high_voltage_threshold:
            alerts_triggered.append({
                'type': 'HIGH_VOLTAGE',
                'message': f"HIGH VOLTAGE ALERT: {latest_data.voltage:.2f}V exceeds {high_voltage_threshold}V",
                'severity': 'HIGH'
            })
        
        # Check Low Voltage
        if latest_data.voltage < low_voltage_threshold:
            alerts_triggered.append({
                'type': 'LOW_VOLTAGE',
                'message': f"LOW VOLTAGE ALERT: {latest_data.voltage:.2f}V below {low_voltage_threshold}V",
                'severity': 'HIGH'
            })
        
        # Check High Power
        if latest_data.power > high_power_threshold:
            alerts_triggered.append({
                'type': 'HIGH_POWER',
                'message': f"HIGH POWER ALERT: {latest_data.power:.2f}W exceeds {high_power_threshold}W",
                'severity': 'MEDIUM'
            })
        
        # Check High Current
        if latest_data.current > high_current_threshold:
            alerts_triggered.append({
                'type': 'HIGH_CURRENT',
                'message': f"HIGH CURRENT ALERT: {latest_data.current:.2f}A exceeds {high_current_threshold}A",
                'severity': 'MEDIUM'
            })
        
        # Send alerts to all users with email enabled
        if alerts_triggered:
            users = User.objects.filter(profile__enable_email_alerts=True)
            
            for alert_info in alerts_triggered:
                for user in users:
                    try:
                        profile = user.profile
                        
                        # Create alert record
                        alert_obj = Alert.objects.create(
                            user=user,
                            alert_type=alert_info['type'],
                            message=alert_info['message'],
                            status='ACTIVE'
                        )
                        
                        # Send Email
                        if profile.enable_email_alerts and user.email:
                            send_email_alert.delay(
                                email=user.email,
                                subject=f"Smart Grid Alert: {alert_info['type']}",
                                message=alert_info['message'],
                                html_message=f"""
                                <html>
                                <body style="font-family: Arial, sans-serif;">
                                    <h2 style="color: #ef4444;">{alert_info['message']}</h2>
                                    <p><strong>Severity:</strong> {alert_info['severity']}</p>
                                    <p><strong>Voltage:</strong> {latest_data.voltage:.2f}V</p>
                                    <p><strong>Power:</strong> {latest_data.power:.2f}W</p>
                                    <p><strong>Current:</strong> {latest_data.current:.2f}A</p>
                                    <p><strong>Time:</strong> {latest_data.timestamp}</p>
                                    <hr>
                                    <p>Check your dashboard for more details.</p>
                                </body>
                                </html>
                                """
                            )
                            alert_obj.email_sent = True
                            alert_obj.save()
                            logger.info(f"Alert email sent to {user.email}")
                        
                        # Send SMS
                        if profile.enable_sms_alerts and profile.phone_number:
                            send_sms_alert.delay(
                                phone=profile.phone_number,
                                message=f"{alert_info['message']}"
                            )
                            alert_obj.sms_sent = True
                            alert_obj.save()
                            logger.info(f"Alert SMS sent to {profile.phone_number}")
                    
                    except Exception as user_error:
                        logger.error(f"Error sending alert to user {user.id}: {str(user_error)}")
                        continue
            
            logger.info(f"{len(alerts_triggered)} alerts triggered and sent")
            return True
        else:
            logger.debug("✓ All energy readings within safe limits")
            return True
        
    except Exception as e:
        logger.error(f"Error in check_energy_alerts: {str(e)}")
        return False


@shared_task
def send_test_alert(email, phone=None):
    """
    ✅ TEST ALERT - For debugging
    """
    logger.info("Sending test alert...")
    
    send_email_alert.delay(
        email=email,
        subject="Smart Grid - Test Email Alert",
        message="This is a test email alert. Your email configuration is working!",
        html_message="""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #10b981;">Test Email Alert</h2>
            <p>This is a test email from your Smart Grid Management System.</p>
            <p><strong>Time:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>Your email configuration is working correctly!</p>
        </body>
        </html>
        """
    )
    
    if phone:
        send_sms_alert.delay(
            phone=phone,
            message="Smart Grid Test SMS: Your SMS configuration is working!"
        )
    
    return {"status": "Test alert sent"}