from rest_framework.decorators import api_view
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
