"""Create conversation with text user_id

Revision ID: ceb61c324258
Revises: cf7b9ef1aebd
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ceb61c324258'
down_revision: Union[str, None] = 'cf7b9ef1aebd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    
    # Create session_context table based on the SessionContext model
    op.execute('''
    CREATE TABLE session_context (
        session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id TEXT,
        agent_id TEXT,
        system_prompt TEXT,
        messages JSONB NOT NULL,
        session_metadata JSONB,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_session_context_user_id ON session_context(user_id);
    CREATE INDEX idx_session_context_created_at ON session_context(created_at);
    ''')
    
    # Create memory table based on the Memory model
    op.execute('''
    CREATE TABLE memory (
        memory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        session_id UUID,
        user_id TEXT,
        agent_id UUID,
        memory_type TEXT,
        content TEXT NOT NULL,
        embedding_model TEXT NOT NULL,
        embedding vector(1024),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        -- Ensure we have at least user_id OR agent_id
        CONSTRAINT memory_owner_check CHECK (user_id IS NOT NULL OR agent_id IS NOT NULL)
    );
    
    CREATE INDEX idx_memory_user_id ON memory(user_id);
    CREATE INDEX idx_memory_agent_id ON memory(agent_id);
    CREATE INDEX idx_memory_session_id ON memory(session_id);
    CREATE INDEX idx_memory_type ON memory(memory_type);
    ''')

def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS memory;')
    op.execute('DROP TABLE IF EXISTS session_context;')
    op.execute('DROP EXTENSION IF EXISTS vector;')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')