import random
import time
from django.utils import timezone
from .models import EnergyData
import threading
import logging

logger = logging.getLogger(__name__)


class EnergySimulator:
    """Simulates realistic energy data"""
    
    def __init__(self, interval=1):  # Generate data every 1 second
        self.interval = interval
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the simulator in background"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("Energy simulator started (1 second interval)")
    
    def stop(self):
        """Stop the simulator"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Energy simulator stopped")
    
    def _run(self):
        """Main simulation loop"""
        base_voltage = 230
        base_current = 5.0
        
        while self.running:
            try:
                # Simulate realistic energy values with variation
                hour = timezone.now().hour
                
                # Higher usage during day (9-17), lower at night
                if 9 <= hour < 18:
                    power_multiplier = 1.2 + random.uniform(-0.3, 0.5)
                else:
                    power_multiplier = 0.6 + random.uniform(-0.2, 0.3)
                
                voltage = base_voltage + random.uniform(-15, 15)
                current = base_current * power_multiplier + random.uniform(-1, 1)
                power = voltage * current
                
                # Create data point
                EnergyData.objects.create(
                    voltage=round(max(180, min(250, voltage)), 2),
                    current=round(max(0, current), 2),
                    power=round(max(0, power), 2),
                    device_on=True
                )
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Simulator error: {str(e)}")
                time.sleep(self.interval)


# Global simulator instance
_simulator = EnergySimulator(interval=1)


def start_simulator():
    """Start energy data simulator"""
    _simulator.start()


def stop_simulator():
    """Stop energy data simulator"""
    _simulator.stop()