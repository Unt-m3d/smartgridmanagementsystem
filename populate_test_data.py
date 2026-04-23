import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from energy.models import EnergyData
from django.utils import timezone

print("🔌 Creating test energy data...")

# Clear existing data (optional)
EnergyData.objects.all().delete()

# Create 100 data points over the last 2 hours
now = timezone.now()
base_voltage = 230
base_current = 5.0
base_power = 1150

for i in range(100):
    timestamp = now - timedelta(seconds=i*72)  # Every 72 seconds
    
    # Add some realistic variation
    voltage = base_voltage + random.uniform(-10, 10)
    current = base_current + random.uniform(-1, 1)
    power = voltage * current
    
    EnergyData.objects.create(
        voltage=round(voltage, 2),
        current=round(current, 2),
        power=round(power, 2),
        device_on=True,
        timestamp=timestamp
    )
    print(f"  ✅ {i+1}/100 - {timestamp.strftime('%H:%M:%S')} | {power:.0f}W")

print("\n✅ Test data created successfully!")
print(f"📊 Total records: {EnergyData.objects.count()}")

# Display latest data
latest = EnergyData.objects.latest('timestamp')
print(f"\n📈 Latest reading:")
print(f"   Voltage: {latest.voltage}V")
print(f"   Current: {latest.current}A")
print(f"   Power: {latest.power}W")
print(f"   Timestamp: {latest.timestamp}")