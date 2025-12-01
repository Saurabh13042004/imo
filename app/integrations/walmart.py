"""Walmart integration using RapidAPI."""

import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

WALMART_BASE_URL = "https://walmart-api.p.rapidapi.com/v3/products"


class WalmartClient:
    """Client for Walmart API integration."""

    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY
        self.base_url = WALMART_BASE_URL
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "walmart-api.p.rapidapi.com"
        }

    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for products on Walmart."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return []

        try:
            params = {
                "query": query,
                "limit": limit
            }

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(self.base_url, params=params, headers=self.headers)
                response.raise_for_status()

            data = response.json()
            products = self._parse_search_results(data, query)
            logger.info(f"Found {len(products)} products on Walmart for query: {query}")
            return products

        except Exception as e:
            logger.error(f"Error searching Walmart: {e}")
            return []

    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information from Walmart."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return None

        try:
            url = f"{self.base_url}/{product_id}"

            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

            data = response.json()
            product = self._parse_product_details(data)
            logger.info(f"Fetched product details for Walmart ID: {product_id}")
            return product

        except Exception as e:
            logger.error(f"Error getting Walmart product details: {e}")
            return None

    def _parse_search_results(self, data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Parse search results from Walmart API response."""
        products = []
        try:
            items = data.get("items", [])
            for item in items:
                product = {
                    "title": item.get("name", ""),
                    "source_id": item.get("product_id", item.get("id", "")),
                    "url": item.get("link", ""),
                    "image_url": item.get("image", item.get("thumbnail", "")),
                    "price": float(item.get("price", 0)) if item.get("price") else None,
                    "rating": float(item.get("rating", 0)) if item.get("rating") else None,
                    "review_count": int(item.get("review_count", 0)) if item.get("review_count") else 0,
                    "brand": item.get("brand", ""),
                    "availability": item.get("availability", "In Stock")
                }
                products.append(product)
        except Exception as e:
            logger.error(f"Error parsing Walmart search results: {e}")
        return products

    def _parse_product_details(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse product details from Walmart API response."""
        try:
            return {
                "title": data.get("name", ""),
                "source_id": data.get("product_id", data.get("id", "")),
                "description": data.get("description", ""),
                "price": float(data.get("price", 0)) if data.get("price") else None,
                "rating": float(data.get("rating", 0)) if data.get("rating") else None,
                "review_count": int(data.get("review_count", 0)) if data.get("review_count") else 0,
                "brand": data.get("brand", ""),
                "category": data.get("category", ""),
                "image_url": data.get("image", ""),
                "url": data.get("link", ""),
                "availability": data.get("availability", "In Stock")
            }
        except Exception as e:
            logger.error(f"Error parsing Walmart product details: {e}")
            return None
