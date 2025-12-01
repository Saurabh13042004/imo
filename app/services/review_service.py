"""Review service for fetching and aggregating reviews."""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models import Review, Product
from app.schemas import ReviewResponse
from app.integrations.amazon import AmazonClient
from app.integrations.reddit import RedditClient
from app.integrations.youtube import YouTubeClient

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for managing product reviews."""

    def __init__(self):
        self.amazon_client = AmazonClient()
        self.reddit_client = RedditClient()
        self.youtube_client = YouTubeClient()

    async def fetch_reviews(
        self,
        db: AsyncSession,
        product: Product,
        sources: List[str],
        force_refresh: bool = False
    ) -> List[Review]:
        """Fetch reviews from multiple sources."""
        try:
            # Check if we need to refresh
            if not force_refresh and product.reviews:
                # Check if reviews are recent enough
                recent_reviews = [
                    r for r in product.reviews
                    if (datetime.utcnow() - r.fetched_at).days < 7
                ]
                if recent_reviews:
                    return recent_reviews

            # Fetch reviews from all sources in parallel
            tasks = []
            for source in sources:
                task = self._fetch_source_reviews(db, product, source)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_reviews = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Review fetch error: {result}")
                    continue
                if result:
                    all_reviews.extend(result)

            logger.info(f"Fetched {len(all_reviews)} reviews for product: {product.id}")
            return all_reviews

        except Exception as e:
            logger.error(f"Error fetching reviews: {e}")
            return []

    async def _fetch_source_reviews(
        self,
        db: AsyncSession,
        product: Product,
        source: str
    ) -> List[Review]:
        """Fetch reviews from a specific source."""
        try:
            reviews_data = []

            if source.lower() == "amazon" and product.asin:
                reviews_data = await self.amazon_client.get_reviews(product.asin)
            elif source.lower() == "reddit":
                reviews_data = await self.reddit_client.search_product(product.title)
            elif source.lower() == "youtube":
                reviews_data = await self.youtube_client.search_reviews(product.title)
            else:
                logger.warning(f"Unknown review source: {source}")
                return []

            # Save reviews to database
            saved_reviews = []
            for review_data in reviews_data:
                review = await self._save_review(db, product.id, source, review_data)
                if review:
                    saved_reviews.append(review)

            return saved_reviews

        except Exception as e:
            logger.error(f"Error fetching reviews from {source}: {e}")
            return []

    async def _save_review(
        self,
        db: AsyncSession,
        product_id: str,
        source: str,
        review_data: dict
    ) -> Optional[Review]:
        """Save or update review in database."""
        try:
            # Check if review exists
            result = await db.execute(
                select(Review).where(
                    and_(
                        Review.product_id == product_id,
                        Review.source == source,
                        Review.source_review_id == review_data.get("source_review_id")
                    )
                )
            )
            review = result.scalar_one_or_none()

            if review:
                # Update existing review
                for key, value in review_data.items():
                    if hasattr(review, key):
                        setattr(review, key, value)
            else:
                # Create new review
                review = Review(
                    product_id=product_id,
                    source=source,
                    **review_data
                )
                db.add(review)

            await db.commit()
            return review

        except Exception as e:
            logger.error(f"Error saving review: {e}")
            await db.rollback()
            return None

    async def get_product_reviews(
        self,
        db: AsyncSession,
        product_id: str
    ) -> List[Review]:
        """Get all reviews for a product."""
        try:
            result = await db.execute(
                select(Review).where(Review.product_id == product_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting product reviews: {e}")
            return []

    async def analyze_sentiment(self, reviews: List[Review]) -> dict:
        """Analyze overall sentiment of reviews."""
        if not reviews:
            return {
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "overall_score": 0
            }

        sentiment_counts = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

        for review in reviews:
            if review.sentiment:
                sentiment_counts[review.sentiment.lower()] += 1

        total = len(reviews)
        overall_score = (
            (sentiment_counts["positive"] * 1.0 +
             sentiment_counts["neutral"] * 0.5) / total
        ) if total > 0 else 0

        return {
            **sentiment_counts,
            "overall_score": round(overall_score, 2),
            "total_reviews": total
        }
