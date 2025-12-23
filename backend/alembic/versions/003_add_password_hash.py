"""Add password_hash column to Profile table.

Revision ID: 003
Revises: 002_full_schema
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_full_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add password_hash column to profile table."""
    # Add password_hash column with nullable=True first (for existing users)
    op.add_column('profiles', sa.Column('password_hash', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('oauth_provider', sa.String(), nullable=True))
    op.add_column('profiles', sa.Column('oauth_provider_id', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove password_hash column from profile table."""
    op.drop_column('profiles', 'oauth_provider_id')
    op.drop_column('profiles', 'oauth_provider')
    op.drop_column('profiles', 'password_hash')
