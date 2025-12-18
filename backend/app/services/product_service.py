"""Product service for detailed product information using cached search results."""

import logging
import httpx
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ProductResponse
from app.config import settings
from app.integrations.google_shopping import GoogleShoppingClient
from app.services.search_service import PRODUCT_CACHE, PRODUCT_BY_SOURCE

logger = logging.getLogger(__name__)


class ProductService:
    """Service for fetching detailed product information from cached search results."""

    def __init__(self):
        self.serpapi_key = settings.SERPAPI_KEY
        self.google_client = None
        if self.serpapi_key:
            self.google_client = GoogleShoppingClient(self.serpapi_key)

    async def get_product_by_id(self, db: AsyncSession, product_id: str) -> Optional[ProductResponse]:
        """Get product by UUID from search cache.
        
        Args:
            db: Database session
            product_id: Product UUID
            
        Returns:
            ProductResponse if found in cache, None otherwise
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
            db: Database session
            source: Product source (retailer name)
            source_id: Source-specific product ID
            
        Returns:
            ProductResponse if found in cache, None otherwise
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

    async def _fetch_serpapi_enrichment(
        self, 
        product_title: str,
        asin: str = "",
        location: Optional[str] = None,
        country: Optional[str] = None,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """Fetch enrichment data from SerpAPI's immersive product endpoint.
        
        Strategy:
        1. Search for product using google engine with shopping results
        2. Find matching product in immersive_products array by title containment
        3. Call google_immersive_product endpoint using serpapi_link for rich enrichment
        4. Returns: prices (stores), external reviews, content, videos
        
        Args:
            product_title: Product title to search
            asin: Optional ASIN for reference (deprecated - not used)
            location: Optional location string for location-based results
            country: Country name for geo-targeting
            language: Language code
            
        Returns:
            SerpAPI immersive product response with cross-store prices, reviews, videos, etc.
        """
        try:
            if not self.serpapi_key:
                logger.debug("SerpAPI key not configured, skipping enrichment")
                return None
            
            logger.info(
                f"[ProductService] Enrichment for product:\\n"
                f"  Title: {product_title[:60]}\\n"
                f"  Country: {country}\\n"
                f"  Location: {location}\\n"
                f"  Language: {language}"
            )
            
            from urllib.parse import urlparse, parse_qs
            from app.utils.geo import get_country_config
            
            # Determine location and country
            final_country = country or "United States"
            final_location = location or final_country
            
            # Get geo config
            geo_config = get_country_config(final_country)
            
            async with httpx.AsyncClient(timeout=20) as client:
                # STEP 1: Search for product to find in immersive_products
                logger.info(
                    f"[ProductService.Enrichment] Step 1: Initial search for product\\n"
                    f"  Location: {final_location}\\n"
                    f"  Country: {final_country}\\n"
                    f"  GL: {geo_config['gl']}\\n"
                    f"  Domain: {geo_config['google_domain']}"
                )
                search_params = {
                    "api_key": self.serpapi_key,
                    "engine": "google_shopping",
                    "q": f"{product_title}",  # Search by title
                    "location": final_location,
                    "gl": geo_config["gl"],
                    "hl": language,
                    "google_domain": geo_config["google_domain"]
                }
                
                logger.info(
                    f"[ProductService.Enrichment] Request params:\\n"
                    f"  URL: https://serpapi.com/search\\n"
                    f"  Params: {{{', '.join(f'{k}: {v}' for k, v in search_params.items() if k != 'api_key')}}}"
                )
                
                search_response = await client.get("https://serpapi.com/search", params=search_params)
                
                if search_response.status_code != 200:
                    logger.warning(f"[SerpAPI] Initial search failed: {search_response.status_code}")
                    return None
                
                search_data = search_response.json()
                
                # STEP 2: Find matching product in immersive_products by title containment
                immersive_products = search_data.get("immersive_products", [])
                if not immersive_products:
                    logger.warning("[SerpAPI] No immersive products found")
                    return None
                
                # Extract key words from Amazon title for matching
                title_words = product_title.split()[:5]  # First 5 words usually identify the product
                
                matching_product = None
                for product in immersive_products:
                    product_title_lower = product.get("title", "").lower()
                    # Check if product contains key words from title
                    if all(word.lower() in product_title_lower for word in title_words[:3]):
                        matching_product = product
                        logger.info(f"[SerpAPI] Found matching product: {product.get('title', '')[:60]}")
                        break
                
                if not matching_product:
                    logger.warning(f"[SerpAPI] No matching product found in immersive_products")
                    return None
                
                # STEP 3: Call immersive product endpoint using serpapi_link
                serpapi_link = matching_product.get("serpapi_link")
                if not serpapi_link:
                    logger.warning("[SerpAPI] No serpapi_link found in matching product")
                    return None
                
                logger.info(f"[SerpAPI] Step 2: Fetching immersive product enrichment via serpapi_link")
                
                try:
                    parsed_url = urlparse(serpapi_link)
                    query_params = parse_qs(parsed_url.query)
                    page_token = query_params.get('page_token', [None])[0]
                    
                    if not page_token:
                        logger.warning("[SerpAPI] No page_token in serpapi_link")
                        return None
                    
                    # Build proper request with decoded page_token
                    immersive_params = {
                        "api_key": self.serpapi_key,
                        "engine": "google_immersive_product",
                        "page_token": page_token
                    }
                    
                    immersive_response = await client.get("https://serpapi.com/search", params=immersive_params)
                    
                except Exception as e:
                    logger.error(f"[SerpAPI] Error parsing serpapi_link: {e}")
                    return None
                
                if immersive_response.status_code == 200:
                    immersive_data = immersive_response.json()
                    logger.info(f"[SerpAPI] Successfully fetched immersive product enrichment")
                    
                    return {
                        "immersive_product": immersive_data,
                        "product_results": immersive_data.get("product_results", {}),
                        "source": "serpapi_immersive",
                        "matched_product": matching_product,
                        "enrichment_ready": True
                    }
                else:
                    logger.warning(f"[SerpAPI] Immersive product fetch failed: {immersive_response.status_code}")
                    logger.debug(f"[SerpAPI] Response: {immersive_response.text[:200]}")
                    return None
                    
        except Exception as e:
            logger.error(f"[SerpAPI] Error fetching enrichment: {e}", exc_info=True)
            return None

    async def get_amazon_product_details(
        self,
        db: AsyncSession,
        asin: str,
        product_title: Optional[str] = None,
        product_image: Optional[str] = None,
        zipcode: Optional[str] = None
    ) -> Optional[ProductResponse]:
        """Get product details from cache by ASIN.
        
        NOTE: This is a compatibility wrapper. Products should be retrieved from
        search cache first. This returns None if product is not in cache.
        
        Args:
            db: Database session
            asin: Amazon Standard Identification Number (no longer used)
            product_title: Optional fallback title
            product_image: Optional fallback image
            zipcode: Optional location parameter
            
        Returns:
            ProductResponse from cache or None
        """
        logger.info(f"[DEPRECATED] get_amazon_product_details called for ASIN: {asin}")
        logger.info("Products should be retrieved from search results cache instead")
        
        # Try to find in cache by ASIN if it was cached
        cache_key = f"amazon:{asin}"
        product = PRODUCT_BY_SOURCE.get(cache_key)
        
        if product:
            return product
        
        logger.warning(f"Product not found for ASIN: {asin} - must use cached search results")
        return None
