"""Database connection and session management."""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=NullPool if settings.DEBUG else None,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"timeout": settings.HTTP_TIMEOUT},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
    
    # Add missing columns if they don't exist
    async with engine.begin() as conn:
        try:
            # Check and add password_hash column
            await conn.execute(text("""
                ALTER TABLE profiles ADD COLUMN IF NOT EXISTS password_hash VARCHAR;
            """))
            logger.info("password_hash column added or already exists")
        except Exception as e:
            logger.debug(f"password_hash column: {e}")
        
        try:
            # Check and add oauth_provider column
            await conn.execute(text("""
                ALTER TABLE profiles ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR;
            """))
            logger.info("oauth_provider column added or already exists")
        except Exception as e:
            logger.debug(f"oauth_provider column: {e}")
        
        try:
            # Check and add oauth_provider_id column
            await conn.execute(text("""
                ALTER TABLE profiles ADD COLUMN IF NOT EXISTS oauth_provider_id VARCHAR;
            """))
            logger.info("oauth_provider_id column added or already exists")
        except Exception as e:
            logger.debug(f"oauth_provider_id column: {e}")


async def close_db():
    """Close database connection."""
    await engine.dispose()
    logger.info("Database connection closed")
