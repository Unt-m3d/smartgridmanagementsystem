from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min, Sum, Count
from .models import EnergyData, EnergyTrend
import logging

logger = logging.getLogger(__name__)


def calculate_trends():
    """Calculate energy trends for different periods"""
    now = timezone.now()
    
    calculate_period_trend('HOURLY', now, timedelta(hours=1))
    calculate_period_trend('DAILY', now, timedelta(days=1))
    calculate_period_trend('WEEKLY', now, timedelta(weeks=1))
    calculate_period_trend('MONTHLY', now, timedelta(days=30))


def calculate_period_trend(period, timestamp, period_delta):
    """Calculate trend for a specific period"""
    try:
        start_time = timestamp - period_delta
        
        data = EnergyData.objects.filter(
            timestamp__gte=start_time,
            timestamp__lte=timestamp
        ).aggregate(
            avg_power=Avg('power'),
            peak_power=Max('power'),
            min_power=Min('power'),
            sum_power=Sum('power'),
            count=Count('id')
        )
        
        if data['avg_power'] is None or data['count'] == 0:
            return
        
        total_energy = (data['sum_power'] / 1000) * (5 / 3600)
        
        EnergyTrend.objects.update_or_create(
            period=period,
            timestamp=timestamp,
            defaults={
                'average_power': data['avg_power'],
                'peak_power': data['peak_power'],
                'minimum_power': data['min_power'],
                'total_energy': total_energy,
            }
        )
        
        logger.info(f"{period} trend calculated")
    except Exception as e:
        logger.error(f"Trend calculation error for {period}: {str(e)}")


def get_energy_summary(days=7):
    """Get energy summary for last N days"""
    start_date = timezone.now() - timedelta(days=days)
    
    data = EnergyData.objects.filter(
        timestamp__gte=start_date
    ).aggregate(
        avg_power=Avg('power'),
        peak_power=Max('power'),
        total_records=Count('id')
    )
    
    total_energy_result = EnergyTrend.objects.filter(
        period='DAILY',
        timestamp__gte=start_date
    ).aggregate(Sum('total_energy'))
    
    total_energy = total_energy_result['total_energy__sum'] or 0
    
    return {
        'average_power': data['avg_power'] or 0,
        'peak_power': data['peak_power'] or 0,
        'total_energy_kwh': total_energy,
        'records': data['total_records'] or 0,
        'period_days': days,
    }