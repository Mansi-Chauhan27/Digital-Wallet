import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')


app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    'add-every-monday-morning': {
        'task': 'apps.transactions.tasks.userReport',
        'schedule': crontab(hour='*', minute='*', day_of_week='*'),
        # 'args': (16, 16),
    },
}


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()