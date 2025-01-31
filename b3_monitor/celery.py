import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b3_monitor.settings')

app = Celery('b3_monitor')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Define Celery Beat schedule - we'll fetch every minute to check frequencies
app.conf.beat_schedule = {
    'fetch-asset-prices': {
        'task': 'assets.tasks.fetch_asset_prices',
        'schedule': crontab(minute='*'),  # Run every minute
    },
}