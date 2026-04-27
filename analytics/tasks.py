from celery import shared_task
from energy.models import EnergyData, EnergyTrend
from analytics.models import EnergyTrend as AnalyticsTrend
from django.utils import timezone
from datetime import timedelta
from django.db import models
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def calculate_energy_trends(self):
    """Calculate daily energy trends - runs at midnight"""
    try:
        today = timezone.now().date()
        start = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time())
        )
        end = timezone.make_aware(
            timezone.datetime.combine(today + timedelta(days=1), timezone.datetime.min.time())
        )
        
        # Get energy data for today
        data = EnergyData.objects.filter(timestamp__gte=start, timestamp__lt=end)
        
        if not data.exists():
            logger.info(f"No energy data found for {today}")
            return {"status": "no_data", "date": str(today)}
        
        # Calculate statistics
        avg_power = data.aggregate(avg=models.Avg('power'))['avg'] or 0
        peak_power = data.aggregate(max=models.Max('power'))['max'] or 0
        min_power = data.aggregate(min=models.Min('power'))['min'] or 0
        total_energy = (avg_power * 24) / 1000  # Convert to kWh
        
        # Find peak hour
        hourly_avg = {}
        for record in data:
            hour = record.timestamp.hour
            if hour not in hourly_avg:
                hourly_avg[hour] = []
            hourly_avg[hour].append(record.power)
        
        peak_hour = max(hourly_avg, key=lambda h: sum(hourly_avg[h]) / len(hourly_avg[h])) if hourly_avg else 0
        
        # Save to analytics app's EnergyTrend model
        trend, created = AnalyticsTrend.objects.get_or_create(
            date=today,
            defaults={
                'avg_power': avg_power,
                'peak_power': peak_power,
                'min_power': min_power,
                'total_energy': total_energy,
                'peak_hour': peak_hour
            }
        )
        
        if not created:
            trend.avg_power = avg_power
            trend.peak_power = peak_power
            trend.min_power = min_power
            trend.total_energy = total_energy
            trend.peak_hour = peak_hour
            trend.save()
        
        logger.info(f"Energy trends calculated for {today}: Avg={avg_power}W, Peak={peak_power}W")
        
        return {
            "status": "success",
            "date": str(today),
            "avg_power": avg_power,
            "peak_power": peak_power
        }
        
    except Exception as e:
        logger.error(f"Trend calculation error: {str(e)}")
        raise self.retry(exc=e, countdown=60)