from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from energy.models import EnergyData
from .models import EnergyTrend, EnergyPrediction
from .serializers import EnergyTrendSerializer, EnergyPredictionSerializer
from django.utils import timezone
from datetime import timedelta
import logging
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_daily_trends(request):
    """📊 Get daily energy trends for graphs"""
    try:
        days = int(request.query_params.get('days', 30))
        
        trends = EnergyTrend.objects.all().order_by('-date')[:days]
        serializer = EnergyTrendSerializer(trends, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching daily trends: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_hourly_trends(request):
    """📊 Get hourly energy trends"""
    try:
        hours = int(request.query_params.get('hours', 24))
        
        now = timezone.now()
        start_time = now - timedelta(hours=hours)
        
        data = EnergyData.objects.filter(timestamp__gte=start_time).order_by('timestamp')
        
        if not data.exists():
            return Response({'data': [], 'message': 'No data available'}, status=status.HTTP_200_OK)
        
        df = pd.DataFrame(list(data.values('timestamp', 'power')))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.floor('H')
        
        hourly = df.groupby('hour')['power'].agg(['mean', 'max', 'min']).reset_index()
        
        result = []
        for _, row in hourly.iterrows():
            result.append({
                'timestamp': row['hour'].isoformat(),
                'avg_power': float(row['mean']),
                'peak_power': float(row['max']),
                'min_power': float(row['min'])
            })
        
        return Response({
            'success': True,
            'data': result,
            'count': len(result)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching hourly trends: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def calculate_trends(request):
    """Calculate daily trends from raw data"""
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
        total_energy = (avg_power * 24) / 1000  # Convert to kWh
        
        peak_hour = 0
        max_power = 0
        for hour in range(24):
            hour_start = start.replace(hour=hour)
            hour_end = hour_start + timedelta(hours=1)
            hour_data = data.filter(timestamp__gte=hour_start, timestamp__lt=hour_end)
            hour_avg = hour_data.aggregate(avg=models.Avg('power'))['avg'] or 0
            if hour_avg > max_power:
                max_power = hour_avg
                peak_hour = hour
        
        trend, created = EnergyTrend.objects.get_or_create(
            date=today,
            defaults={
                'avg_power': avg_power,
                'peak_power': peak_power,
                'min_power': min_power,
                'total_energy': total_energy,
                'peak_hour': peak_hour
            }
        )
        
        serializer = EnergyTrendSerializer(trend)
        return Response({
            'success': True,
            'created': created,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error calculating trends: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def predict_energy(request):
    """🤖 Get AI predictions for next 48 hours"""
    try:
        days = int(request.query_params.get('days', 30))
        
        trends = EnergyTrend.objects.all().order_by('-date')[:days]
        
        if trends.count() < 7:
            return Response({
                'warning': 'Not enough data for accurate prediction',
                'data': []
            }, status=status.HTTP_200_OK)
        
        X = np.array(range(len(trends))).reshape(-1, 1)
        y = np.array([t.avg_power for t in trends])
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_X = np.array(range(len(trends), len(trends) + 48)).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        result = []
        for i, pred in enumerate(predictions):
            future_date = timezone.now().date() + timedelta(hours=i)
            result.append({
                'prediction_date': future_date.isoformat(),
                'predicted_power': float(max(0, pred)),
                'confidence': 0.75,
                'hour': i % 24
            })
        
        return Response({
            'success': True,
            'data': result,
            'count': len(result)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error predicting energy: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_statistics(request):
    """Get overall energy statistics"""
    try:
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Last 7 days
        data_week = EnergyData.objects.filter(timestamp__gte=week_ago)
        avg_week = data_week.aggregate(avg=models.Avg('power'))['avg'] or 0
        peak_week = data_week.aggregate(max=models.Max('power'))['max'] or 0
        
        # Last 30 days
        data_month = EnergyData.objects.filter(timestamp__gte=month_ago)
        avg_month = data_month.aggregate(avg=models.Avg('power'))['avg'] or 0
        
        return Response({
            'success': True,
            'statistics': {
                'last_7_days': {
                    'avg_power': float(avg_week),
                    'peak_power': float(peak_week),
                    'data_points': data_week.count()
                },
                'last_30_days': {
                    'avg_power': float(avg_month),
                    'data_points': data_month.count()
                }
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.db import models