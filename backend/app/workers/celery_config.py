"""
Celery Worker Configuration
"""
from celery import Celery

from app.config import settings


# Create Celery instance
celery_app = Celery(
    "ats_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Optional: Result expiration
celery_app.conf.result_expires = 3600  # 1 hour
