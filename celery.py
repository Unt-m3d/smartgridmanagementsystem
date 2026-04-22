import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'predict-energy-every-hour': {
        'task': 'energy.tasks.predict_future_energy',
        'schedule': crontab(minute=0),  # Every hour
    },
    'check-anomalies-every-15-min': {
        'task': 'energy.tasks.check_energy_anomalies',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'calculate-trends-every-hour': {
        'task': 'energy.tasks.calculate_energy_trends',
        'schedule': crontab(minute=0),  # Every hour
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')