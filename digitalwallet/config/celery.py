import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.beat_schedule = {
    # Executes every first of every month.
    'send-email-every-month': {
        'task': 'apps.transactions.tasks.userReport',
        'schedule': crontab(0, 0, day_of_month='1'),
        # 'args': (16, 16),
    },
}


app.autodiscover_tasks()