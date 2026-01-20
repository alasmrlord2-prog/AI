"""Add sessions table for session management

Revision ID: 002_add_sessions
Revises: 001_add_indexes
Create Date: 2024-12-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_sessions'
down_revision = '001_add_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Create sessions table for session management."""
    # Check if table already exists
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'sessions' in existing_tables:
        print("Table 'sessions' already exists, skipping creation")
        return
    
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('refresh_token_hash', sa.String(255), nullable=True, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('refresh_expires_at', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_tenant_id', 'sessions', ['tenant_id'])
    op.create_index('ix_sessions_token_hash', 'sessions', ['token_hash'], unique=True)
    op.create_index('ix_sessions_refresh_token_hash', 'sessions', ['refresh_token_hash'], unique=True)
    op.create_index('ix_sessions_expires_at', 'sessions', ['expires_at'])
    op.create_index('ix_sessions_revoked', 'sessions', ['revoked'])
    
    # Composite index for common queries
    op.create_index('ix_sessions_user_revoked', 'sessions', ['user_id', 'revoked'])


def downgrade():
    """Drop sessions table."""
    op.drop_index('ix_sessions_user_revoked', table_name='sessions')
    op.drop_index('ix_sessions_revoked', table_name='sessions')
    op.drop_index('ix_sessions_expires_at', table_name='sessions')
    op.drop_index('ix_sessions_refresh_token_hash', table_name='sessions')
    op.drop_index('ix_sessions_token_hash', table_name='sessions')
    op.drop_index('ix_sessions_tenant_id', table_name='sessions')
    op.drop_index('ix_sessions_user_id', table_name='sessions')
    op.drop_table('sessions')

