"""Amazon integration using RapidAPI."""

import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

AMAZON_BASE_URL = "https://amazon-data-scraper-api3.p.rapidapi.com/queries"


class AmazonClient:
    """Client for Amazon API integration."""

    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY
        self.base_url = AMAZON_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "amazon-data-scraper-api3.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }

    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for products on Amazon."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return []

        try:
            payload = {
                "source": "amazon_search",
                "query": query,
                "geo_location": "60607",
                "domain": "com",
                "parse": True,
                "limit": limit
            }

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.post(self.base_url, json=payload, headers=self.headers)
                response.raise_for_status()

            data = response.json()
            products = self._parse_search_results(data, query)
            logger.info(f"Found {len(products)} products on Amazon for query: {query}")
            return products

        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return []

    async def get_product_details(self, asin: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information from Amazon."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return None

        try:
            payload = {
                "source": "amazon_product",
                "asin": asin,
                "domain": "com",
                "parse": True
            }

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.post(self.base_url, json=payload, headers=self.headers)
                response.raise_for_status()

            data = response.json()
            product = self._parse_product_details(data)
            logger.info(f"Fetched product details for ASIN: {asin}")
            return product

        except Exception as e:
            logger.error(f"Error getting Amazon product details: {e}")
            return None

    async def get_reviews(self, asin: str, page: int = 1) -> List[Dict[str, Any]]:
        """Get product reviews from Amazon."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return []

        try:
            payload = {
                "source": "amazon_reviews",
                "asin": asin,
                "domain": "com",
                "parse": True,
                "page": page
            }

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.post(self.base_url, json=payload, headers=self.headers)
                response.raise_for_status()

            data = response.json()
            reviews = self._parse_reviews(data)
            logger.info(f"Fetched {len(reviews)} reviews for ASIN: {asin}")
            return reviews

        except Exception as e:
            logger.error(f"Error getting Amazon reviews: {e}")
            return []

    def _parse_search_results(self, data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Parse search results from Amazon API response."""
        products = []
        try:
            results = data.get("results", [])
            for item in results:
                product = {
                    "title": item.get("title", ""),
                    "source_id": item.get("asin", ""),
                    "asin": item.get("asin", ""),
                    "url": item.get("url", ""),
                    "image_url": item.get("image", ""),
                    "price": float(item.get("price", 0)) if item.get("price") else None,
                    "rating": float(item.get("rating", 0)) if item.get("rating") else None,
                    "review_count": int(item.get("review_count", 0)) if item.get("review_count") else 0,
                    "brand": item.get("brand", ""),
                    "availability": item.get("availability", "")
                }
                products.append(product)
        except Exception as e:
            logger.error(f"Error parsing Amazon search results: {e}")
        return products

    def _parse_product_details(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse product details from Amazon API response."""
        try:
            item = data.get("results", {}).get(0) if isinstance(data.get("results"), list) else data.get("results", {})
            if not item:
                return None

            return {
                "title": item.get("title", ""),
                "source_id": item.get("asin", ""),
                "asin": item.get("asin", ""),
                "description": item.get("description", ""),
                "price": float(item.get("price", 0)) if item.get("price") else None,
                "rating": float(item.get("rating", 0)) if item.get("rating") else None,
                "review_count": int(item.get("review_count", 0)) if item.get("review_count") else 0,
                "brand": item.get("brand", ""),
                "category": item.get("category", ""),
                "image_url": item.get("image", ""),
                "url": item.get("url", ""),
                "availability": item.get("availability", "")
            }
        except Exception as e:
            logger.error(f"Error parsing Amazon product details: {e}")
            return None

    def _parse_reviews(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse reviews from Amazon API response."""
        reviews = []
        try:
            results = data.get("results", [])
            for item in results:
                review = {
                    "source_review_id": item.get("review_id", ""),
                    "author": item.get("author", ""),
                    "rating": float(item.get("rating", 0)) if item.get("rating") else None,
                    "review_title": item.get("title", ""),
                    "review_text": item.get("review_text", ""),
                    "posted_at": item.get("posted_at"),
                    "verified_purchase": item.get("verified_purchase", False),
                    "helpful_count": int(item.get("helpful_count", 0)) if item.get("helpful_count") else 0
                }
                reviews.append(review)
        except Exception as e:
            logger.error(f"Error parsing Amazon reviews: {e}")
        return reviews
