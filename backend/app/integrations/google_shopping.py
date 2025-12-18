"""Google Shopping integration using SerpAPI."""

import logging
import re
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
import json

from app.utils.geo import get_country_config, log_serpapi_params

logger = logging.getLogger(__name__)


class GoogleShoppingClient:
    """Client for Google Shopping integration using SerpAPI."""

    def __init__(self, api_key: str):
        """Initialize with SerpAPI key.
        
        Args:
            api_key: SerpAPI API key
        """
        self.api_key = api_key
        GoogleSearch.SERP_API_KEY = api_key

    def search(
        self, 
        query: str, 
        limit: int = 100,
        location: Optional[str] = None,
        country: Optional[str] = None,
        language: str = "en",
        timeout: int = 5
    ) -> List[Dict[str, Any]]:
        """Search Google Shopping and return results.
        
        Args:
            query: Search keyword
            limit: Maximum results to return
            location: Location string (e.g., "Bengaluru,India" or "India")
            country: Country name for geo-targeting (used if location not provided)
            language: Language code (default "en")
            timeout: Request timeout in seconds
            
        Returns:
            List of product results
        """
        try:
            # If location not provided, use country
            if not location and country:
                location = country
            elif not location:
                location = "United States"
            
            # Get geo config for the location
            geo_config = get_country_config(country or "United States")
            
            # Build SerpAPI parameters
            params = {
                "engine": "google_shopping",  # Explicit engine
                "q": query,
                "num": min(limit, 100),  # max 100 per request
                "api_key": self.api_key,
                "location": location,
                "gl": geo_config["gl"],
                "hl": language,
                "google_domain": geo_config["google_domain"],
            }

            # Log the exact SerpAPI request being made
            log_serpapi_params(
                keyword=query,
                location=location,
                gl=geo_config["gl"],
                hl=language,
                google_domain=geo_config["google_domain"]
            )

            logger.info(
                f"[GoogleShoppingClient] Executing search with params:\\n"
                f"  Params: {json.dumps({k: v for k, v in params.items() if k != 'api_key'}, indent=2)}"
            )

            search = GoogleSearch(params)
            results = search.get_dict()

            if "error" in results:
                logger.error(f"[SerpAPI] Google Shopping API error: {results.get('error')}")
                return []

            # Extract shopping results
            shopping_results = results.get("shopping_results", [])
            
            logger.info(
                f"[SerpAPI Response] Status: Success | Results: {len(shopping_results)} | "
                f"Query: {query} | Location: {location} | Country: {country}"
            )
            
            if not shopping_results:
                logger.warning(f"[SerpAPI] No shopping_results found for query: {query} at location: {location}")
                return []
            
            # Transform results
            transformed = []
            for result in shopping_results:
                if result:
                    try:
                        transformed_result = self.transform_result(result)
                        if transformed_result:  # Only add if transformation was successful
                            transformed.append(transformed_result)
                    except Exception as e:
                        logger.debug(f"Skipping result due to transformation error: {e}")
                        continue
            
            logger.info(f"Retrieved {len(transformed)} results from Google Shopping for: {query}")
            return transformed

        except Exception as e:
            logger.error(f"Error searching Google Shopping: {e}", exc_info=True)
            return []

    @staticmethod
    def transform_result(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform Google Shopping result to standard format.
        
        Args:
            result: Raw Google Shopping result from shopping_results array
            
        Returns:
            Standardized product result or None if transformation fails
        """
        try:
            # Extract title
            title = result.get("title", "")
            if not title:
                logger.debug("Skipping result with no title")
                return None
            
            # Extract and parse price
            price = GoogleShoppingClient._parse_price(result.get("extracted_price", result.get("price", "")))
            
            # Extract rating and reviews
            rating = GoogleShoppingClient._parse_rating(result.get("rating"))
            review_count = GoogleShoppingClient._parse_review_count(result.get("reviews"))
            
            # Extract source (retailer name) - this is the actual store selling the product
            # e.g., "Walmart", "Best Buy", "Target", "Staples", "Office Depot"
            retailer_name = result.get("source", "Unknown Retailer")
            
            # Extract product link
            link = result.get("product_link", result.get("link", ""))
            
            # Extract thumbnail/image
            image_url = result.get("thumbnail", result.get("serpapi_thumbnail", ""))
            
            # Extract product ID
            product_id = result.get("product_id", "")
            
            # Extract immersive product page token (for detailed product info)
            immersive_product_page_token = result.get("immersive_product_page_token", "")
            
            # Extract immersive product API link (direct link to detailed product data)
            immersive_product_api_link = result.get("serpapi_immersive_product_api", "")
            
            transformed = {
                "title": title,
                "source": retailer_name,  # Use retailer name as source (e.g., "Walmart", "Best Buy")
                "source_id": product_id,
                "url": link,
                "image_url": image_url,
                "price": price,
                "currency": "USD",
                "rating": rating,
                "review_count": review_count or 0,
                "brand": "",
                "manufacturer": retailer_name,
                "description": title,
                "category": "",
                "asin": "",
                "availability": "In Stock",
                "position": result.get("position", 0),
                "product_id": product_id,
                "api_source": "google_shopping",  # Track which API provided this result
                "retailer": retailer_name,  # Store retailer info explicitly
                # Immersive product data for detailed product information
                "immersive_product_page_token": immersive_product_page_token,
                "immersive_product_api_link": immersive_product_api_link,
            }
            return transformed
        except Exception as e:
            logger.error(f"Error transforming Google Shopping result: {e}")
            return None

    def get_immersive_product_data(self, product_title: str, source: str) -> Optional[str]:
        """Fetch immersive product API link for products that don't have it.
        
        For retailers like Best Buy, Walmart, etc., SerpAPI might not return the
        immersive_product_api link directly. This method tries to fetch it by
        doing a product-specific search.
        
        Args:
            product_title: The product title
            source: The retailer/source name
            
        Returns:
            The immersive product API link or None
        """
        try:
            # Build a specific search query for the product + retailer
            search_query = f"{product_title} {source}"
            
            params = {
                "q": search_query,
                "tbm": "shop",
                "num": 10,
                "api_key": self.api_key,
            }
            
            results = GoogleSearch(params).get_dict()
            shopping_results = results.get("shopping_results", [])
            
            # Look for a matching product and extract immersive link
            for result in shopping_results:
                result_source = result.get("source", "").lower()
                if source.lower() in result_source or result_source in source.lower():
                    immersive_link = result.get("serpapi_immersive_product_api", "")
                    if immersive_link:
                        logger.info(f"Found immersive API link for {product_title} from {source}")
                        return immersive_link
            
            logger.debug(f"No immersive API link found for {product_title} from {source}")
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching immersive product data: {e}")
            return None

    @staticmethod
    def _parse_price(price_value: Any) -> Optional[float]:
        """Parse price from string or numeric value.
        
        Handles multiple formats:
        - Direct float/int: 99.99, 100
        - String with currency: "$99.99", "€99,99"
        - Already extracted: extracted_price field
        """
        try:
            if price_value is None or price_value == "":
                return None
            
            # If already numeric, return as float
            if isinstance(price_value, (int, float)):
                return float(price_value) if price_value > 0 else None
            
            # Convert to string and clean
            price_str = str(price_value)
            # Remove currency symbols and commas
            price = price_str.replace("$", "").replace("€", "").replace(",", "").strip()
            
            # Handle "price - price" ranges (take first price)
            if " - " in price:
                price = price.split(" - ")[0].strip()
            
            float_price = float(price)
            return float_price if float_price > 0 else None
        except (ValueError, AttributeError, TypeError):
            return None

    @staticmethod
    def _parse_rating(rating_value: Any) -> Optional[float]:
        """Parse rating from various formats.
        
        Handles:
        - Direct float/int: 4.5
        - String: "4.5", "4.5 out of 5"
        """
        try:
            if rating_value is None or rating_value == "":
                return None
            
            # If already numeric, return as float
            if isinstance(rating_value, (int, float)):
                rating_float = float(rating_value)
                return rating_float if 0 <= rating_float <= 5 else None
            
            # Convert to string and extract first number
            rating_str = str(rating_value)
            rating = rating_str.split()[0]
            rating_float = float(rating)
            return rating_float if 0 <= rating_float <= 5 else None
        except (ValueError, IndexError, AttributeError, TypeError):
            return None

    @staticmethod
    def _parse_review_count(reviews_value: Any) -> int:
        """Parse review count from various formats.
        
        Handles:
        - Direct int: 123
        - String: "123", "1,234", "(123)"
        """
        try:
            if reviews_value is None or reviews_value == "":
                return 0
            
            # If already numeric, return as int
            if isinstance(reviews_value, (int, float)):
                count = int(reviews_value)
                return count if count >= 0 else 0
            
            # Convert to string and extract numbers
            reviews_str = str(reviews_value)
            matches = re.findall(r'\d+', reviews_str.replace(",", ""))
            return int(matches[0]) if matches else 0
        except (ValueError, IndexError, TypeError):
            return 0

    async def _parse_search_results(self, data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Legacy method for compatibility."""
        shopping_results = data.get("shopping_results", [])
        return [self.transform_result(r) for r in shopping_results if r]
