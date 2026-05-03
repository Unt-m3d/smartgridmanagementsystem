import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

#  Use solo pool for Windows compatibility
app.conf.worker_pool = 'solo'

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

#  Schedule periodic tasks
app.conf.beat_schedule = {
    'predict-energy-every-hour': {
        'task': 'energy.tasks.predict_future_energy',
        'schedule': crontab(minute=0),
    },
    'check-anomalies-every-5-min': {
        'task': 'energy.tasks.check_energy_anomalies',
        'schedule': crontab(minute='*/5'),
    },
    'calculate-trends-daily': {
        'task': 'analytics.tasks.calculate_energy_trends',
        'schedule': crontab(hour=0, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')