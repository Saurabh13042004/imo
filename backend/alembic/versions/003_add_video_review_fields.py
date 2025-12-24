"""Add status and s3_key fields to user_reviews table."""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # Add status column with default 'pending'
    op.add_column(
        'user_reviews',
        sa.Column('status', sa.String(), server_default=sa.text("'pending'::text"), nullable=False)
    )
    
    # Add s3_key column for S3 storage reference
    op.add_column(
        'user_reviews',
        sa.Column('s3_key', sa.String(), nullable=True)
    )
    
    # Add updated_at column with default now()
    op.add_column(
        'user_reviews',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    
    # Create index on status for faster queries
    op.create_index('idx_user_reviews_status', 'user_reviews', ['status'])
    op.create_index('idx_user_reviews_product_status', 'user_reviews', ['product_id', 'status'])


def downgrade() -> None:
    op.drop_index('idx_user_reviews_product_status', table_name='user_reviews')
    op.drop_index('idx_user_reviews_status', table_name='user_reviews')
    op.drop_column('user_reviews', 'updated_at')
    op.drop_column('user_reviews', 's3_key')
    op.drop_column('user_reviews', 'status')
