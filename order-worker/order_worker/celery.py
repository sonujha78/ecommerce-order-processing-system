import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "order_worker.settings")

app = Celery("order_worker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
