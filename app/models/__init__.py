"""Database models."""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.product import Product
from app.models.review import Review
from app.models.video import Video
from app.models.search_cache import SearchCache

__all__ = ["Base", "Product", "Review", "Video", "SearchCache"]
