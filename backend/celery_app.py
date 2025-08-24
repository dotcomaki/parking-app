from celery import Celery
import celery
from celery.schedules import crontab
from .app import create_app
from .config import Config

def make_celery(app=None):
    """
    Factory to create a Celery instance tied to our Flask app.
    """
    app = app or create_app()
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config.get('result_backend', app.config['CELERY_BROKER_URL']),
        include=['backend.tasks']
    )
    celery.conf.update(app.config)

    celery.conf.beat_schedule = {
        'daily-chat-reminder': {
            'task': 'backend.tasks.send_daily_reminder',
            'schedule': crontab(hour=9, minute=0),
        },
        'monthly-parking-report': {
            'task': 'backend.tasks.send_monthly_report',
            'schedule': crontab(day_of_month=1, hour=8, minute=0),
        },
    }

    celery.conf.timezone = 'Asia/Kolkata'

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    return celery

celery = make_celery()