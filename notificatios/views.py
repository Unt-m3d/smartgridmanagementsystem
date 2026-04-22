from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserContact, AlertRule
from .serializers import UserContactSerializer, AlertRuleSerializer
from .tasks import send_email_alert, send_sms_alert, check_alerts
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def register_contact(request):
    """🔔 Register user contact for alerts"""
    try:
        serializer = UserContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Contact registered successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error registering contact: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_alert_rule(request):
    """Create alert rule"""
    try:
        serializer = AlertRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Alert rule created',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating alert rule: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_alert_rules(request):
    """Get all alert rules"""
    try:
        rules = AlertRule.objects.filter(is_active=True)
        serializer = AlertRuleSerializer(rules, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching alert rules: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_email_alert(request):
    """Test email alert"""
    try:
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        
        send_email_alert.delay(
            email,
            "Test Alert - Smart Grid",
            "This is a test alert from your Smart Grid Management System"
        )
        
        return Response({
            'success': True,
            'message': f'Test email sent to {email}'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_sms_alert(request):
    """Test SMS alert"""
    try:
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone number required'}, status=status.HTTP_400_BAD_REQUEST)
        
        send_sms_alert.delay(
            phone,
            "Test SMS: Smart Grid Management System"
        )
        
        return Response({
            'success': True,
            'message': f'Test SMS sent to {phone}'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error sending test SMS: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def trigger_alert_check(request):
    """Manually trigger alert check"""
    try:
        check_alerts.delay()
        return Response({
            'success': True,
            'message': 'Alert check triggered'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error triggering alert check: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)