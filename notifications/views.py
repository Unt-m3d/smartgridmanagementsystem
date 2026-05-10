from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserContact, AlertRule
from .serializers import UserContactSerializer, AlertRuleSerializer
from .tasks import send_email_alert, send_sms_alert, send_email_with_attachment
import logging
import json

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
                'message': 'Contact registered successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
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
                'message': 'Alert rule created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating alert rule: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_alert_rules(request):
    """Get all active alert rules"""
    try:
        rules = AlertRule.objects.filter(is_active=True)
        serializer = AlertRuleSerializer(rules, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting alert rules: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_email_alert(request):
    """Send test email alert - supports single or multiple emails"""
    try:
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Support both single email string and list of emails
        # Format: {"email": "test@gmail.com"} or {"email": ["test1@gmail.com", "test2@yahoo.com"]}
        
        result = send_email_alert(
            email=email,
            subject='[TEST] Smart Grid Alert System',
            message='This is a test email from your Smart Grid Management System.\n\nIf you received this email, your notification system is working correctly!',
            html_message='''
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #333;">🔌 Smart Grid Test Alert</h2>
                        <p style="color: #666; font-size: 14px;">If you received this email, your notification system is working correctly!</p>
                        <div style="background-color: #e8f4f8; padding: 15px; border-left: 4px solid #0099cc; margin-top: 20px;">
                            <p style="margin: 0; color: #0099cc;"><strong>Email notifications are ENABLED</strong></p>
                        </div>
                        <p style="color: #999; font-size: 12px; margin-top: 30px;">Smart Grid Management System</p>
                    </div>
                </body>
            </html>
            '''
        )
        
        if result:
            # Format email list for response
            email_list = email if isinstance(email, list) else [email]
            return Response({
                'success': True,
                'message': f'Email sent successfully to {len(email_list)} recipient(s)',
                'recipients': email_list
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to send email - check logs for details'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in test_email_alert: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_sms_alert(request):
    """Send test SMS alert"""
    try:
        phone = request.data.get('phone')
        if not phone:
            return Response({
                'success': False,
                'error': 'Phone number required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not phone.startswith('+'):
            phone = '+' + phone
        
        result = send_sms_alert(
            phone=phone,
            message='[TEST] Smart Grid Alert System: Your SMS alerts are working!'
        )
        
        if result:
            return Response({
                'success': True,
                'message': f'SMS sent successfully to {phone}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to send SMS - check logs for details'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in test_sms_alert: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def send_bulk_email_alert(request):
    """Send email to multiple recipients - NEW ENDPOINT"""
    try:
        emails = request.data.get('emails', [])
        subject = request.data.get('subject', 'Smart Grid Alert')
        message = request.data.get('message', '')
        html_message = request.data.get('html_message', None)
        
        if not emails:
            return Response({
                'success': False,
                'error': 'At least one email required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not message:
            return Response({
                'success': False,
                'error': 'Message required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle both list and comma-separated string
        if isinstance(emails, str):
            emails = [e.strip() for e in emails.split(',')]
        
        result = send_email_alert(
            email=emails,
            subject=subject,
            message=message,
            html_message=html_message
        )
        
        if result:
            return Response({
                'success': True,
                'message': f'Email sent to {len(emails)} recipient(s)',
                'recipients': emails
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to send emails'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in send_bulk_email_alert: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)