# ecommerce_project/celery.py

"""
Celery Configuration

Sets up Celery for asynchronous task processing.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')

# Create Celery app
app = Celery('ecommerce_project')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery beat schedule for periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-expired-otps': {
        'task': 'apps.authentication.tasks.cleanup_expired_otps',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    'cleanup-old-login-attempts': {
        'task': 'apps.authentication.tasks.cleanup_old_login_attempts',
        'schedule': crontab(hour=3, minute=0),  # Run daily at 3 AM
    },
}