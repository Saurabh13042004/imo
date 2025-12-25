"""Task initialization."""

# Import tasks so they are registered with Celery
from app.tasks.review_tasks import (
    fetch_community_reviews_task,
    fetch_store_reviews_task,
    fetch_google_reviews_task
)

__all__ = [
    "fetch_community_reviews_task",
    "fetch_store_reviews_task",
    "fetch_google_reviews_task",
]

