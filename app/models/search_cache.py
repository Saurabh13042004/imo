"""Search cache model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models import Base


class SearchCache(Base):
    """Search cache database model."""

    __tablename__ = "search_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(String(200), nullable=False)
    source = Column(String(50), nullable=False)
    result_data = Column(JSON, nullable=True)
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_search_cache_query", "query", "source", unique=True),
        Index("idx_search_cache_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<SearchCache(id={self.id}, query={self.query}, source={self.source})>"
