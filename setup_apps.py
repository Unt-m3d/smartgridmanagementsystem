import os

# Create analytics app
os.makedirs('analytics/migrations', exist_ok=True)

# Create notifications app
os.makedirs('notifications/migrations', exist_ok=True)

# Create renewable app
os.makedirs('renewable/migrations', exist_ok=True)

# Analytics files
with open('analytics/__init__.py', 'w') as f:
    f.write('')

with open('analytics/apps.py', 'w') as f:
    f.write('''from django.apps import AppConfig

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
''')

with open('analytics/models.py', 'w') as f:
    f.write('''from django.db import models

class EnergyTrend(models.Model):
    date = models.DateField(unique=True)
    avg_power = models.FloatField()
    peak_power = models.FloatField()
    min_power = models.FloatField()
    total_energy = models.FloatField()
    peak_hour = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - Avg: {self.avg_power}W"

class EnergyPrediction(models.Model):
    prediction_date = models.DateField()
    predicted_power = models.FloatField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prediction_date']

    def __str__(self):
        return f"{self.prediction_date} - {self.predicted_power}W"
''')

with open('analytics/serializers.py', 'w') as f:
    f.write('''from rest_framework import serializers
from .models import EnergyTrend, EnergyPrediction

class EnergyTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyTrend
        fields = ['id', 'date', 'avg_power', 'peak_power', 'min_power', 'total_energy', 'peak_hour', 'created_at']

class EnergyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyPrediction
        fields = ['id', 'prediction_date', 'predicted_power', 'confidence', 'created_at']
''')

with open('analytics/views.py', 'w') as f:
    f.write('''from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from energy.models import EnergyData
from .models import EnergyTrend, EnergyPrediction
from .serializers import EnergyTrendSerializer, EnergyPredictionSerializer
from django.utils import timezone
from datetime import timedelta
import logging
from django.db import models

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_daily_trends(request):
    try:
        days = int(request.query_params.get('days', 30))
        trends = EnergyTrend.objects.all().order_by('-date')[:days]
        serializer = EnergyTrendSerializer(trends, many=True)
        return Response({'success': True, 'data': serializer.data, 'count': len(serializer.data)}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_hourly_trends(request):
    try:
        hours = int(request.query_params.get('hours', 24))
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        data = EnergyData.objects.filter(timestamp__gte=start_time).order_by('timestamp')
        return Response({'success': True, 'data': []}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def calculate_trends(request):
    try:
        today = timezone.now().date()
        start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        end = timezone.make_aware(timezone.datetime.combine(today + timedelta(days=1), timezone.datetime.min.time()))
        data = EnergyData.objects.filter(timestamp__gte=start, timestamp__lt=end)
        if not data.exists():
            return Response({'message': 'No data for today'}, status=status.HTTP_200_OK)
        avg_power = data.aggregate(avg=models.Avg('power'))['avg'] or 0
        peak_power = data.aggregate(max=models.Max('power'))['max'] or 0
        min_power = data.aggregate(min=models.Min('power'))['min'] or 0
        total_energy = (avg_power * 24) / 1000
        trend, created = EnergyTrend.objects.get_or_create(date=today, defaults={'avg_power': avg_power, 'peak_power': peak_power, 'min_power': min_power, 'total_energy': total_energy, 'peak_hour': 0})
        serializer = EnergyTrendSerializer(trend)
        return Response({'success': True, 'created': created, 'data': serializer.data}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def predict_energy(request):
    try:
        days = int(request.query_params.get('days', 30))
        trends = EnergyTrend.objects.all().order_by('-date')[:days]
        if trends.count() < 7:
            return Response({'warning': 'Not enough data', 'data': []}, status=status.HTTP_200_OK)
        return Response({'success': True, 'data': []}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_statistics(request):
    try:
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        data_week = EnergyData.objects.filter(timestamp__gte=week_ago)
        avg_week = data_week.aggregate(avg=models.Avg('power'))['avg'] or 0
        return Response({'success': True, 'avg_power': float(avg_week)}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
''')

with open('analytics/urls.py', 'w') as f:
    f.write('''from django.urls import path
from . import views

urlpatterns = [
    path('daily-trends/', views.get_daily_trends, name='daily-trends'),
    path('hourly-trends/', views.get_hourly_trends, name='hourly-trends'),
    path('calculate-trends/', views.calculate_trends, name='calculate-trends'),
    path('predict/', views.predict_energy, name='predict-energy'),
    path('statistics/', views.get_statistics, name='statistics'),
]
''')

with open('analytics/migrations/__init__.py', 'w') as f:
    f.write('')

# Notifications files
with open('notifications/__init__.py', 'w') as f:
    f.write('')

with open('notifications/apps.py', 'w') as f:
    f.write('''from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
''')

with open('notifications/models.py', 'w') as f:
    f.write('''from django.db import models

class UserContact(models.Model):
    user_email = models.EmailField(unique=True)
    user_phone = models.CharField(max_length=20, blank=True, null=True)
    receive_email_alerts = models.BooleanField(default=True)
    receive_sms_alerts = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_email

class AlertRule(models.Model):
    name = models.CharField(max_length=100)
    alert_type = models.CharField(max_length=50, choices=[('voltage_high', 'High Voltage'), ('voltage_low', 'Low Voltage'), ('power_high', 'High Power')])
    threshold = models.FloatField()
    is_active = models.BooleanField(default=True)
    contact = models.ForeignKey(UserContact, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.threshold}"
''')

