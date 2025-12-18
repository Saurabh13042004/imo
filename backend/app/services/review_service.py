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
from app.integrations.forums import ForumClient

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for managing product reviews."""

    def __init__(self):
        self.amazon_client = AmazonClient()
        self.reddit_client = RedditClient()
        self.youtube_client = YouTubeClient()
        self.forum_client = ForumClient()

    async def fetch_reviews(
        self,
        db: AsyncSession = None,
        product: Optional[object] = None,
        sources: List[str] = None,
        force_refresh: bool = False,
        product_title: Optional[str] = None
    ) -> List[dict]:
        """
        Fetch reviews from multiple sources.
        Can be called with either:
        - product + db + sources (for full Product objects)
        - product_title + sources (for direct title-based search)
        """
        try:
            if product_title:
                # Direct title-based search (used by intelligent endpoint)
                tasks = []
                for source in (sources or []):
                    task = self._fetch_source_reviews_by_title(product_title, source)
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)

                all_reviews = []
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Review fetch error: {result}")
                        continue
                    if result:
                        all_reviews.extend(result)

                logger.info(f"Fetched {len(all_reviews)} reviews for product: {product_title}")
                return all_reviews

            else:
                # Product-based search with database
                if not product or not db:
                    return []

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

    async def _fetch_source_reviews_by_title(
        self,
        product_title: str,
        source: str
    ) -> List[dict]:
        """Fetch reviews from a specific source using just the product title."""
        try:
            reviews_data = []

            if source.lower() == "reddit":
                reviews_data = await self.reddit_client.search_product(product_title)
            elif source.lower() == "forums":
                reviews_data = await self.forum_client.search_product(product_title)
            elif source.lower() == "youtube":
                reviews_data = await self.youtube_client.search_reviews(product_title)
            else:
                logger.warning(f"Unknown review source: {source}")
                return []

            # Normalize review data and add source field
            normalized_data = []
            for review in reviews_data:
                if not review or not review.get("source_review_id"):
                    continue

                normalized_review = {
                    "source": source.capitalize(),  # Add source field
                    "source_review_id": review.get("source_review_id", ""),
                    "author": review.get("author") or review.get("reviewer_name") or "Anonymous",
                    "rating": review.get("rating"),
                    "title": review.get("review_title") or review.get("title") or "",
                    "content": review.get("review_text") or review.get("content") or "",
                    "url": review.get("url") or ""
                }

                # Only add if we have content
                if normalized_review["content"]:
                    normalized_data.append(normalized_review)

            logger.info(f"Fetched {len(normalized_data)} reviews from {source} for '{product_title}'")
            return normalized_data

        except Exception as e:
            logger.error(f"Error fetching reviews from {source}: {e}")
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
            elif source.lower() == "forum":
                reviews_data = await self.forum_client.search_product(product.title)
            elif source.lower() == "youtube":
                reviews_data = await self.youtube_client.search_reviews(product.title)
            else:
                logger.warning(f"Unknown review source: {source}")
                return []

            # Normalize review data
            normalized_data = self._normalize_reviews(reviews_data, source)

            # Save reviews to database
            saved_reviews = []
            for review_data in normalized_data:
                review = await self._save_review(db, product.id, source, review_data)
                if review:
                    saved_reviews.append(review)

            return saved_reviews

        except Exception as e:
            logger.error(f"Error fetching reviews from {source}: {e}")
            return []

    def _normalize_reviews(self, reviews_data: List[dict], source: str) -> List[dict]:
        """Normalize review data from different sources to consistent format."""
        normalized = []

        for review in reviews_data:
            if not review or not review.get("source_review_id"):
                continue

            # Map source-specific fields to standard Review model fields
            normalized_review = {
                "source_review_id": review.get("source_review_id", ""),
                "author": review.get("author") or review.get("reviewer_name") or "Anonymous",
                "rating": review.get("rating"),
                "title": review.get("review_title") or review.get("title") or "",
                "content": review.get("review_text") or review.get("content") or "",
                "url": review.get("url") or ""
            }

            # Only add if we have content
            if normalized_review["content"]:
                normalized.append(normalized_review)

        return normalized

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
