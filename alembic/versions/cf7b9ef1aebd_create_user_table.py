"""Create user table

Revision ID: cf7b9ef1aebd
Revises: 
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf7b9ef1aebd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.execute('''
    CREATE TABLE platform_user (
        user_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
        organization_id TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Index on organization_id for faster queries
    CREATE INDEX idx_platform_user_organization_id ON platform_user(organization_id);
    ''')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP TABLE IF EXISTS platform_user;')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
