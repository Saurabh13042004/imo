"""Reddit integration."""

import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

REDDIT_API_BASE = "https://oauth.reddit.com"


class RedditClient:
    """Client for Reddit API integration."""

    def __init__(self):
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        self.base_url = REDDIT_API_BASE
        self.access_token = None

    async def _get_access_token(self) -> Optional[str]:
        """Get Reddit OAuth access token."""
        if not self.client_id or not self.client_secret:
            logger.warning("Reddit credentials not configured")
            return None

        if self.access_token:
            return self.access_token

        try:
            auth = (self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.post(
                    "https://www.reddit.com/api/v1/access_token",
                    auth=auth,
                    data=data,
                    headers={"User-Agent": "ProductAggregator/1.0"}
                )
                response.raise_for_status()

            self.access_token = response.json()["access_token"]
            return self.access_token

        except Exception as e:
            logger.error(f"Error getting Reddit access token: {e}")
            return None

    async def search_product(self, product_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search Reddit for product discussions and reviews."""
        token = await self._get_access_token()
        if not token:
            logger.warning("Reddit access token not available")
            return []

        try:
            headers = {
                "Authorization": f"bearer {token}",
                "User-Agent": "ProductAggregator/1.0"
            }

            params = {
                "q": f"{product_name} review OR discussion",
                "limit": limit,
                "sort": "relevance",
                "time": "all",
                "type": "comments"
            }

            async with httpx.AsyncClient(timeout=settings.API_TIMEOUT) as client:
                response = await client.get(
                    f"{self.base_url}/r/all/search",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()

            data = response.json()
            results = self._parse_search_results(data)
            logger.info(f"Found {len(results)} Reddit posts for: {product_name}")
            return results

        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []

    def _parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse search results from Reddit API."""
        results = []
        try:
            children = data.get("data", {}).get("children", [])

            for item in children:
                comment = item.get("data", {})
                result = {
                    "source_review_id": comment.get("id", ""),
                    "author": comment.get("author", "[deleted]"),
                    "review_text": comment.get("body", ""),
                    "review_title": comment.get("subject", "Reddit Discussion"),
                    "posted_at": comment.get("created_utc"),
                    "helpful_count": comment.get("score", 0),
                    "url": f"https://reddit.com{comment.get('permalink', '')}"
                }
                results.append(result)

        except Exception as e:
            logger.error(f"Error parsing Reddit results: {e}")

        return results
