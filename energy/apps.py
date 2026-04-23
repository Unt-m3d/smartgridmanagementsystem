import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class EnergyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'energy'
    
    def ready(self):
        """Start simulator when Django starts"""
        try:
            from .simulator import start_simulator
            start_simulator()
            logger.info("✅ Energy simulator auto-started")
        except Exception as e:
            logger.warning(f"⚠️ Could not start simulator: {str(e)}")