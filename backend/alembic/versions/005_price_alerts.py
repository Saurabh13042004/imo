"""Add price alerts table.

Revision ID: 005
Revises: 004
Create Date: 2024-12-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create price_alerts table."""
    op.create_table(
        'price_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('product_url', sa.String(), nullable=False),
        sa.Column('target_price', sa.Numeric(), nullable=False),
        sa.Column('current_price', sa.Numeric(), nullable=True),
        sa.Column('currency', sa.String(), nullable=False, server_default='usd'),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('alert_sent', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('alert_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_price_alerts_product_id', 'price_alerts', ['product_id'], unique=False)
    op.create_index('ix_price_alerts_user_id', 'price_alerts', ['user_id'], unique=False)
    op.create_index('ix_price_alerts_email', 'price_alerts', ['email'], unique=False)


def downgrade() -> None:
    """Drop price_alerts table."""
    op.drop_index('ix_price_alerts_email', table_name='price_alerts')
    op.drop_index('ix_price_alerts_user_id', table_name='price_alerts')
    op.drop_index('ix_price_alerts_product_id', table_name='price_alerts')
    op.drop_table('price_alerts')
