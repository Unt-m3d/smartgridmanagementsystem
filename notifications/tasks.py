import logging
logger = logging.getLogger(__name__)

def send_email_alert(email, subject, message):
    logger.info(f"Email to {email}: {subject}")
    return True

def send_sms_alert(phone, message):
    logger.info(f"SMS to {phone}")
    return True
