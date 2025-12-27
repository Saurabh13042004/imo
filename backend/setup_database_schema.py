"""
Database schema setup script - Creates tables and alters columns as needed.
Idempotent: Safe to run multiple times without errors.
"""

import asyncio
import logging
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages database schema creation and alterations."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,
        )
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def execute_sql(self, sql: str, description: str = None) -> bool:
        """Execute SQL statement safely."""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text(sql))
            logger.info(f"✓ {description or 'Command executed successfully'}")
            return True
        except Exception as e:
            logger.warning(f"⚠ {description or 'Command failed'}: {str(e)}")
            return False

    async def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    )
                """))
                return result.scalar()
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False

    async def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if column exists in table."""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = '{table_name}' AND column_name = '{column_name}'
                    )
                """))
                return result.scalar()
        except Exception as e:
            logger.error(f"Error checking column existence: {e}")
            return False

    async def get_column_type(self, table_name: str, column_name: str) -> str:
        """Get the data type of a column."""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(f"""
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = '{column_name}'
                """))
                row = result.scalar()
                return row if row else None
        except Exception as e:
            logger.error(f"Error getting column type: {e}")
            return None

    async def setup_schema(self):
        """Setup all tables and columns."""
        logger.info("=" * 70)
        logger.info("Starting Database Schema Setup")
        logger.info("=" * 70)

        # Define table schemas
        tables = {
            'affiliate_clicks': """
                CREATE TABLE IF NOT EXISTS public.affiliate_clicks (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    product_id uuid NOT NULL,
                    timestamp timestamp with time zone NOT NULL DEFAULT now(),
                    subscription_status character varying,
                    conversion_value numeric,
                    session_id character varying,
                    CONSTRAINT affiliate_clicks_pkey PRIMARY KEY (id),
                    CONSTRAINT affiliate_clicks_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'analytics_events': """
                CREATE TABLE IF NOT EXISTS public.analytics_events (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid,
                    event_name character varying NOT NULL,
                    event_data jsonb,
                    timestamp timestamp with time zone NOT NULL DEFAULT now(),
                    session_id character varying,
                    user_agent character varying,
                    ip_address inet,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT analytics_events_pkey PRIMARY KEY (id)
                )
            """,
            'app_config': """
                CREATE TABLE IF NOT EXISTS public.app_config (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    config_key character varying NOT NULL,
                    config_value jsonb NOT NULL,
                    description character varying,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT app_config_pkey PRIMARY KEY (id)
                )
            """,
            'background_analysis_tasks': """
                CREATE TABLE IF NOT EXISTS public.background_analysis_tasks (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    query_hash character varying NOT NULL,
                    page integer NOT NULL,
                    status character varying NOT NULL,
                    products_analyzed integer,
                    total_products integer,
                    started_at timestamp with time zone NOT NULL DEFAULT now(),
                    completed_at timestamp with time zone,
                    heartbeat_at timestamp with time zone NOT NULL DEFAULT now(),
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT background_analysis_tasks_pkey PRIMARY KEY (id)
                )
            """,
            'comments': """
                CREATE TABLE IF NOT EXISTS public.comments (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    review_id uuid NOT NULL,
                    content character varying NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT comments_pkey PRIMARY KEY (id),
                    CONSTRAINT comments_review_id_fkey FOREIGN KEY (review_id) REFERENCES public.user_reviews(id)
                )
            """,
            'contacts': """
                CREATE TABLE IF NOT EXISTS public.contacts (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    name character varying NOT NULL,
                    email character varying NOT NULL,
                    subject character varying NOT NULL,
                    message text NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone DEFAULT now(),
                    CONSTRAINT contacts_pkey PRIMARY KEY (id)
                )
            """,
            'daily_search_usage': """
                CREATE TABLE IF NOT EXISTS public.daily_search_usage (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid,
                    session_id character varying,
                    search_date date NOT NULL,
                    search_count integer NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT daily_search_usage_pkey PRIMARY KEY (id),
                    CONSTRAINT daily_search_usage_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
                )
            """,
            'error_logs': """
                CREATE TABLE IF NOT EXISTS public.error_logs (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    function_name character varying NOT NULL,
                    error_type character varying NOT NULL,
                    error_message character varying NOT NULL,
                    error_details jsonb,
                    query_context character varying,
                    user_id uuid,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT error_logs_pkey PRIMARY KEY (id)
                )
            """,
            'likes': """
                CREATE TABLE IF NOT EXISTS public.likes (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    review_id uuid NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT likes_pkey PRIMARY KEY (id),
                    CONSTRAINT likes_review_id_fkey FOREIGN KEY (review_id) REFERENCES public.user_reviews(id)
                )
            """,
            'payment_transactions': """
                CREATE TABLE IF NOT EXISTS public.payment_transactions (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    transaction_id character varying NOT NULL UNIQUE,
                    amount numeric NOT NULL,
                    type character varying NOT NULL,
                    status character varying NOT NULL,
                    stripe_session_id character varying,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    subscription_id uuid,
                    currency character varying DEFAULT 'usd'::character varying,
                    stripe_payment_intent_id character varying UNIQUE,
                    metadata_json character varying,
                    CONSTRAINT payment_transactions_pkey PRIMARY KEY (id),
                    CONSTRAINT payment_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id),
                    CONSTRAINT fk_payment_transactions_subscription_id FOREIGN KEY (subscription_id) REFERENCES public.subscriptions(id)
                )
            """,
            'price_alerts': """
                CREATE TABLE IF NOT EXISTS public.price_alerts (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid,
                    product_id character varying NOT NULL,
                    product_name character varying NOT NULL,
                    product_url character varying NOT NULL,
                    target_price numeric NOT NULL,
                    current_price numeric,
                    currency character varying,
                    email character varying NOT NULL,
                    is_active boolean NOT NULL,
                    alert_sent boolean NOT NULL,
                    alert_sent_at timestamp with time zone,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT price_alerts_pkey PRIMARY KEY (id),
                    CONSTRAINT price_alerts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
                )
            """,
            'price_comparisons': """
                CREATE TABLE IF NOT EXISTS public.price_comparisons (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    product_id uuid NOT NULL,
                    retailer character varying NOT NULL,
                    price numeric NOT NULL,
                    url character varying,
                    availability character varying,
                    shipping character varying,
                    fetched_at timestamp with time zone DEFAULT now(),
                    CONSTRAINT price_comparisons_pkey PRIMARY KEY (id),
                    CONSTRAINT price_comparisons_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'product_likes': """
                CREATE TABLE IF NOT EXISTS public.product_likes (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    product_id uuid NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT product_likes_pkey PRIMARY KEY (id),
                    CONSTRAINT product_likes_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'product_reviews': """
                CREATE TABLE IF NOT EXISTS public.product_reviews (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    product_id uuid NOT NULL,
                    external_review_id character varying NOT NULL UNIQUE,
                    reviewer_name character varying,
                    rating integer NOT NULL,
                    title character varying,
                    review_text character varying,
                    verified_purchase boolean,
                    review_date timestamp with time zone,
                    positive_feedback integer,
                    negative_feedback integer,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    source character varying,
                    CONSTRAINT product_reviews_pkey PRIMARY KEY (id),
                    CONSTRAINT product_reviews_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'products': """
                CREATE TABLE IF NOT EXISTS public.products (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    title character varying NOT NULL,
                    source character varying NOT NULL,
                    source_id character varying NOT NULL,
                    asin character varying,
                    url text,
                    image_url text,
                    price numeric,
                    currency character varying,
                    rating numeric,
                    review_count integer,
                    description text,
                    description_source character varying,
                    description_quality_score integer,
                    description_fetched_at timestamp with time zone,
                    brand character varying,
                    category character varying,
                    availability character varying,
                    is_detailed_fetched boolean,
                    reviews_summary text,
                    immersive_product_page_token text,
                    immersive_product_api_link text,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT products_pkey PRIMARY KEY (id),
                    CONSTRAINT products_source_id_key UNIQUE (source, source_id)
                )
            """,
            'profiles': """
                CREATE TABLE IF NOT EXISTS public.profiles (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    email character varying UNIQUE,
                    full_name character varying,
                    avatar_url character varying,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    subscription_tier character varying DEFAULT 'free'::character varying,
                    access_level character varying DEFAULT 'basic'::character varying,
                    password_hash character varying,
                    oauth_provider character varying,
                    oauth_provider_id character varying,
                    CONSTRAINT profiles_pkey PRIMARY KEY (id)
                )
            """,
            'reviews': """
                CREATE TABLE IF NOT EXISTS public.reviews (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    product_id uuid NOT NULL,
                    source character varying NOT NULL,
                    source_review_id character varying,
                    author character varying,
                    rating numeric,
                    review_text text,
                    review_title character varying,
                    verified_purchase boolean,
                    helpful_count integer,
                    image_urls TEXT[],
                    posted_at timestamp with time zone,
                    fetched_at timestamp with time zone NOT NULL DEFAULT now(),
                    sentiment character varying,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT reviews_pkey PRIMARY KEY (id),
                    CONSTRAINT reviews_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'search_cache': """
                CREATE TABLE IF NOT EXISTS public.search_cache (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    query character varying NOT NULL,
                    source character varying NOT NULL,
                    result_data jsonb,
                    cached_at timestamp with time zone NOT NULL DEFAULT now(),
                    expires_at timestamp with time zone,
                    CONSTRAINT search_cache_pkey PRIMARY KEY (id)
                )
            """,
            'search_unlocks': """
                CREATE TABLE IF NOT EXISTS public.search_unlocks (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    search_query character varying NOT NULL,
                    unlock_date timestamp with time zone NOT NULL DEFAULT now(),
                    payment_amount numeric NOT NULL,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT search_unlocks_pkey PRIMARY KEY (id),
                    CONSTRAINT search_unlocks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
                )
            """,
            'short_video_reviews': """
                CREATE TABLE IF NOT EXISTS public.short_video_reviews (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    product_id uuid NOT NULL,
                    platform character varying NOT NULL,
                    video_url character varying NOT NULL,
                    thumbnail_url character varying,
                    creator character varying NOT NULL,
                    caption character varying,
                    likes integer,
                    views integer,
                    duration integer,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT short_video_reviews_pkey PRIMARY KEY (id),
                    CONSTRAINT short_video_reviews_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'subscription_events': """
                CREATE TABLE IF NOT EXISTS public.subscription_events (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid,
                    event_type character varying NOT NULL,
                    event_data jsonb,
                    session_id character varying,
                    user_agent character varying,
                    ip_address character varying,
                    referrer character varying,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT subscription_events_pkey PRIMARY KEY (id)
                )
            """,
            'subscriptions': """
                CREATE TABLE IF NOT EXISTS public.subscriptions (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    plan_type character varying NOT NULL DEFAULT 'free'::character varying,
                    is_active boolean NOT NULL DEFAULT false,
                    subscription_end timestamp with time zone,
                    stripe_customer_id character varying,
                    stripe_subscription_id character varying UNIQUE,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    trial_end timestamp with time zone,
                    billing_cycle character varying,
                    subscription_start timestamp with time zone,
                    trial_start timestamp with time zone,
                    stripe_product_id character varying,
                    CONSTRAINT subscriptions_pkey PRIMARY KEY (id),
                    CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id)
                )
            """,
            'usage_logs': """
                CREATE TABLE IF NOT EXISTS public.usage_logs (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    type character varying NOT NULL,
                    count integer,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT usage_logs_pkey PRIMARY KEY (id)
                )
            """,
            'user_interactions': """
                CREATE TABLE IF NOT EXISTS public.user_interactions (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid,
                    interaction_type character varying NOT NULL,
                    content_type character varying,
                    content_id character varying,
                    interaction_data jsonb,
                    session_id character varying,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT user_interactions_pkey PRIMARY KEY (id)
                )
            """,
            'user_reviews': """
                CREATE TABLE IF NOT EXISTS public.user_reviews (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    product_id uuid NOT NULL,
                    video_url character varying,
                    title character varying NOT NULL,
                    description character varying,
                    rating integer NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    status character varying NOT NULL DEFAULT 'pending'::character varying,
                    s3_key character varying,
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT user_reviews_pkey PRIMARY KEY (id),
                    CONSTRAINT user_reviews_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'user_roles': """
                CREATE TABLE IF NOT EXISTS public.user_roles (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    user_id uuid NOT NULL,
                    role character varying NOT NULL,
                    created_at timestamp with time zone DEFAULT now(),
                    CONSTRAINT user_roles_pkey PRIMARY KEY (id)
                )
            """,
            'videos': """
                CREATE TABLE IF NOT EXISTS public.videos (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    product_id uuid NOT NULL,
                    video_id character varying NOT NULL,
                    title character varying,
                    channel_name character varying,
                    channel_id character varying,
                    thumbnail_url text,
                    duration integer,
                    view_count bigint,
                    like_count integer,
                    published_at timestamp with time zone,
                    description text,
                    video_url text,
                    fetched_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT videos_pkey PRIMARY KEY (id),
                    CONSTRAINT videos_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id)
                )
            """,
            'ai_verdicts': """
                CREATE TABLE IF NOT EXISTS public.ai_verdicts (
                    id uuid NOT NULL DEFAULT gen_random_uuid(),
                    product_id uuid NOT NULL,
                    imo_score numeric NOT NULL,
                    summary text NOT NULL,
                    pros jsonb DEFAULT '[]'::jsonb,
                    cons jsonb DEFAULT '[]'::jsonb,
                    who_should_buy text,
                    who_should_avoid text,
                    deal_breakers jsonb DEFAULT '[]'::jsonb,
                    verdict_type character varying DEFAULT 'product'::character varying,
                    created_at timestamp with time zone NOT NULL DEFAULT now(),
                    updated_at timestamp with time zone NOT NULL DEFAULT now(),
                    CONSTRAINT ai_verdicts_pkey PRIMARY KEY (id)
                )
            """,
        }

        # Create all tables
        logger.info("\nCreating tables...")
        for table_name, create_sql in tables.items():
            await self.execute_sql(create_sql, f"Table '{table_name}'")

        # Create indexes
        logger.info("\nCreating indexes...")
        indexes = {
            'idx_products_source': 'CREATE INDEX IF NOT EXISTS idx_products_source ON public.products(source)',
            'idx_reviews_product_id': 'CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON public.reviews(product_id)',
            'idx_profiles_email': 'CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email)',
            'idx_subscriptions_user_id': 'CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id)',
            'idx_payment_transactions_user_id': 'CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON public.payment_transactions(user_id)',
            'idx_analytics_user_id': 'CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON public.analytics_events(user_id)',
            'idx_error_logs_created': 'CREATE INDEX IF NOT EXISTS idx_error_logs_created ON public.error_logs(created_at)',
            'idx_search_cache_query': 'CREATE INDEX IF NOT EXISTS idx_search_cache_query ON public.search_cache(query)',
        }

        for index_name, create_index_sql in indexes.items():
            await self.execute_sql(create_index_sql, f"Index '{index_name}'")

        logger.info("\n" + "=" * 70)
        logger.info("Database Schema Setup Complete!")
        logger.info("=" * 70)

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()


async def main():
    """Main entry point."""
    manager = SchemaManager(settings.DATABASE_URL)
    try:
        await manager.setup_schema()
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())
