from sqlalchemy import Column, String, Integer, Float, DateTime, UUID, Index, ForeignKey
from datetime import datetime
import uuid
from app.models import Base


class ShortVideoReview(Base):
    """Short-form video review model (TikTok/YouTube Shorts/Instagram Reels style)."""

    __tablename__ = "short_video_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # 'youtube', 'tiktok', 'instagram'
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    creator = Column(String(200), nullable=False)
    caption = Column(String(1000), nullable=True)
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    duration = Column(Integer, nullable=True)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_product_platform', 'product_id', 'platform'),
    )

    def __repr__(self) -> str:
        return f"<ShortVideoReview(product_id={self.product_id}, platform={self.platform}, creator={self.creator})>"
