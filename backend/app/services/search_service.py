"""Search service for product aggregation with multi-source support."""

import logging
import json
import hashlib
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

from app.schemas import SearchRequest, ProductResponse
from app.config import settings
from app.integrations.google_shopping import GoogleShoppingClient

logger = logging.getLogger(__name__)

# Thread pool for concurrent API calls
THREAD_POOL = ThreadPoolExecutor(max_workers=3, thread_name_prefix="search_")

# In-memory product cache: maps product_id -> ProductResponse
# This allows us to retrieve products by ID when user clicks on them
PRODUCT_CACHE: Dict[str, ProductResponse] = {}
PRODUCT_BY_SOURCE: Dict[str, ProductResponse] = {}  # Maps "source:source_id" -> ProductResponse


class SearchService:
    """Service for searching products with Google Shopping as canonical source."""

    def __init__(self):
        self.serpapi_key = settings.SERPAPI_KEY
        self.search_timeout = settings.SEARCH_TIMEOUT
        self.total_timeout = settings.SEARCH_TOTAL_TIMEOUT
        
        # Initialize Google Shopping client (required)
        self.google_client = None
        if self.serpapi_key:
            self.google_client = GoogleShoppingClient(self.serpapi_key)
        else:
            logger.warning("SerpAPI key not configured - Google Shopping search will not work")

    async def search_all_sources(
        self,
        db: AsyncSession,
        search_request: SearchRequest,
        use_cache: bool = True
    ) -> Tuple[List[ProductResponse], int]:
        """Search using Google Shopping as canonical source.
        
        Args:
            db: Database session
            search_request: Search request with keyword, country, city, language
            use_cache: Whether to use cache
            
        Returns:
            Tuple of (product_responses, total_count)
        """
        try:
            start_time = time.time()
            keyword = search_request.keyword.strip()
            country = search_request.country or "United States"
            city = search_request.city
            language = search_request.language or "en"
            
            # Build location string for SerpAPI
            if city:
                location = f"{city},{country}"
            else:
                location = country
            
            logger.info(
                f"[SearchService] Starting search:\\n"
                f"  Keyword: {keyword}\\n"
                f"  Country: {country}\\n"
                f"  City: {city}\\n"
                f"  Language: {language}\\n"
                f"  Location for SerpAPI: {location}"
            )
            
            if not self.google_client:
                logger.error("Google Shopping client not initialized")
                return [], 0
            
            # Search Google Shopping with proper geo parameters
            results = self._search_google_shopping(keyword, location, country, language)
            
            # Convert to ProductResponse objects
            product_responses = self._convert_to_product_responses(results)
            
            # Cache products for later retrieval
            for product in product_responses:
                PRODUCT_CACHE[str(product.id)] = product
                # Also cache by source:source_id
                if product.source_id:
                    cache_key = f"{product.source}:{product.source_id}"
                    PRODUCT_BY_SOURCE[cache_key] = product
            
            elapsed = time.time() - start_time
            logger.info(
                f"[SearchService] Search completed in {elapsed:.2f}s: "
                f"Found {len(product_responses)} unique products"
            )
            
            return product_responses, len(product_responses)

        except Exception as e:
            logger.error(f"[SearchService] Error in search_all_sources: {e}", exc_info=True)
            return [], 0

    def _search_google_shopping(
        self,
        keyword: str,
        location: str,
        country: Optional[str] = None,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Search Google Shopping with proper geo parameters.
        
        Args:
            keyword: Search keyword
            location: Location string (e.g., "India" or "Bengaluru,India")
            country: Country name for geo-targeting
            language: Language code
            
        Returns:
            List of product results from Google Shopping
        """
        try:
            logger.info(
                f"[SearchService._search] Calling GoogleShoppingClient.search with:\\n"
                f"  Keyword: {keyword}\\n"
                f"  Location: {location}\\n"
                f"  Country: {country}\\n"
                f"  Language: {language}"
            )
            results = self.google_client.search(
                query=keyword,
                limit=100,
                location=location,
                country=country,
                language=language
            )
            logger.info(f"[SearchService._search] Retrieved {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"[SearchService._search] Error: {e}", exc_info=True)
            return []

    def _convert_to_product_responses(
        self,
        results: List[Dict[str, Any]]
    ) -> List[ProductResponse]:
        """Convert Google Shopping results to ProductResponse objects.
        
        Args:
            results: List of results from Google Shopping
            
        Returns:
            List of ProductResponse objects
        """
        product_responses = []
        
        for result in results:
            try:
                # Source is retailer name from Google Shopping (Walmart, Best Buy, Amazon, etc.)
                source = result.get("source", "Google Shopping")
                
                # Extract image URL
                image_url = result.get("image_url") or result.get("url_image", "")
                
                # Extract review count and rating
                review_count = result.get("review_count") or result.get("reviews_count", 0)
                rating = result.get("rating") or result.get("rating", None)
                
                # Get immersive product data for enrichment
                immersive_api_link = result.get("immersive_product_api_link", "")
                immersive_page_token = result.get("immersive_product_page_token", "")
                
                # Try to fetch immersive link if not present
                if not immersive_api_link and self.google_client:
                    try:
                        fetched_link = self.google_client.get_immersive_product_data(
                            result.get("title", ""),
                            source
                        )
                        if fetched_link:
                            immersive_api_link = fetched_link
                            logger.debug(f"Fetched immersive link for {source} product")
                    except Exception as e:
                        logger.debug(f"Could not fetch immersive link: {e}")
                
                product_response = ProductResponse(
                    id=str(uuid4()),
                    title=result.get("title", "")[:200],
                    source=source,
                    source_id=result.get("source_id", result.get("product_id", "")),
                    asin="",  # No ASIN for non-Amazon sources
                    url=result.get("url", ""),
                    image_url=image_url,
                    price=self._parse_price(result.get("price")),
                    currency=result.get("currency", "USD"),
                    rating=self._parse_rating(rating),
                    review_count=int(review_count) if review_count else 0,
                    description=result.get("description", result.get("title", ""))[:500],
                    brand=result.get("brand", result.get("manufacturer", "")),
                    category=result.get("category", ""),
                    availability=result.get("availability", "In Stock"),
                    immersive_product_page_token=immersive_page_token,
                    immersive_product_api_link=immersive_api_link,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                product_responses.append(product_response)
            except Exception as e:
                logger.error(f"Error converting result to ProductResponse: {e}")
                continue
        
        return product_responses

    @staticmethod
    def _get_product_id(result: Dict[str, Any]) -> Optional[str]:
        """Extract unique product ID from result.
        
        Args:
            result: Product result dict
            
        Returns:
            Unique product ID or None
        """
        # Try different ID fields depending on source
        for id_field in ['source_id', 'product_id', 'asin', 'id']:
            if result.get(id_field):
                return str(result.get(id_field))
        return None

    @staticmethod
    def _hash_title(title: str) -> str:
        """Create hash of title for comparison.
        
        Args:
            title: Product title
            
        Returns:
            SHA256 hash of title
        """
        clean_title = title.lower().strip()
        return hashlib.sha256(clean_title.encode()).hexdigest()

    @staticmethod
    def _titles_similar(title1: str, title2: str, threshold: float = 0.85) -> bool:
        """Check if two titles are similar using simple similarity.
        
        Args:
            title1: First title
            title2: Second title
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if titles are similar
        """
        from difflib import SequenceMatcher
        
        ratio = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
        return ratio >= threshold

    @staticmethod
    def _parse_price(price: Any) -> Optional[float]:
        """Parse price value.
        
        Args:
            price: Price value (string, float, or int)
            
        Returns:
            Parsed price as float or None
        """
        try:
            if price is None:
                return None
            if isinstance(price, (int, float)):
                return float(price)
            if isinstance(price, str):
                # Remove currency symbols and commas
                clean = price.replace("$", "").replace(",", "").strip()
                return float(clean)
            return None
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _parse_rating(rating: Any) -> Optional[float]:
        """Parse rating value.
        
        Args:
            rating: Rating value (string, float, or int)
            
        Returns:
            Parsed rating as float or None
        """
        try:
            if rating is None:
                return None
            if isinstance(rating, (int, float)):
                return float(rating)
            if isinstance(rating, str):
                # Take first number (e.g., "4.5 out of 5" -> "4.5")
                return float(rating.split()[0])
            return None
        except (ValueError, IndexError, AttributeError):
            return None

    async def get_product_by_id(self, db: AsyncSession, product_id: str) -> Optional[ProductResponse]:
        """Get product by ID from cache.
        
        Args:
            db: Database session (for compatibility)
            product_id: UUID of the product
            
        Returns:
            ProductResponse if found, None otherwise
        """
        try:
            product = PRODUCT_CACHE.get(product_id)
            if product:
                logger.info(f"Retrieved product from cache: {product_id}")
                return product
            else:
                logger.warning(f"Product not found in cache: {product_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting product by ID: {e}")
            return None

    async def get_product_by_source(
        self,
        db: AsyncSession,
        source: str,
        source_id: str
    ) -> Optional[ProductResponse]:
        """Get product by source and source_id from cache.
        
        Args:
            db: Database session (for compatibility)
            source: Product source (e.g., "amazon", "walmart")
            source_id: Source-specific product ID
            
        Returns:
            ProductResponse if found, None otherwise
        """
        try:
            cache_key = f"{source}:{source_id}"
            product = PRODUCT_BY_SOURCE.get(cache_key)
            if product:
                logger.info(f"Retrieved product from cache: {cache_key}")
                return product
            else:
                logger.warning(f"Product not found in cache: {cache_key}")
                return None
        except Exception as e:
            logger.error(f"Error getting product by source: {e}")
            return None
