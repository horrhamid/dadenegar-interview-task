from __future__ import absolute_import, unicode_literals
from dotenv import load_dotenv
from celery.schedules import crontab
import os

from celery import Celery
import warnings

warnings.filterwarnings("ignore")

env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), '.env')
load_dotenv(env_file)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FormFlow.settings')

app = Celery('FormFlow')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # noqa


app.conf.beat_schedule = {
    'archive-at-00:30-am-every-day': {
        'task': 'survey.tasks.archiver',
        'schedule': crontab(hour=0, minute=30),
    },
}
