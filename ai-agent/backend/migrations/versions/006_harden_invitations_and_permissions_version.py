"""Harden invitations and add permissions version.

Revision ID: 006_harden_invitations_and_permissions_version
Revises: 005_add_user_invitations_and_usage_events
Create Date: 2026-02-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql
import hashlib
import os


# revision identifiers, used by Alembic.
revision = "006_harden_invitations_and_permissions_version"
down_revision = "005_add_user_invitations_and_usage_events"
branch_labels = None
depends_on = None


def _get_hash_secret() -> str:
    secret = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise ValueError("SECRET_KEY or JWT_SECRET_KEY must be set to migrate invitation tokens")
    return secret


def upgrade():
    """Add permissions_version and harden invitation tokens."""
    conn = op.get_bind()
    inspector = inspect(conn)
    is_sqlite = conn.dialect.name == "sqlite"

    # tenant_users.permissions_version
    columns = {col["name"] for col in inspector.get_columns("tenant_users")}
    if "permissions_version" not in columns:
        op.add_column(
            "tenant_users",
            sa.Column("permissions_version", sa.Integer(), nullable=False, server_default="1"),
        )
        if not is_sqlite:
            op.alter_column("tenant_users", "permissions_version", server_default=None)

    # user_invitations: token -> token_hash, add revoked_at
    if "user_invitations" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("user_invitations")}

        if "token_hash" not in columns:
            op.add_column("user_invitations", sa.Column("token_hash", sa.String(255), nullable=True))

        if "revoked_at" not in columns:
            op.add_column("user_invitations", sa.Column("revoked_at", sa.DateTime(), nullable=True))

        if "token" in columns:
            secret = _get_hash_secret()
            user_invitations = sa.table(
                "user_invitations",
                sa.column("id", postgresql.UUID(as_uuid=True)),
                sa.column("token", sa.String()),
                sa.column("token_hash", sa.String()),
            )
            rows = conn.execute(sa.select(user_invitations.c.id, user_invitations.c.token)).fetchall()
            for row in rows:
                if row.token:
                    token_hash = hashlib.sha256(f"{row.token}{secret}".encode()).hexdigest()
                    conn.execute(
                        user_invitations.update()
                        .where(user_invitations.c.id == row.id)
                        .values(token_hash=token_hash)
                    )

        existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_invitations")}
        if "ix_user_invitations_token" in existing_indexes:
            op.drop_index("ix_user_invitations_token", table_name="user_invitations")

        if is_sqlite:
            with op.batch_alter_table("user_invitations") as batch_op:
                if "token" in columns:
                    batch_op.drop_column("token")
                batch_op.alter_column("token_hash", existing_type=sa.String(255), nullable=False)
        else:
            if "token" in columns:
                op.drop_column("user_invitations", "token")
            op.alter_column("user_invitations", "token_hash", existing_type=sa.String(255), nullable=False)

        # Ensure token_hash is non-null + indexed unique
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_invitations")}
        if "ix_user_invitations_token_hash" not in existing_indexes:
            op.create_index(
                "ix_user_invitations_token_hash",
                "user_invitations",
                ["token_hash"],
                unique=True,
            )


def downgrade():
    """Revert permissions_version and invitation hardening."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # tenant_users.permissions_version
    columns = {col["name"] for col in inspector.get_columns("tenant_users")}
    if "permissions_version" in columns:
        op.drop_column("tenant_users", "permissions_version")

    # user_invitations: token_hash -> token, drop revoked_at
    if "user_invitations" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("user_invitations")}

        if "token_hash" in columns:
            op.add_column("user_invitations", sa.Column("token", sa.String(255), nullable=True))

            # Cannot restore raw tokens; leave token NULL
            existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_invitations")}
            if "ix_user_invitations_token_hash" in existing_indexes:
                op.drop_index("ix_user_invitations_token_hash", table_name="user_invitations")
            op.drop_column("user_invitations", "token_hash")

        if "revoked_at" in columns:
            op.drop_column("user_invitations", "revoked_at")
