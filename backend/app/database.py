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
    # async with engine.begin() as conn:
        # try:
        #     # FIX: Drop the orphaned foreign key constraint on profiles that references non-existent users table
        #     await conn.execute(text("""
        #         ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;
        #     """))
        #     logger.info("Dropped orphaned foreign key constraint on profiles")
        # except Exception as e:
        #     logger.debug(f"profiles foreign key constraint: {e}")
        
        # try:
        #     # FIX: Drop the bad user_roles_user_id_fkey that references non-existent users table
        #     # and add correct foreign key to profiles table
        #     await conn.execute(text("""
        #         ALTER TABLE user_roles DROP CONSTRAINT IF EXISTS user_roles_user_id_fkey;
        #     """))
        #     logger.info("Dropped orphaned user_roles_user_id_fkey constraint")
            
        #     # Now add the correct foreign key to profiles
        #     await conn.execute(text("""
        #         ALTER TABLE user_roles 
        #         ADD CONSTRAINT user_roles_user_id_fkey 
        #         FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
        #     """))
        #     logger.info("Added correct foreign key user_roles_user_id_fkey to profiles")
        # except Exception as e:
        #     logger.debug(f"user_roles foreign key constraint: {e}")
        
        # try:
        #     # FIX: Convert user_roles.role column from custom enum type to VARCHAR
        #     # This allows the ORM to insert string values directly
        #     await conn.execute(text("""
        #         ALTER TABLE user_roles 
        #         ALTER COLUMN role TYPE VARCHAR USING role::text;
        #     """))
        #     logger.info("Converted user_roles.role column to VARCHAR")
        # except Exception as e:
        #     logger.debug(f"user_roles.role column conversion: {e}")
        
        # try:
        #     # Check and add password_hash column
        #     await conn.execute(text("""
        #         ALTER TABLE profiles ADD COLUMN IF NOT EXISTS password_hash VARCHAR;
        #     """))
        #     logger.info("password_hash column added or already exists")
        # except Exception as e:
        #     logger.debug(f"password_hash column: {e}")
        
        # try:
        #     # Check and add oauth_provider column
        #     await conn.execute(text("""
        #         ALTER TABLE profiles ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR;
        #     """))
        #     logger.info("oauth_provider column added or already exists")
        # except Exception as e:
        #     logger.debug(f"oauth_provider column: {e}")
        
        # try:
        #     # Check and add oauth_provider_id column
        #     await conn.execute(text("""
        #         ALTER TABLE profiles ADD COLUMN IF NOT EXISTS oauth_provider_id VARCHAR;
        #     """))
        #     logger.info("oauth_provider_id column added or already exists")
        # except Exception as e:
        #     logger.debug(f"oauth_provider_id column: {e}")
        
        # # Add missing subscription columns for payment gateway
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS billing_cycle VARCHAR;
        #     """))
        #     logger.info("billing_cycle column added or already exists")
        # except Exception as e:
        #     logger.debug(f"billing_cycle column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS subscription_start TIMESTAMP WITH TIME ZONE;
        #     """))
        #     logger.info("subscription_start column added or already exists")
        # except Exception as e:
        #     logger.debug(f"subscription_start column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS trial_start TIMESTAMP WITH TIME ZONE;
        #     """))
        #     logger.info("trial_start column added or already exists")
        # except Exception as e:
        #     logger.debug(f"trial_start column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS stripe_product_id VARCHAR;
        #     """))
        #     logger.info("stripe_product_id column added or already exists")
        # except Exception as e:
        #     logger.debug(f"stripe_product_id column: {e}")
        
        # # Add missing payment_transactions columns
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE payment_transactions ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'usd';
        #     """))
        #     logger.info("currency column added or already exists")
        # except Exception as e:
        #     logger.debug(f"currency column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE payment_transactions ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR UNIQUE;
        #     """))
        #     logger.info("stripe_payment_intent_id column added or already exists")
        # except Exception as e:
        #     logger.debug(f"stripe_payment_intent_id column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE payment_transactions ADD COLUMN IF NOT EXISTS stripe_session_id VARCHAR;
        #     """))
        #     logger.info("stripe_session_id column added or already exists")
        # except Exception as e:
        #     logger.debug(f"stripe_session_id column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE payment_transactions ADD COLUMN IF NOT EXISTS metadata_json VARCHAR;
        #     """))
        #     logger.info("metadata_json column added or already exists")
        # except Exception as e:
        #     logger.debug(f"metadata_json column: {e}")
        
        # # Fix subscription_id column type in payment_transactions (UUID instead of String)
        # try:
        #     # Check if column exists and what type it is
        #     result = await conn.execute(text("""
        #         SELECT data_type 
        #         FROM information_schema.columns 
        #         WHERE table_name = 'payment_transactions' 
        #         AND column_name = 'subscription_id'
        #     """))
        #     existing_type = result.scalar_one_or_none()
            
        #     if existing_type and existing_type != 'uuid':
        #         logger.info("Fixing subscription_id column type from String to UUID...")
        #         # Drop the column and recreate as UUID
        #         await conn.execute(text("""
        #             ALTER TABLE payment_transactions DROP COLUMN IF EXISTS subscription_id CASCADE;
        #         """))
        #         await conn.execute(text("""
        #             ALTER TABLE payment_transactions ADD COLUMN subscription_id UUID;
        #         """))
        #         await conn.execute(text("""
        #             ALTER TABLE payment_transactions
        #             ADD CONSTRAINT fk_payment_transactions_subscription_id
        #             FOREIGN KEY (subscription_id) REFERENCES subscriptions(id);
        #         """))
        #         await conn.execute(text("""
        #             CREATE INDEX IF NOT EXISTS idx_payment_transactions_subscription_id 
        #             ON payment_transactions(subscription_id);
        #         """))
        #         logger.info("subscription_id column fixed as UUID with foreign key")
        #     elif not existing_type:
        #         # Column doesn't exist, add it
        #         await conn.execute(text("""
        #             ALTER TABLE payment_transactions ADD COLUMN subscription_id UUID;
        #         """))
        #         await conn.execute(text("""
        #             ALTER TABLE payment_transactions
        #             ADD CONSTRAINT fk_payment_transactions_subscription_id
        #             FOREIGN KEY (subscription_id) REFERENCES subscriptions(id);
        #         """))
        #         await conn.execute(text("""
        #             CREATE INDEX IF NOT EXISTS idx_payment_transactions_subscription_id 
        #             ON payment_transactions(subscription_id);
        #         """))
        #         logger.info("subscription_id column added as UUID")
        #     else:
        #         logger.info("subscription_id column already exists as UUID")
        # except Exception as e:
        #     logger.debug(f"subscription_id column fix: {e}")
        
        # Add missing user_reviews columns
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE user_reviews ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'pending';
        #     """))
        #     logger.info("status column added or already exists in user_reviews")
        # except Exception as e:
        #     logger.debug(f"user_reviews status column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE user_reviews ADD COLUMN IF NOT EXISTS s3_key VARCHAR;
        #     """))
        #     logger.info("s3_key column added or already exists in user_reviews")
        # except Exception as e:
        #     logger.debug(f"user_reviews s3_key column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE user_reviews ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        #     """))
        #     logger.info("updated_at column added or already exists in user_reviews")
        # except Exception as e:
        #     logger.debug(f"user_reviews updated_at column: {e}")
        
        # Add missing daily_search_usage columns if table exists
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE daily_search_usage ADD COLUMN IF NOT EXISTS search_date DATE;
        #     """))
        #     logger.info("search_date column added or already exists in daily_search_usage")
        # except Exception as e:
        #     logger.debug(f"daily_search_usage search_date column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE daily_search_usage ADD COLUMN IF NOT EXISTS search_count INTEGER DEFAULT 0;
        #     """))
        #     logger.info("search_count column added or already exists in daily_search_usage")
        # except Exception as e:
        #     logger.debug(f"daily_search_usage search_count column: {e}")
        
        # Add missing products columns
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS asin VARCHAR(20);
        #     """))
        #     logger.info("asin column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products asin column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS url TEXT;
        #     """))
        #     logger.info("url column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products url column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT;
        #     """))
        #     logger.info("image_url column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products image_url column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS price NUMERIC(10,2);
        #     """))
        #     logger.info("price column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products price column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'USD';
        #     """))
        #     logger.info("currency column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products currency column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS rating NUMERIC(3,2);
        #     """))
        #     logger.info("rating column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products rating column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;
        #     """))
        #     logger.info("review_count column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products review_count column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS description TEXT;
        #     """))
        #     logger.info("description column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products description column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS description_source VARCHAR(50);
        #     """))
        #     logger.info("description_source column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products description_source column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS description_quality_score INTEGER;
        #     """))
        #     logger.info("description_quality_score column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products description_quality_score column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS description_fetched_at TIMESTAMP WITH TIME ZONE;
        #     """))
        #     logger.info("description_fetched_at column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products description_fetched_at column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS brand VARCHAR(200);
        #     """))
        #     logger.info("brand column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products brand column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(200);
        #     """))
        #     logger.info("category column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products category column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS availability VARCHAR(50);
        #     """))
        #     logger.info("availability column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products availability column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS is_detailed_fetched BOOLEAN DEFAULT FALSE;
        #     """))
        #     logger.info("is_detailed_fetched column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products is_detailed_fetched column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS reviews_summary TEXT;
        #     """))
        #     logger.info("reviews_summary column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products reviews_summary column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS immersive_product_page_token TEXT;
        #     """))
        #     logger.info("immersive_product_page_token column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products immersive_product_page_token column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS immersive_product_api_link TEXT;
        #     """))
        #     logger.info("immersive_product_api_link column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products immersive_product_api_link column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        #     """))
        #     logger.info("created_at column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products created_at column: {e}")
        
        # try:
        #     await conn.execute(text("""
        #         ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        #     """))
        #     logger.info("updated_at column added or already exists in products")
        # except Exception as e:
        #     logger.debug(f"products updated_at column: {e}")
        
        # # Add contacts table if it doesn't exist
        # try:
        #     await conn.execute(text("""
        #         CREATE TABLE IF NOT EXISTS contacts (
        #             id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #             name VARCHAR(255) NOT NULL,
        #             email VARCHAR(255) NOT NULL,
        #             subject VARCHAR(500) NOT NULL,
        #             message TEXT NOT NULL,
        #             created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        #             updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        #         )
        #     """))
        #     # Create indexes
        #     await conn.execute(text("""
        #         CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)
        #     """))
        #     await conn.execute(text("""
        #         CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at)
        #     """))
        #     logger.info("contacts table created or already exists")
        # except Exception as e:
        #     logger.debug(f"contacts table: {e}")


async def close_db():
    """Close database connection."""
    await engine.dispose()
    logger.info("Database connection closed")
