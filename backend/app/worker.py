"""Celery worker entry point."""

from app.celery_app import celery_app
from app.tasks import review_tasks  # noqa: F401

if __name__ == '__main__':
    celery_app.start()
