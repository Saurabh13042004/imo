"""Video service for fetching YouTube reviews."""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Video, Product
from app.integrations.youtube import YouTubeClient

logger = logging.getLogger(__name__)


class VideoService:
    """Service for managing product videos."""

    def __init__(self):
        self.youtube_client = YouTubeClient()

    async def fetch_product_videos(
        self,
        db: AsyncSession,
        product: Product,
        force_refresh: bool = False,
        min_views: int = 0
    ) -> List[Video]:
        """Fetch YouTube videos for a product."""
        try:
            # Check if we need to refresh
            if not force_refresh and product.videos:
                existing_videos = [
                    v for v in product.videos
                    if v.view_count and v.view_count >= min_views
                ]
                if existing_videos:
                    return existing_videos

            # Fetch videos from YouTube
            videos_data = await self.youtube_client.search_reviews(product.title)

            # Filter by minimum views
            filtered_videos = [
                v for v in videos_data
                if v.get("view_count", 0) >= min_views
            ]

            # Save videos to database
            saved_videos = []
            for video_data in filtered_videos:
                video = await self._save_video(db, product.id, video_data)
                if video:
                    saved_videos.append(video)

            logger.info(f"Fetched {len(saved_videos)} videos for product: {product.id}")
            return saved_videos

        except Exception as e:
            logger.error(f"Error fetching videos: {e}")
            return []

    async def _save_video(
        self,
        db: AsyncSession,
        product_id: str,
        video_data: dict
    ) -> Optional[Video]:
        """Save or update video in database."""
        try:
            # Check if video exists
            result = await db.execute(
                select(Video).where(
                    Video.product_id == product_id,
                    Video.video_id == video_data.get("video_id")
                )
            )
            video = result.scalar_one_or_none()

            if video:
                # Update existing video
                for key, value in video_data.items():
                    if hasattr(video, key):
                        setattr(video, key, value)
            else:
                # Create new video
                video = Video(
                    product_id=product_id,
                    **video_data
                )
                db.add(video)

            await db.commit()
            return video

        except Exception as e:
            logger.error(f"Error saving video: {e}")
            await db.rollback()
            return None

    async def get_product_videos(
        self,
        db: AsyncSession,
        product_id: str
    ) -> List[Video]:
        """Get all videos for a product."""
        try:
            result = await db.execute(
                select(Video).where(Video.product_id == product_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting product videos: {e}")
            return []
