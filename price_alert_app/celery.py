from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_alert_app.settings')

app = Celery('price_alert_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'check-prices-every-5-minutes': {
        'task': 'alerts.tasks.scheduled_price_check',
        'schedule': crontab(minute='*/5'),
    },
}
