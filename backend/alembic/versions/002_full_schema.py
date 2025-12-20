"""Complete database schema with all tables.

Revision ID: 002_full_schema
Revises: 001_initial
Create Date: 2025-12-20 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_full_schema'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create app_config table
    op.create_table(
        'app_config',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('config_key', sa.String(), nullable=False),
        sa.Column('config_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_key', name='app_config_config_key_key')
    )

    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('subscription_tier', sa.String(), server_default=sa.text("'free'::text"), nullable=True),
        sa.Column('access_level', sa.String(), server_default=sa.text("'basic'::text"), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_type', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('subscription_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_subscription_id', name='subscriptions_stripe_subscription_id_key')
    )

    # Create payment_transactions table
    op.create_table(
        'payment_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default=sa.text("'pending'::text"), nullable=False),
        sa.Column('stripe_session_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id', name='payment_transactions_transaction_id_key')
    )

    # Create search_unlocks table
    op.create_table(
        'search_unlocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('search_query', sa.String(), nullable=False),
        sa.Column('unlock_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('payment_amount', sa.Numeric(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create affiliate_clicks table
    op.create_table(
        'affiliate_clicks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('subscription_status', sa.String(), server_default=sa.text("'free'::text"), nullable=True),
        sa.Column('conversion_value', sa.Numeric(), server_default=sa.text('0'), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create price_comparisons table
    op.create_table(
        'price_comparisons',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('retailer', sa.String(), nullable=False),
        sa.Column('price', sa.Numeric(), nullable=False),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('availability', sa.String(), nullable=True),
        sa.Column('shipping', sa.String(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_likes table
    op.create_table(
        'product_likes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_reviews table
    op.create_table(
        'product_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('external_review_id', sa.String(), nullable=False),
        sa.Column('reviewer_name', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('review_text', sa.String(), nullable=True),
        sa.Column('verified_purchase', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('positive_feedback', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('negative_feedback', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('source', sa.String(), server_default=sa.text("'Unknown'::text"), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_review_id', name='product_reviews_external_review_id_key')
    )

    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('video_url', sa.String(), nullable=False),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('views', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('likes', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_reviews table
    op.create_table(
        'user_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('(rating >= 1) AND (rating <= 5)', name='user_reviews_rating_check')
    )

    # Create likes table
    op.create_table(
        'likes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['review_id'], ['user_reviews.id'], name='likes_review_id_fkey')
    )

    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['review_id'], ['user_reviews.id'], name='comments_review_id_fkey')
    )

    # Create usage_logs table
    op.create_table(
        'usage_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('count', sa.Integer(), server_default=sa.text('1'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create error_logs table
    op.create_table(
        'error_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('function_name', sa.String(), nullable=False),
        sa.Column('error_type', sa.String(), nullable=False),
        sa.Column('error_message', sa.String(), nullable=False),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('query_context', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_name', sa.String(), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_interactions table
    op.create_table(
        'user_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('interaction_type', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=True),
        sa.Column('content_id', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create subscription_events table
    op.create_table(
        'subscription_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('referrer', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create background_analysis_tasks table
    op.create_table(
        'background_analysis_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('query_hash', sa.String(), nullable=False),
        sa.Column('page', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), server_default=sa.text("'running'::text"), nullable=False),
        sa.Column('products_analyzed', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('total_products', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('heartbeat_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Add foreign keys to products table
    op.create_foreign_key(
        'affiliate_clicks_product_id_fkey',
        'affiliate_clicks', 'products',
        ['product_id'], ['id']
    )
    op.create_foreign_key(
        'price_comparisons_product_id_fkey',
        'price_comparisons', 'products',
        ['product_id'], ['id']
    )
    op.create_foreign_key(
        'product_likes_product_id_fkey',
        'product_likes', 'products',
        ['product_id'], ['id']
    )
    op.create_foreign_key(
        'fk_product_reviews_product_id',
        'product_reviews', 'products',
        ['product_id'], ['id']
    )
    op.create_foreign_key(
        'videos_product_id_fkey',
        'videos', 'products',
        ['product_id'], ['id']
    )
    op.create_foreign_key(
        'user_reviews_product_id_fkey',
        'user_reviews', 'products',
        ['product_id'], ['id']
    )

    # Create indexes
    op.create_index('idx_affiliate_clicks_user', 'affiliate_clicks', ['user_id'])
    op.create_index('idx_affiliate_clicks_product', 'affiliate_clicks', ['product_id'])
    op.create_index('idx_analytics_events_user', 'analytics_events', ['user_id'])
    op.create_index('idx_analytics_events_timestamp', 'analytics_events', ['timestamp'])
    op.create_index('idx_product_reviews_product', 'product_reviews', ['product_id'])
    op.create_index('idx_videos_product', 'videos', ['product_id'])
    op.create_index('idx_user_reviews_product', 'user_reviews', ['product_id'])
    op.create_index('idx_user_reviews_user', 'user_reviews', ['user_id'])
    op.create_index('idx_usage_logs_user', 'usage_logs', ['user_id'])
    op.create_index('idx_error_logs_timestamp', 'error_logs', ['created_at'])


def downgrade() -> None:
    # Drop all indexes
    op.drop_index('idx_error_logs_timestamp')
    op.drop_index('idx_usage_logs_user')
    op.drop_index('idx_user_reviews_user')
    op.drop_index('idx_user_reviews_product')
    op.drop_index('idx_videos_product')
    op.drop_index('idx_product_reviews_product')
    op.drop_index('idx_analytics_events_timestamp')
    op.drop_index('idx_analytics_events_user')
    op.drop_index('idx_affiliate_clicks_product')
    op.drop_index('idx_affiliate_clicks_user')

    # Drop all tables
    op.drop_table('user_roles')
    op.drop_table('background_analysis_tasks')
    op.drop_table('subscription_events')
    op.drop_table('user_interactions')
    op.drop_table('analytics_events')
    op.drop_table('error_logs')
    op.drop_table('usage_logs')
    op.drop_table('comments')
    op.drop_table('likes')
    op.drop_table('user_reviews')
    op.drop_table('videos')
    op.drop_table('product_reviews')
    op.drop_table('product_likes')
    op.drop_table('price_comparisons')
    op.drop_table('affiliate_clicks')
    op.drop_table('search_unlocks')
    op.drop_table('payment_transactions')
    op.drop_table('subscriptions')
    op.drop_table('profiles')
    op.drop_table('app_config')
