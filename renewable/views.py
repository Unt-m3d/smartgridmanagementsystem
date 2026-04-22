from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RenewableSource, RenewableData, CarbonSavings
from .serializers import RenewableSourceSerializer, RenewableDataSerializer, CarbonSavingsSerializer
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def add_renewable_source(request):
    try:
        serializer = RenewableSourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error adding renewable source: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_renewable_sources(request):
    try:
        sources = RenewableSource.objects.all()
        serializer = RenewableSourceSerializer(sources, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching renewable sources: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def record_renewable_data(request):
    try:
        serializer = RenewableDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error recording renewable data: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_renewable_generation(request):
    try:
        data = RenewableData.objects.all().order_by('-timestamp')[:100]
        serializer = RenewableDataSerializer(data, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching renewable generation: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def record_carbon_savings(request):
    try:
        serializer = CarbonSavingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error recording carbon savings: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_carbon_savings(request):
    try:
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        savings = CarbonSavings.objects.filter(date__gte=start_date).order_by('-date')
        serializer = CarbonSavingsSerializer(savings, many=True)
        
        # Calculate totals
        totals = savings.aggregate(
            renewable_energy_kwh=Sum('renewable_energy_kwh'),
            carbon_saved_kg=Sum('carbon_saved_kg'),
            cost_saved=Sum('cost_saved')
        )
        
        return Response({
            'success': True,
            'data': serializer.data,
            'totals': {
                'renewable_energy_kwh': totals['renewable_energy_kwh'] or 0,
                'carbon_saved_kg': totals['carbon_saved_kg'] or 0,
                'cost_saved': totals['cost_saved'] or 0,
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching carbon savings: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)