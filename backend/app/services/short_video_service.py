"""Service for fetching and caching short-form video reviews."""

import logging
from typing import List, Dict, Any, Optional
import asyncio
import httpx
import re
from uuid import UUID
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)

# Singleton HTTP client for video service with larger connection pool
_video_client = None

def get_video_client() -> httpx.AsyncClient:
    """Get or create singleton HTTP client for video service."""
    global _video_client
    if _video_client is None:
        limits = httpx.Limits(max_connections=50, max_keepalive_connections=10)
        _video_client = httpx.AsyncClient(timeout=30.0, limits=limits)
    return _video_client

# In-memory cache for short video reviews
short_video_cache: Dict[str, Dict[str, Any]] = {}
CACHE_EXPIRY_HOURS = 24


class ShortVideoReviewService:
    """Service to fetch short-form video reviews (YouTube Shorts, TikTok, Instagram Reels)."""

    def __init__(self):
        self.cache = short_video_cache
        self.cache_expiry = CACHE_EXPIRY_HOURS
        self.serpapi_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
        self.client = get_video_client()

    def _get_cache_key(self, product_id: str) -> str:
        """Generate cache key for product."""
        return f"short_videos_{product_id}"

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry or "timestamp" not in cache_entry:
            return False
        
        age_hours = (datetime.utcnow() - cache_entry["timestamp"]).total_seconds() / 3600
        return age_hours < self.cache_expiry

    async def fetch_short_video_reviews(
        self,
        product_id: UUID,
        product_title: str,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch short-form video reviews for a product using SerpAPI's google_short_videos engine.
        
        Searches for:
        - YouTube Shorts
        - TikTok videos
        - Instagram Reels
        
        Returns up to 10 results from SerpAPI.
        
        Args:
            product_id: UUID of the product
            product_title: Product title for search queries
            force_refresh: Bypass cache if True
        
        Returns:
            List of short video review dictionaries
        """
        cache_key = self._get_cache_key(str(product_id))
        
        # Check cache first
        if not force_refresh and cache_key in self.cache:
            cached = self.cache[cache_key]
            if self._is_cache_valid(cached):
                logger.info(f"[ShortVideoReview] Using cached videos for {product_id}")
                return cached["videos"]
        
        try:
            videos = await self._search_short_videos(product_title)
            
            # Cache the results
            self.cache[cache_key] = {
                "videos": videos,
                "timestamp": datetime.utcnow(),
                "product_id": str(product_id)
            }
            
            logger.info(f"[ShortVideoReview] Fetched {len(videos)} short videos for {product_title}")
            return videos
            
        except Exception as e:
            logger.error(f"[ShortVideoReview] Error fetching videos for {product_title}: {str(e)}")
            return []

    async def _search_short_videos(self, product_title: str) -> List[Dict[str, Any]]:
        """
        Search for short-form videos using SerpAPI's google_short_videos engine.
        
        Queries SerpAPI which aggregates:
        - YouTube Shorts
        - TikTok videos
        - Instagram Reels
        
        Returns up to 10 videos from all platforms combined.
        """
        if not self.serpapi_key:
            logger.warning("[ShortVideoReview] SerpAPI key not configured")
            return []
        
        try:
            params = {
                "engine": "google_short_videos",
                "q": product_title,
                "api_key": self.serpapi_key
            }
            
            logger.info(f"[ShortVideoReview] Searching SerpAPI for: {product_title}")
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            short_video_results = data.get("short_video_results", [])
            
            logger.info(f"[ShortVideoReview] Found {len(short_video_results)} short videos from SerpAPI")
            
            # Transform SerpAPI response to our format
            videos = []
            for result in short_video_results[:10]:  # Limit to 10
                video = self._transform_serpapi_result(result)
                if video:
                    videos.append(video)
            
            return videos
        
        except httpx.RequestError as e:
            logger.error(f"[ShortVideoReview] HTTP error querying SerpAPI: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"[ShortVideoReview] Error searching short videos: {str(e)}")
            return []

    def _transform_serpapi_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform SerpAPI short video result to our schema.
        
        Args:
            result: Raw result from SerpAPI google_short_videos engine
            
        Returns:
            Transformed video dictionary or None if invalid
        """
        try:
            # Extract platform from source
            source = result.get("source", "").lower()
            platform_map = {
                "youtube": "YouTube Shorts",
                "tiktok": "TikTok",
                "instagram": "Instagram Reels"
            }
            platform = platform_map.get(source, "YouTube Shorts")
            
            # Parse duration (format: "0:43" or "1:23")
            duration_str = result.get("duration", "")
            duration_seconds = None
            if duration_str:
                try:
                    parts = duration_str.split(":")
                    if len(parts) == 2:
                        minutes, seconds = int(parts[0]), int(parts[1])
                        duration_seconds = minutes * 60 + seconds
                except (ValueError, IndexError):
                    pass
            
            video = {
                "id": f"{source}_{result.get('position', 0)}",  # Unique ID
                "platform": platform,
                "video_url": result.get("link", ""),
                "thumbnail_url": result.get("thumbnail", ""),
                "creator": result.get("channel", ""),
                "caption": result.get("title", ""),
                "likes": 0,  # SerpAPI doesn't provide likes
                "views": 0,  # SerpAPI doesn't provide views
                "duration": duration_seconds,
                "source_icon": result.get("source_icon", ""),
                "clip_preview": result.get("clip", "")
            }
            
            # Only return if we have essential fields
            if video["video_url"] and video["caption"]:
                return video
            
            return None
            
        except Exception as e:
            logger.warning(f"[ShortVideoReview] Error transforming result: {str(e)}")
            return None

    def clear_cache(self) -> int:
        """Clear all cached short video reviews."""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"[ShortVideoReview] Cleared cache with {count} entries")
        return count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_cached_products": len(self.cache),
            "cache_entries": [
                {
                    "product_id": entry.get("product_id"),
                    "video_count": len(entry.get("videos", [])),
                    "age_hours": round((datetime.utcnow() - entry["timestamp"]).total_seconds() / 3600, 2)
                }
                for entry in self.cache.values()
            ]
        }


# Singleton instance
short_video_service = ShortVideoReviewService()
