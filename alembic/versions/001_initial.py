"""Generate initial migration."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_id', sa.String(200), nullable=False),
        sa.Column('asin', sa.String(20), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(10), nullable=True),
        sa.Column('rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_source', sa.String(50), nullable=True),
        sa.Column('description_quality_score', sa.Integer(), nullable=True),
        sa.Column('description_fetched_at', sa.DateTime(), nullable=True),
        sa.Column('brand', sa.String(200), nullable=True),
        sa.Column('category', sa.String(200), nullable=True),
        sa.Column('availability', sa.String(50), nullable=True),
        sa.Column('is_detailed_fetched', sa.Boolean(), nullable=True),
        sa.Column('reviews_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source', 'source_id', name='idx_products_source_id')
    )
    op.create_index('idx_products_title', 'products', ['title'])

    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_review_id', sa.String(200), nullable=True),
        sa.Column('author', sa.String(200), nullable=True),
        sa.Column('rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.Column('review_title', sa.String(500), nullable=True),
        sa.Column('verified_purchase', sa.Boolean(), nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=True),
        sa.Column('image_urls', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), nullable=True),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'source', 'source_review_id', name='idx_reviews_product_source')
    )
    op.create_index('idx_reviews_product', 'reviews', ['product_id'])
    op.create_index('idx_reviews_source', 'reviews', ['source'])

    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', sa.String(50), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('channel_name', sa.String(200), nullable=True),
        sa.Column('channel_id', sa.String(100), nullable=True),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('view_count', sa.BigInteger(), nullable=True),
        sa.Column('like_count', sa.Integer(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('video_url', sa.Text(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'video_id', name='idx_videos_product_id')
    )
    op.create_index('idx_videos_product', 'videos', ['product_id'])

    # Create search_cache table
    op.create_table(
        'search_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('query', sa.String(200), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('result_data', postgresql.JSON(), nullable=True),
        sa.Column('cached_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('query', 'source', name='idx_search_cache_query')
    )
    op.create_index('idx_search_cache_expires', 'search_cache', ['expires_at'])


def downgrade() -> None:
    op.drop_table('search_cache')
    op.drop_table('videos')
    op.drop_table('reviews')
    op.drop_table('products')
