"""Add user_invitations and usage_events tables.

Revision ID: 005_add_user_invitations_and_usage_events
Revises: 004_add_feature_key_to_audit_logs
Create Date: 2026-02-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "005_add_user_invitations_and_usage_events"
down_revision = "004_add_feature_key_to_audit_logs"
branch_labels = None
depends_on = None


def upgrade():
    """Create user_invitations and usage_events tables."""
    from sqlalchemy import inspect

    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    if "user_invitations" not in existing_tables:
        op.create_table(
            "user_invitations",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("token", sa.String(255), nullable=False, unique=True),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("accepted_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
        op.create_index("ix_user_invitations_user_id", "user_invitations", ["user_id"])
        op.create_index("ix_user_invitations_tenant_id", "user_invitations", ["tenant_id"])
        op.create_index("ix_user_invitations_token", "user_invitations", ["token"], unique=True)

    if "usage_events" not in existing_tables:
        op.create_table(
            "usage_events",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("service", sa.String(100), nullable=False),
            sa.Column("action", sa.String(100), nullable=False),
            sa.Column("units", sa.Integer(), server_default="1", nullable=False),
            sa.Column("source", sa.String(100), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
        op.create_index("ix_usage_events_tenant_id", "usage_events", ["tenant_id"])
        op.create_index("ix_usage_events_user_id", "usage_events", ["user_id"])
        op.create_index("ix_usage_events_created_at", "usage_events", ["created_at"])


def downgrade():
    """Drop user_invitations and usage_events tables."""
    op.drop_index("ix_usage_events_created_at", table_name="usage_events")
    op.drop_index("ix_usage_events_user_id", table_name="usage_events")
    op.drop_index("ix_usage_events_tenant_id", table_name="usage_events")
    op.drop_table("usage_events")

    op.drop_index("ix_user_invitations_token", table_name="user_invitations")
    op.drop_index("ix_user_invitations_tenant_id", table_name="user_invitations")
    op.drop_index("ix_user_invitations_user_id", table_name="user_invitations")
    op.drop_table("user_invitations")
