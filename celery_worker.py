"""
Celery worker configuration for Newsletter Service
"""

import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

celery = Celery("newsletter_service")
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Use RedBeat scheduler if available, otherwise use default
redbeat_redis_url = os.getenv("CELERY_REDBEAT_REDIS_URL")
if redbeat_redis_url:
    celery.conf.beat_scheduler = "redbeat.RedBeatScheduler"
    celery.conf.redbeat_redis_url = redbeat_redis_url
    celery.conf.redbeat_key_prefix = os.getenv("CELERY_REDBEAT_KEY_PREFIX", "redbeat:")
    celery.conf.redbeat_lock_timeout = 600
    celery.conf.redbeat_lock_key = f"{celery.conf.redbeat_key_prefix}lock"
    celery.conf.redbeat_retry_period = 300
    celery.conf.redbeat_lock_retry = True
    celery.conf.redbeat_max_retries = 3

# Task discovery
celery.autodiscover_tasks(["app.tasks"])

# Beat Schedule - Check for due content every minute
celery.conf.beat_schedule = {
    "check-due-content": {
        "task": "app.tasks.check_due_content",
        "schedule": crontab(minute="*"),  # Every minute
    }
}

# General Celery Settings
celery.conf.update(
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3540,  # 59 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
