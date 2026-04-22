from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from .models import UserContact, AlertRule
from energy.models import EnergyData, AlertHistory
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email_alert(user_email, subject, message):
    """Send email alert"""
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=False,
        )
        
        AlertHistory.objects.create(
            alert_type='email',
            message=message,
            sent_via='email',
            recipient=user_email,
            status='sent'
        )
        logger.info(f"Email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        AlertHistory.objects.create(
            alert_type='email',
            message=message,
            sent_via='email',
            recipient=user_email,
            status='failed'
        )
        return False


@shared_task
def send_sms_alert(phone_number, message):
    """Send SMS alert via Twilio"""
    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio credentials not configured")
            return False
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_obj = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        AlertHistory.objects.create(
            alert_type='sms',
            message=message,
            sent_via='sms',
            recipient=phone_number,
            status='sent'
        )
        logger.info(f"SMS sent to {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        AlertHistory.objects.create(
            alert_type='sms',
            message=message,
            sent_via='sms',
            recipient=phone_number,
            status='failed'
        )
        return False


@shared_task
def check_alerts():
    """Check energy data and send alerts if thresholds are exceeded"""
    try:
        latest_data = EnergyData.objects.latest('timestamp')
        
        alert_rules = AlertRule.objects.filter(is_active=True)
        
        for rule in alert_rules:
            contact = rule.contact
            should_alert = False
            message = ""
            
            if rule.alert_type == 'voltage_high' and latest_data.voltage > rule.threshold:
                should_alert = True
                message = f"⚠️ HIGH VOLTAGE ALERT: {latest_data.voltage}V (Threshold: {rule.threshold}V)"
            
            elif rule.alert_type == 'voltage_low' and latest_data.voltage < rule.threshold:
                should_alert = True
                message = f"⚠️ LOW VOLTAGE ALERT: {latest_data.voltage}V (Threshold: {rule.threshold}V)"
            
            elif rule.alert_type == 'power_high' and latest_data.power > rule.threshold:
                should_alert = True
                message = f"⚠️ HIGH POWER ALERT: {latest_data.power}W (Threshold: {rule.threshold}W)"
            
            if should_alert:
                if contact.receive_email_alerts:
                    send_email_alert.delay(
                        contact.user_email,
                        f"Smart Grid Alert: {rule.name}",
                        message
                    )
                
                if contact.receive_sms_alerts and contact.user_phone:
                    send_sms_alert.delay(contact.user_phone, message)
        
        return True
    except Exception as e:
        logger.error(f"Error checking alerts: {str(e)}")
        return False


@shared_task
def send_weekly_report(user_email):
    """Send weekly energy report"""
    try:
        from analytics.models import EnergyTrend
        from django.db.models import Avg, Max
        
        week_ago = timezone.now().date() - timezone.timedelta(days=7)
        trends = EnergyTrend.objects.filter(date__gte=week_ago)
        
        if not trends.exists():
            return False
        
        avg_power = trends.aggregate(Avg('avg_power'))['avg_power__avg'] or 0
        peak_power = trends.aggregate(Max('peak_power'))['peak_power__max'] or 0
        
        report = f"""
        📊 Weekly Energy Report
        
        Period: Last 7 Days
        Average Power: {avg_power:.2f}W
        Peak Power: {peak_power:.2f}W
        Days Analyzed: {trends.count()}
        
        Keep monitoring your energy consumption!
        """
        
        send_email_alert.delay(user_email, "Weekly Energy Report", report)
        return True
    except Exception as e:
        logger.error(f"Error sending weekly report: {str(e)}")
        return False