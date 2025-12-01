"""Google Shopping integration using SERP API."""

import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SERP_API_URL = "https://google-serp-api2.p.rapidapi.com/v1/shopping"


class GoogleShoppingClient:
    """Client for Google Shopping integration."""

    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY
        self.base_url = SERP_API_URL
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "google-serp-api2.p.rapidapi.com"
        }

    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for products on Google Shopping."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return []

        try:
            params = {
                "q": query,
                "num": limit,
                "hl": "en",
                "gl": "us"
            }

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(self.base_url, params=params, headers=self.headers)
                response.raise_for_status()

            data = response.json()
            products = self._parse_search_results(data, query)
            logger.info(f"Found {len(products)} products on Google Shopping for query: {query}")
            return products

        except Exception as e:
            logger.error(f"Error searching Google Shopping: {e}")
            return []

    def _parse_search_results(self, data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Parse search results from Google Shopping API response."""
        products = []
        try:
            shopping_results = data.get("shopping_results", [])
            for item in shopping_results:
                product = {
                    "title": item.get("title", ""),
                    "source_id": item.get("product_id", item.get("link", "").split("?")[0]),
                    "url": item.get("link", ""),
                    "image_url": item.get("image", ""),
                    "price": float(item.get("price", 0)) if item.get("price") else None,
                    "rating": float(item.get("rating", 0)) if item.get("rating") else None,
                    "review_count": int(item.get("review_count", 0)) if item.get("review_count") else 0,
                    "brand": item.get("brand", ""),
                    "source": "google_shopping"
                }
                products.append(product)
        except Exception as e:
            logger.error(f"Error parsing Google Shopping results: {e}")
        return products

    async def search_reviews(self, product_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for product reviews on Google."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return []

        try:
            query = f"{product_name} review"
            params = {
                "q": query,
                "num": limit,
                "hl": "en",
                "gl": "us"
            }

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(self.base_url, params=params, headers=self.headers)
                response.raise_for_status()

            data = response.json()
            reviews = self._parse_review_results(data)
            logger.info(f"Found {len(reviews)} review results for: {product_name}")
            return reviews

        except Exception as e:
            logger.error(f"Error searching Google reviews: {e}")
            return []

    def _parse_review_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse review results from Google API."""
        reviews = []
        try:
            organic_results = data.get("organic_results", [])
            for item in organic_results:
                review = {
                    "source_review_id": item.get("position", ""),
                    "review_title": item.get("title", ""),
                    "review_text": item.get("snippet", ""),
                    "url": item.get("link", "")
                }
                reviews.append(review)
        except Exception as e:
            logger.error(f"Error parsing Google review results: {e}")
        return reviews
