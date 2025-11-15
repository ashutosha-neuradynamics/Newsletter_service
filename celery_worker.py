"""
celery worker configurations
"""

import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv


load_dotenv()

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")
celery.conf.beat_scheduler = "redbeat.RedBeatScheduler"
celery.conf.redbeat_redis_url = os.getenv("CELERY_REDBEAT_REDIS_URL")
celery.conf.redbeat_key_prefix = os.getenv("CELERY_REDBEAT_KEY_PREFIX", "redbeat:")

# RedBeat Settings
celery.conf.redbeat_lock_timeout = 600  # 10 minutes in seconds
celery.conf.redbeat_lock_key = f"{celery.conf.redbeat_key_prefix}lock"
celery.conf.redbeat_retry_period = 300  # 5 minutes
celery.conf.redbeat_lock_retry = True  # Enable lock retry
celery.conf.redbeat_max_retries = 3  # Maximum number of retries

# Task discovery
celery.autodiscover_tasks([])

# Beat Schedule
celery.conf.beat_schedule = {
    "process_unread_emails": {
        "task": "",
        "schedule": crontab(minute="*/30"),
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
