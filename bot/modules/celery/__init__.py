import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_mother.settings')
from django.conf import settings

app = Celery(
    'bot_mother',
    backend=settings.CELERY_BACKEND,
    broker=settings.CELERY_BROKER
)

# Time zone
app.conf.enable_utc = settings.USE_TZ
app.conf.timezone = settings.TIME_ZONE

# MQ interfaces
app.conf.accept_content = {'pickle'}
app.conf.task_serializer = 'pickle'
app.conf.result_serializer = 'pickle'

app.autodiscover_tasks()


