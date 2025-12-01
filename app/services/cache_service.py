"""Cache service for handling caching operations."""

import logging
import json
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models import SearchCache
from app.config import settings

logger = logging.getLogger(__name__)

# In-memory cache as fallback
_memory_cache: Dict[str, Tuple[Any, datetime]] = {}


class UUIDEncoder(json.JSONEncoder):
    """Custom JSON encoder for UUID and datetime objects."""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CacheService:
    """Service for managing cache operations."""

    @staticmethod
    async def get_cache(
        db: AsyncSession,
        query: str,
        source: str
    ) -> Optional[Any]:
        """Get cached search result."""
        try:
            result = await db.execute(
                select(SearchCache).where(
                    and_(
                        SearchCache.query == query,
                        SearchCache.source == source,
                        SearchCache.expires_at > datetime.utcnow()
                    )
                )
            )
            cache = result.scalar_one_or_none()
            if cache:
                logger.info(f"Cache hit for query: {query}, source: {source}")
                return cache.result_data
            return None
        except Exception as e:
            logger.error(f"Error retrieving cache: {e}")
            return None

    @staticmethod
    async def set_cache(
        db: AsyncSession,
        query: str,
        source: str,
        result_data: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set cache for search result (non-blocking)."""
        try:
            if ttl is None:
                ttl = settings.SEARCH_CACHE_TTL

            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            cache_key = f"{query}#{source}"

            # Convert result_data to JSON-serializable format
            try:
                serialized_data = json.loads(
                    json.dumps(result_data, cls=UUIDEncoder, default=str)
                )
            except Exception as e:
                logger.warning(f"Could not serialize result_data: {e}")
                serialized_data = result_data

            # Always store in memory cache (non-blocking)
            _memory_cache[cache_key] = (serialized_data, expires_at)
            logger.info(f"Cache set (memory) for query: {query}, source: {source}, ttl: {ttl}s")

            # Try to store in database (non-blocking - don't fail if it doesn't work)
            try:
                # Create new cache entry without reading first (simpler transaction)
                cache = SearchCache(
                    query=query,
                    source=source,
                    result_data=serialized_data,
                    expires_at=expires_at
                )
                db.add(cache)
                await db.flush()
                logger.debug(f"Cache also stored in database for: {query}, source: {source}")
            except Exception as db_error:
                logger.debug(f"Database cache storage failed (non-critical): {db_error}")
                # Don't fail the operation, memory cache is enough
                pass

            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    @staticmethod
    async def invalidate_cache(
        db: AsyncSession,
        query: Optional[str] = None,
        source: Optional[str] = None
    ) -> bool:
        """Invalidate cache entries."""
        try:
            # Clear memory cache entries matching criteria
            keys_to_delete = []
            for cache_key in _memory_cache:
                if query and source:
                    if cache_key == f"{query}#{source}":
                        keys_to_delete.append(cache_key)
                elif query:
                    if cache_key.startswith(f"{query}#"):
                        keys_to_delete.append(cache_key)
                elif source:
                    if cache_key.endswith(f"#{source}"):
                        keys_to_delete.append(cache_key)

            for key in keys_to_delete:
                del _memory_cache[key]

            logger.info(f"Cache invalidated: query={query}, source={source}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False

    @staticmethod
    async def cleanup_expired_cache(db: AsyncSession) -> int:
        """Clean up expired cache entries."""
        try:
            # Clean expired memory cache entries
            expired_keys = []
            for cache_key, (_, expires_at) in _memory_cache.items():
                if expires_at < datetime.utcnow():
                    expired_keys.append(cache_key)

            for key in expired_keys:
                del _memory_cache[key]

            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
