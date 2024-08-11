# myapp/tasks.py
from .models import Form
from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta


@shared_task
def archiver():
    cutoff_time = now() - timedelta(days=2)
    forms = Form.alives.filter(published_at__lt=cutoff_time, status=Form.StatusChoices.PUBLISHED)
    for form in forms:
        form.archive()

