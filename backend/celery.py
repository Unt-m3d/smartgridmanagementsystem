import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# ===== WINDOWS DEVELOPMENT MODE =====
# Disable Redis requirement - run tasks synchronously
app.conf.update(
    task_always_eager=True,  # Execute tasks immediately
    task_eager_propagates=True,  # Show errors immediately
)