"""Add database indexes and optimizations

Revision ID: 001_add_indexes
Revises: 
Create Date: 2024-12-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '001_add_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for better query performance."""
    
    # Check if tables exist before creating indexes
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Indexes for users table (if exists)
    if 'users' in existing_tables:
        try:
            op.create_index(
                'ix_users_email',
                'users',
                ['email'],
                unique=True,
                if_not_exists=True
            )
            op.create_index(
                'ix_users_tenant_id',
                'users',
                ['tenant_id'],
                if_not_exists=True
            )
            op.create_index(
                'ix_users_created_at',
                'users',
                ['created_at'],
                if_not_exists=True
            )
        except Exception as e:
            print(f"Warning: Could not create indexes on users: {e}")
    
    # Indexes for tenants table (if exists)
    if 'tenants' in existing_tables:
        try:
            op.create_index(
                'ix_tenants_name',
                'tenants',
                ['name'],
                if_not_exists=True
            )
            op.create_index(
                'ix_tenants_created_at',
                'tenants',
                ['created_at'],
                if_not_exists=True
            )
        except Exception as e:
            print(f"Warning: Could not create indexes on tenants: {e}")
    
    # Indexes for sessions table (if exists)
    if 'sessions' in existing_tables:
        try:
            op.create_index(
                'ix_sessions_user_id',
                'sessions',
                ['user_id'],
                if_not_exists=True
            )
            op.create_index(
                'ix_sessions_token',
                'sessions',
                ['token'],
                unique=True,
                if_not_exists=True
            )
            op.create_index(
                'ix_sessions_expires_at',
                'sessions',
                ['expires_at'],
                if_not_exists=True
            )
        except Exception as e:
            print(f"Warning: Could not create indexes on sessions: {e}")
    
    # Indexes for audit_logs table (if exists)
    if 'audit_logs' in existing_tables:
        try:
            op.create_index(
                'ix_audit_logs_user_id',
                'audit_logs',
                ['user_id'],
                if_not_exists=True
            )
            op.create_index(
                'ix_audit_logs_tenant_id',
                'audit_logs',
                ['tenant_id'],
                if_not_exists=True
            )
            op.create_index(
                'ix_audit_logs_action',
                'audit_logs',
                ['action'],
                if_not_exists=True
            )
            op.create_index(
                'ix_audit_logs_created_at',
                'audit_logs',
                ['created_at'],
                if_not_exists=True
            )
            # Composite index for common queries
            op.create_index(
                'ix_audit_logs_tenant_created',
                'audit_logs',
                ['tenant_id', 'created_at'],
                if_not_exists=True
            )
        except Exception as e:
            print(f"Warning: Could not create indexes on audit_logs: {e}")
    
    # Indexes for tokens table (if exists)
    if 'tokens' in existing_tables:
        try:
            op.create_index(
                'ix_tokens_user_id',
                'tokens',
                ['user_id'],
                if_not_exists=True
            )
            op.create_index(
                'ix_tokens_tenant_id',
                'tokens',
                ['tenant_id'],
                if_not_exists=True
            )
            op.create_index(
                'ix_tokens_token_hash',
                'tokens',
                ['token_hash'],
                unique=True,
                if_not_exists=True
            )
            op.create_index(
                'ix_tokens_expires_at',
                'tokens',
                ['expires_at'],
                if_not_exists=True
            )
        except Exception as e:
            print(f"Warning: Could not create indexes on tokens: {e}")


def downgrade():
    """Remove indexes."""
    try:
        op.drop_index('ix_users_email', table_name='users', if_exists=True)
        op.drop_index('ix_users_tenant_id', table_name='users', if_exists=True)
        op.drop_index('ix_users_created_at', table_name='users', if_exists=True)
    except Exception:
        pass
    
    try:
        op.drop_index('ix_tenants_name', table_name='tenants', if_exists=True)
        op.drop_index('ix_tenants_created_at', table_name='tenants', if_exists=True)
    except Exception:
        pass
    
    try:
        op.drop_index('ix_sessions_user_id', table_name='sessions', if_exists=True)
        op.drop_index('ix_sessions_token', table_name='sessions', if_exists=True)
        op.drop_index('ix_sessions_expires_at', table_name='sessions', if_exists=True)
    except Exception:
        pass
    
    try:
        op.drop_index('ix_audit_logs_user_id', table_name='audit_logs', if_exists=True)
        op.drop_index('ix_audit_logs_tenant_id', table_name='audit_logs', if_exists=True)
        op.drop_index('ix_audit_logs_action', table_name='audit_logs', if_exists=True)
        op.drop_index('ix_audit_logs_created_at', table_name='audit_logs', if_exists=True)
        op.drop_index('ix_audit_logs_tenant_created', table_name='audit_logs', if_exists=True)
    except Exception:
        pass
    
    try:
        op.drop_index('ix_tokens_user_id', table_name='tokens', if_exists=True)
        op.drop_index('ix_tokens_tenant_id', table_name='tokens', if_exists=True)
        op.drop_index('ix_tokens_token_hash', table_name='tokens', if_exists=True)
        op.drop_index('ix_tokens_expires_at', table_name='tokens', if_exists=True)
    except Exception:
        pass
