from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EnergyData, DeviceStatus, EnergyPrediction, Alert, RenewableEnergyData, UserProfile
from .serializers import EnergyDataSerializer, EnergyPredictionSerializer, AlertSerializer, RenewableEnergySerializer
from .tasks import predict_future_energy, send_alert_notifications, check_energy_anomalies
from .analytics import get_energy_summary
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


def get_device_status():
    """Get current device status from database"""
    try:
        status_obj = DeviceStatus.objects.get(device_id='main_device')
        return status_obj.status == 'on'
    except DeviceStatus.DoesNotExist:
        DeviceStatus.objects.create(device_id='main_device', status='on')
        return True
    except Exception as e:
        logger.error(f"Error getting device status: {str(e)}")
        return True


def set_device_status(is_on):
    """Set device status in database"""
    try:
        device, created = DeviceStatus.objects.get_or_create(device_id='main_device')
        device.status = 'on' if is_on else 'off'
        device.save()
        logger.info(f"Device status set to: {device.status}")
    except Exception as e:
        logger.error(f"Error setting device status: {str(e)}")


@api_view(['POST'])
def receive_data(request):
    """Save energy data with validation"""
    try:
        serializer = EnergyDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Energy data saved successfully")
            
            # Trigger background tasks
            check_energy_anomalies.delay()
            
            return Response({"message": "Data saved successfully"}, status=201)

        logger.warning(f"Validation error: {serializer.errors}")
        return Response({
            "error": "Invalid data",
            "details": serializer.errors
        }, status=400)
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        return Response({
            "error": "Failed to save data",
            "details": str(e)
        }, status=500)


@api_view(['GET'])
def get_data(request):
    """Fetch energy data with pagination"""
    try:
        limit = request.query_params.get('limit', 100)
        hours = request.query_params.get('hours', None)

        try:
            limit = int(limit)
            if limit <= 0:
                limit = 100
            if limit > 1000:
                limit = 1000
        except ValueError:
            logger.warning(f"Invalid limit parameter: {limit}")
            limit = 100

        query = EnergyData.objects.all().order_by('-timestamp')
        
        if hours:
            try:
                hours = int(hours)
                start_time = timezone.now() - timedelta(hours=hours)
                query = query.filter(timestamp__gte=start_time)
            except ValueError:
                pass

        data = query[:limit]

        if not data.exists():
            logger.info("No energy data found")
            return Response([], status=200)

        serializer = EnergyDataSerializer(data, many=True)
        logger.info(f"Retrieved {len(serializer.data)} energy records")
        return Response(serializer.data, status=200)

    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return Response({
            "error": "Failed to fetch data",
            "details": str(e)
        }, status=500)


@api_view(['POST'])
def turn_on(request):
    """Turn device ON and save to database"""
    try:
        set_device_status(True)
        logger.info("Device turned ON")
        return Response({
            "status": "Device turned ON",
            "on": True,
            "message": "Device is now ON"
        }, status=200)
    except Exception as e:
        logger.error(f"Error turning on device: {str(e)}")
        return Response({
            "error": "Failed to turn on device",
            "details": str(e)
        }, status=500)


@api_view(['POST'])
def turn_off(request):
    """Turn device OFF and save to database"""
    try:
        set_device_status(False)
        logger.info("Device turned OFF")
        return Response({
            "status": "Device turned OFF",
            "on": False,
            "message": "Device is now OFF"
        }, status=200)
    except Exception as e:
        logger.error(f"Error turning off device: {str(e)}")
        return Response({
            "error": "Failed to turn off device",
            "details": str(e)
        }, status=500)


@api_view(['GET'])
def get_status(request):
    """Get current device status from database"""
    try:
        is_on = get_device_status()
        logger.debug(f"Device status retrieved: {is_on}")
        return Response({
            "on": is_on,
            "status": "ON" if is_on else "OFF"
        }, status=200)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return Response({
            "error": "Failed to get status",
            "details": str(e)
        }, status=500)


# ============ NEW ENDPOINTS ============

@api_view(['GET'])
def get_predictions(request):
    """Get AI energy predictions"""
    try:
        hours = request.query_params.get('hours', 24)
        
        try:
            hours = int(hours)
        except ValueError:
            hours = 24

        predictions = EnergyPrediction.objects.filter(
            predicted_timestamp__gte=timezone.now()
        ).order_by('predicted_timestamp')[:hours]

        serializer = EnergyPredictionSerializer(predictions, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        logger.error(f"Error fetching predictions: {str(e)}")
        return Response({
            "error": "Failed to fetch predictions",
            "details": str(e)
        }, status=500)


@api_view(['POST'])
def trigger_prediction(request):
    """Manually trigger energy prediction"""
    try:
        predict_future_energy.delay()
        return Response({
            "message": "Prediction task triggered",
            "status": "processing"
        }, status=202)
    except Exception as e:
        logger.error(f"Error triggering prediction: {str(e)}")
        return Response({
            "error": "Failed to trigger prediction",
            "details": str(e)
        }, status=500)


@api_view(['GET'])
def get_alerts(request):
    """Get user alerts"""
    try:
        status_filter = request.query_params.get('status', 'ACTIVE')
        
        alerts = Alert.objects.filter(
            status=status_filter
        ).order_by('-created_at')[:50]

        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return Response({
            "error": "Failed to fetch alerts",
            "details": str(e)
        }, status=500)


@api_view(['POST'])
def resolve_alert(request, alert_id):
    """Mark alert as resolved"""
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.status = 'RESOLVED'
        alert.resolved_at = timezone.now()
        alert.save()
        
        return Response({
            "message": "Alert resolved",
            "alert_id": alert_id
        }, status=200)
    except Alert.DoesNotExist:
        return Response({"error": "Alert not found"}, status=404)
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        return Response({
            "error": "Failed to resolve alert",
            "details": str(e)
        }, status=500)


@api_view(['GET', 'POST'])
def renewable_energy(request):
    """Get or add renewable energy data"""
    if request.method == 'GET':
        try:
            hours = request.query_params.get('hours', 24)
            start_time = timezone.now() - timedelta(hours=int(hours))
            
            data = RenewableEnergyData.objects.filter(
                timestamp__gte=start_time
            ).order_by('-timestamp')

            serializer = RenewableEnergySerializer(data, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.error(f"Error fetching renewable data: {str(e)}")
            return Response({
                "error": "Failed to fetch data",
                "details": str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            serializer = RenewableEnergySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Renewable energy data saved")
                return Response(serializer.data, status=201)
            
            return Response({
                "error": "Invalid data",
                "details": serializer.errors
            }, status=400)
        except Exception as e:
            logger.error(f"Error saving renewable data: {str(e)}")
            return Response({
                "error": "Failed to save data",
                "details": str(e)
            }, status=500)


@api_view(['GET'])
def energy_summary(request):
    """Get energy usage summary"""
    try:
        days = request.query_params.get('days', 7)
        
        try:
            days = int(days)
        except ValueError:
            days = 7

        summary = get_energy_summary(days)
        return Response(summary, status=200)
    except Exception as e:
        logger.error(f"Error fetching summary: {str(e)}")
        return Response({
            "error": "Failed to fetch summary",
            "details": str(e)
        }, status=500)


def dashboard(request):
    """Render dashboard template"""
    try:
        return render(request, 'dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return HttpResponse(f"<h1>Error</h1><p>{str(e)}</p>", status=500)