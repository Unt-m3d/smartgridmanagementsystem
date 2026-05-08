from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserContact, AlertRule
from .serializers import UserContactSerializer, AlertRuleSerializer
from .tasks import send_email_alert, send_sms_alert
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def register_contact(request):
    """Register user contact for alerts"""
    try:
        serializer = UserContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Contact registered',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
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
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_alert_rules(request):
    """Get all active alert rules"""
    try:
        rules = AlertRule.objects.filter(is_active=True)
        serializer = AlertRuleSerializer(rules, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_email_alert(request):
    """Send test email alert"""
    try:
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ SEND EMAIL IMMEDIATELY
        result = send_email_alert(
            email=email,
            subject='🔌 Smart Grid Test Alert',
            message='This is a test email from your Smart Grid Management System.',
            html_message='<h2>🔌 Smart Grid Test Alert</h2><p>If you received this, email notifications are working!</p>'
        )
        
        if result:
            return Response({'success': True, 'message': f'✅ Email sent to {email}'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_sms_alert(request):
    """Send test SMS alert"""
    try:
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': 'Phone required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not phone.startswith('+'):
            phone = '+' + phone
        
        # ✅ SEND SMS IMMEDIATELY
        result = send_sms_alert(
            phone=phone,
            message='🔌 Smart Grid Test: Your SMS alerts are working!'
        )
        
        if result:
            return Response({'success': True, 'message': f'✅ SMS sent to {phone}'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'Failed to send SMS'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)