"""Celery application configuration."""

import os
import logging
from celery import Celery
from celery.schedules import crontab
from app.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "imo_backend",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
)

# Import tasks to register them with Celery
from app.tasks import review_tasks  # noqa: F401, E402

# Configure Celery
celery_app.conf.update(
    # Task configuration
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution configuration
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Result backend configuration
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_on_timeout": True,
    },
    
    # Task routes (optional - for distributing tasks to specific workers)
    task_routes={
        "app.tasks.review_tasks.*": {"queue": "reviews"},
    },
    
    # Queues
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "reviews": {"exchange": "reviews", "routing_key": "reviews"},
        "high": {"exchange": "high", "routing_key": "high"},
    },
    
    # Beat schedule (if needed for periodic tasks)
    beat_schedule={
        # Example periodic task (uncomment if needed)
        # "clear-old-results": {
        #     "task": "app.tasks.cleanup.clear_old_results",
        #     "schedule": crontab(hour=2, minute=0),  # Run at 2 AM daily
        # },
    },
)

logger.info(f"Celery configured with broker: {celery_app.conf.broker_connection_retry_on_startup}")

# Autodiscover tasks from all modules
celery_app.autodiscover_tasks(['app.tasks'])
