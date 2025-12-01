"""Search service for product aggregation."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from app.models import Product
from app.schemas import SearchRequest, ProductResponse
from app.integrations.amazon import AmazonClient
from app.integrations.walmart import WalmartClient
from app.integrations.google_shopping import GoogleShoppingClient
from app.services.cache_service import CacheService
from app.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching products across multiple sources."""

    def __init__(self):
        self.amazon_client = AmazonClient()
        self.walmart_client = WalmartClient()
        self.google_client = GoogleShoppingClient()
        self.cache_service = CacheService()

    async def search_all_sources(
        self,
        db: AsyncSession,
        search_request: SearchRequest,
        use_cache: bool = True
    ) -> List[ProductResponse]:
        """Search all enabled sources in parallel."""
        try:
            results = []
            tasks = []

            # Create search tasks for each source
            for source in search_request.sources:
                task = self._search_source(db, source, search_request, use_cache)
                tasks.append(task)

            # Execute all searches in parallel
            source_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate results
            for source_result in source_results:
                if isinstance(source_result, Exception):
                    logger.error(f"Search error: {source_result}")
                    continue
                if source_result:
                    results.extend(source_result)

            # Apply filters
            filtered_results = await self._apply_filters(results, search_request)

            logger.info(f"Search completed: {len(filtered_results)} results for query: {search_request.query}")
            return filtered_results

        except Exception as e:
            logger.error(f"Error in search_all_sources: {e}")
            return []

    async def _search_source(
        self,
        db: AsyncSession,
        source: str,
        search_request: SearchRequest,
        use_cache: bool
    ) -> List[ProductResponse]:
        """Search a specific source."""
        try:
            # Check cache first
            if use_cache:
                cached_results = await self.cache_service.get_cache(
                    db, search_request.query, source
                )
                if cached_results:
                    return [ProductResponse(**item) for item in cached_results]

            # Search based on source
            if source.lower() == "amazon":
                results = await self.amazon_client.search(search_request.query, search_request.limit)
            elif source.lower() == "walmart":
                results = await self.walmart_client.search(search_request.query, search_request.limit)
            elif source.lower() == "google_shopping":
                results = await self.google_client.search(search_request.query, search_request.limit)
            else:
                logger.warning(f"Unknown source: {source}")
                return []

            # Save results to database
            product_responses = []
            for result in results:
                product = await self._save_product(db, result, source)
                product_responses.append(ProductResponse.from_orm(product))

            # Cache results
            await self.cache_service.set_cache(
                db,
                search_request.query,
                source,
                [item.dict() for item in product_responses],
                settings.SEARCH_CACHE_TTL
            )

            return product_responses

        except Exception as e:
            logger.error(f"Error searching {source}: {e}")
            return []

    async def _save_product(self, db: AsyncSession, product_data: Dict[str, Any], source: str) -> Product:
        """Save or update product in database."""
        try:
            # Check if product exists
            result = await db.execute(
                select(Product).where(
                    and_(
                        Product.source == source,
                        Product.source_id == product_data.get("source_id")
                    )
                )
            )
            product = result.scalar_one_or_none()

            if product:
                # Update existing product
                for key, value in product_data.items():
                    if hasattr(product, key):
                        setattr(product, key, value)
            else:
                # Create new product
                product = Product(
                    source=source,
                    **product_data
                )
                db.add(product)

            await db.flush()
            await db.commit()
            return product

        except Exception as e:
            logger.error(f"Error saving product: {e}")
            try:
                await db.rollback()
            except:
                pass
            raise

    async def _apply_filters(
        self,
        results: List[ProductResponse],
        search_request: SearchRequest
    ) -> List[ProductResponse]:
        """Apply filters to search results."""
        filtered = results

        # Filter by minimum rating
        if search_request.min_rating:
            filtered = [
                p for p in filtered
                if p.rating and p.rating >= search_request.min_rating
            ]

        # Filter by maximum price
        if search_request.max_price:
            filtered = [
                p for p in filtered
                if p.price and p.price <= search_request.max_price
            ]

        # Limit results
        return filtered[:search_request.limit]

    async def get_product_by_id(self, db: AsyncSession, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        try:
            result = await db.execute(
                select(Product).where(Product.id == product_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return None

    async def get_product_by_source(
        self,
        db: AsyncSession,
        source: str,
        source_id: str
    ) -> Optional[Product]:
        """Get product by source and source_id."""
        try:
            result = await db.execute(
                select(Product).where(
                    and_(
                        Product.source == source,
                        Product.source_id == source_id
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting product by source: {e}")
            return None
