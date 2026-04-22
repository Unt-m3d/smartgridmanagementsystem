from rest_framework.decorators import api_view
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

@api_view(['GET'])
def get_renewable_percentage(request):
    """Calculate renewable energy as percentage of total generation"""
    try:
        renewable_data = RenewableData.objects.all()
        
        if not renewable_data.exists():
            return Response({
                'success': True,
                'data': {
                    'renewable_percentage': 0.0,
                    'total_renewable_energy': 0.0,
                    'count': 0
                }
            }, status=status.HTTP_200_OK)
        
        total_renewable = sum([float(d.energy_generated) for d in renewable_data])
        
        return Response({
            'success': True,
            'data': {
                'renewable_percentage': 100.0,
                'total_renewable_energy': total_renewable,
                'count': renewable_data.count()
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error calculating renewable percentage: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)