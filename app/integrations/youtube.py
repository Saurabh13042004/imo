"""YouTube integration."""

import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeClient:
    """Client for YouTube API integration."""

    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = YOUTUBE_API_BASE

    async def search_reviews(self, product_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for product review videos on YouTube."""
        if not self.api_key:
            logger.warning("YouTube API key not configured")
            return []

        try:
            params = {
                "part": "id,snippet",
                "q": f"{product_name} review",
                "type": "video",
                "maxResults": limit,
                "order": "relevance",
                "key": self.api_key
            }

            async with httpx.AsyncClient(timeout=settings.API_TIMEOUT) as client:
                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()

            data = response.json()
            videos = await self._get_video_details(data.get("items", []))
            logger.info(f"Found {len(videos)} YouTube videos for: {product_name}")
            return videos

        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []

    async def _get_video_details(self, video_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed information for videos."""
        video_ids = [item["id"]["videoId"] for item in video_items]

        if not video_ids:
            return []

        try:
            params = {
                "part": "statistics,snippet,contentDetails",
                "id": ",".join(video_ids),
                "key": self.api_key
            }

            async with httpx.AsyncClient(timeout=settings.API_TIMEOUT) as client:
                response = await client.get(f"{self.base_url}/videos", params=params)
                response.raise_for_status()

            data = response.json()
            return self._parse_video_details(data.get("items", []))

        except Exception as e:
            logger.error(f"Error getting YouTube video details: {e}")
            return []

    def _parse_video_details(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse video details from YouTube API response."""
        results = []
        try:
            for video in videos:
                snippet = video.get("snippet", {})
                statistics = video.get("statistics", {})

                video_data = {
                    "video_id": video.get("id", ""),
                    "title": snippet.get("title", ""),
                    "channel_name": snippet.get("channelTitle", ""),
                    "channel_id": snippet.get("channelId", ""),
                    "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "description": snippet.get("description", ""),
                    "published_at": snippet.get("publishedAt"),
                    "view_count": int(statistics.get("viewCount", 0)) if statistics.get("viewCount") else 0,
                    "like_count": int(statistics.get("likeCount", 0)) if statistics.get("likeCount") else 0,
                    "video_url": f"https://www.youtube.com/watch?v={video.get('id', '')}"
                }

                # Parse duration
                duration_str = video.get("contentDetails", {}).get("duration", "")
                video_data["duration"] = self._parse_duration(duration_str)

                results.append(video_data)
        except Exception as e:
            logger.error(f"Error parsing YouTube video details: {e}")

        return results

    @staticmethod
    def _parse_duration(duration_str: str) -> Optional[int]:
        """Parse ISO 8601 duration to seconds."""
        try:
            import re
            pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
            match = re.match(pattern, duration_str)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                return hours * 3600 + minutes * 60 + seconds
        except Exception as e:
            logger.error(f"Error parsing duration: {e}")
        return None
