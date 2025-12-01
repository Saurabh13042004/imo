"""Video model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, BigInteger, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models import Base


class Video(Base):
    """Video (YouTube) database model."""

    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(String(50), nullable=False)
    title = Column(String(500), nullable=True)
    channel_name = Column(String(200), nullable=True)
    channel_id = Column(String(100), nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    view_count = Column(BigInteger, nullable=True)
    like_count = Column(Integer, nullable=True)
    published_at = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="videos")

    __table_args__ = (
        Index("idx_videos_product", "product_id"),
        Index("idx_videos_product_id", "product_id", "video_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, product_id={self.product_id}, video_id={self.video_id})>"