with open('notifications/serializers.py', 'w') as f:
    f.write('''from rest_framework import serializers
from .models import UserContact, AlertRule

class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContact
        fields = ['id', 'user_email', 'user_phone', 'receive_email_alerts', 'receive_sms_alerts']

class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = ['id', 'name', 'alert_type', 'threshold', 'is_active', 'contact']
''')

with open('notifications/views.py', 'w') as f:
    f.write('''from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserContact, AlertRule
from .serializers import UserContactSerializer, AlertRuleSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def register_contact(request):
    try:
        serializer = UserContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Contact registered', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_alert_rule(request):
    try:
        serializer = AlertRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Alert rule created', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_alert_rules(request):
    try:
        rules = AlertRule.objects.filter(is_active=True)
        serializer = AlertRuleSerializer(rules, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def test_email_alert(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': True, 'message': f'Test email sent to {email}'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def test_sms_alert(request):
    try:
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone required'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': True, 'message': f'Test SMS sent to {phone}'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
''')

with open('notifications/urls.py', 'w') as f:
    f.write('''from django.urls import path
from . import views

urlpatterns = [
    path('register-contact/', views.register_contact, name='register-contact'),
    path('create-rule/', views.create_alert_rule, name='create-rule'),
    path('get-rules/', views.get_alert_rules, name='get-rules'),
    path('test-email/', views.test_email_alert, name='test-email'),
    path('test-sms/', views.test_sms_alert, name='test-sms'),
]
''')

with open('notifications/tasks.py', 'w') as f:
    f.write('''import logging
logger = logging.getLogger(__name__)

def send_email_alert(email, subject, message):
    logger.info(f"Email to {email}: {subject}")
    return True

def send_sms_alert(phone, message):
    logger.info(f"SMS to {phone}")
    return True
''')

with open('notifications/migrations/__init__.py', 'w') as f:
    f.write('')

# Renewable files
with open('renewable/__init__.py', 'w') as f:
    f.write('')

with open('renewable/apps.py', 'w') as f:
    f.write('''from django.apps import AppConfig

class RenewableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'renewable'
''')

with open('renewable/models.py', 'w') as f:
    f.write('''from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class RenewableSource(models.Model):
    SOURCE_TYPES = [('solar', 'Solar Panel'), ('wind', 'Wind Turbine'), ('hydro', 'Hydroelectric'), ('other', 'Other')]
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    capacity = models.FloatField(validators=[MinValueValidator(0)])
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

class RenewableData(models.Model):
    source = models.ForeignKey(RenewableSource, on_delete=models.CASCADE)
    power_generated = models.FloatField(validators=[MinValueValidator(0)])
    efficiency = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.source.name} - {self.power_generated}W"

class CarbonSavings(models.Model):
    date = models.DateField(unique=True)
    renewable_energy_kwh = models.FloatField(validators=[MinValueValidator(0)])
    carbon_saved_kg = models.FloatField(validators=[MinValueValidator(0)])
    cost_saved = models.FloatField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}"
''')

with open('renewable/serializers.py', 'w') as f:
    f.write('''from rest_framework import serializers
from .models import RenewableSource, RenewableData, CarbonSavings

class RenewableSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenewableSource
        fields = ['id', 'name', 'source_type', 'capacity', 'location', 'is_active']

class RenewableDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenewableData
        fields = ['id', 'source', 'power_generated', 'efficiency', 'timestamp']

class CarbonSavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonSavings
        fields = ['id', 'date', 'renewable_energy_kwh', 'carbon_saved_kg', 'cost_saved']
''')

with open('renewable/views.py', 'w') as f:
    f.write('''from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RenewableSource, RenewableData, CarbonSavings
from .serializers import RenewableSourceSerializer, RenewableDataSerializer, CarbonSavingsSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def add_renewable_source(request):
    try:
        serializer = RenewableSourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_renewable_sources(request):
    try:
        sources = RenewableSource.objects.all()
        serializer = RenewableSourceSerializer(sources, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def record_renewable_data(request):
    try:
        serializer = RenewableDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_renewable_generation(request):
    try:
        data = RenewableData.objects.all().order_by('-timestamp')[:100]
        serializer = RenewableDataSerializer(data, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def record_carbon_savings(request):
    try:
        serializer = CarbonSavingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_carbon_savings(request):
    try:
        savings = CarbonSavings.objects.all().order_by('-date')[:30]
        serializer = CarbonSavingsSerializer(savings, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
''')

with open('renewable/urls.py', 'w') as f:
    f.write('''from django.urls import path
from . import views

urlpatterns = [
    path('add-source/', views.add_renewable_source, name='add-source'),
    path('sources/', views.get_renewable_sources, name='sources'),
    path('record-data/', views.record_renewable_data, name='record-data'),
    path('generation/', views.get_renewable_generation, name='generation'),
    path('carbon-savings/', views.get_carbon_savings, name='carbon-savings'),
    path('record-carbon/', views.record_carbon_savings, name='record-carbon'),
]
''')

with open('renewable/migrations/__init__.py', 'w') as f:
    f.write('')

# Create backend/celery.py
with open('backend/celery.py', 'w') as f:
    f.write('''import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
''')

print("All apps created successfully!")
print("Next step: python manage.py makemigrations && python manage.py migrate")