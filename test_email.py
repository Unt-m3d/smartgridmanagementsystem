import os
from dotenv import load_dotenv
from django.core.mail import send_mail
from django.conf import settings

load_dotenv()

# Test email configuration
email_config = {
    'EMAIL_HOST': os.getenv('EMAIL_HOST'),
    'EMAIL_PORT': os.getenv('EMAIL_PORT'),
    'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER'),
    'EMAIL_HOST_PASSWORD': os.getenv('EMAIL_HOST_PASSWORD'),
}

print("📧 Email Configuration:")
print(f"  HOST: {email_config['EMAIL_HOST']}")
print(f"  PORT: {email_config['EMAIL_PORT']}")
print(f"  USER: {email_config['EMAIL_HOST_USER']}")
print(f"  PASSWORD: {'*' * len(email_config['EMAIL_HOST_PASSWORD']) if email_config['EMAIL_HOST_PASSWORD'] else 'NOT SET'}")

# Test connection
try:
    from django.core.mail.backends.smtp import EmailBackend
    backend = EmailBackend(
        host=email_config['EMAIL_HOST'],
        port=int(email_config['EMAIL_PORT']),
        username=email_config['EMAIL_HOST_USER'],
        password=email_config['EMAIL_HOST_PASSWORD'],
        use_tls=True,
        fail_silently=False
    )
    connection = backend.open()
    if connection:
        print("\n✅ Gmail connection successful!")
        backend.close()
    else:
        print("\n❌ Gmail connection failed!")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")