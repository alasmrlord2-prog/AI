"""Add feature entitlements and tenant_id on users

Revision ID: 003_add_feature_entitlements
Revises: 002_add_sessions
Create Date: 2026-01-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003_add_feature_entitlements"
down_revision = "002_add_sessions"
branch_labels = None
depends_on = None


def upgrade():
    """Create feature entitlement tables and add users.tenant_id."""
    from sqlalchemy import inspect

    conn = op.get_bind()
    inspector = inspect(conn)
    is_sqlite = conn.dialect.name == "sqlite"
    existing_tables = inspector.get_table_names()

    if "features" not in existing_tables:
        op.create_table(
            "features",
            sa.Column("key", sa.String(length=100), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )

    if "tenant_features" not in existing_tables:
        op.create_table(
            "tenant_features",
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("feature_key", sa.String(length=100), nullable=False),
            sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("limits", sa.JSON(), nullable=True),
            sa.Column("starts_at", sa.DateTime(), nullable=True),
            sa.Column("ends_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("tenant_id", "feature_key"),
        )
        op.create_index("ix_tenant_features_tenant_id", "tenant_features", ["tenant_id"])
        op.create_index("ix_tenant_features_feature_key", "tenant_features", ["feature_key"])
        if not is_sqlite:
            op.create_foreign_key(
                "fk_tenant_features_tenant",
                "tenant_features",
                "tenants",
                ["tenant_id"],
                ["id"],
            )
            op.create_foreign_key(
                "fk_tenant_features_feature",
                "tenant_features",
                "features",
                ["feature_key"],
                ["key"],
            )

    if "feature_usage_counters" not in existing_tables:
        op.create_table(
            "feature_usage_counters",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("feature_key", sa.String(length=100), nullable=False),
            sa.Column("counter_key", sa.String(length=100), nullable=False),
            sa.Column("value", sa.BigInteger(), server_default="0", nullable=False),
            sa.Column("reset_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
        op.create_index("ix_feature_usage_counters_tenant_id", "feature_usage_counters", ["tenant_id"])
        op.create_index("ix_feature_usage_counters_feature_key", "feature_usage_counters", ["feature_key"])
        op.create_index("ix_feature_usage_counters_counter_key", "feature_usage_counters", ["counter_key"])
        if not is_sqlite:
            op.create_foreign_key(
                "fk_feature_usage_counters_tenant",
                "feature_usage_counters",
                "tenants",
                ["tenant_id"],
                ["id"],
            )
            op.create_foreign_key(
                "fk_feature_usage_counters_feature",
                "feature_usage_counters",
                "features",
                ["feature_key"],
                ["key"],
            )

    if "users" in existing_tables:
        user_columns = [col["name"] for col in inspector.get_columns("users")]
        if "tenant_id" not in user_columns:
            op.add_column("users", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True))
            op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
            if not is_sqlite:
                op.create_foreign_key(
                    "fk_users_tenant",
                    "users",
                    "tenants",
                    ["tenant_id"],
                    ["id"],
                )


def downgrade():
    """Drop feature entitlements and users.tenant_id."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    is_sqlite = conn.dialect.name == "sqlite"
    existing_tables = inspector.get_table_names()

    if "users" in existing_tables:
        user_columns = [col["name"] for col in inspector.get_columns("users")]
        if "tenant_id" in user_columns:
            if not is_sqlite:
                op.drop_constraint("fk_users_tenant", "users", type_="foreignkey")
            op.drop_index("ix_users_tenant_id", table_name="users")
            op.drop_column("users", "tenant_id")

    if "feature_usage_counters" in existing_tables:
        if not is_sqlite:
            op.drop_constraint("fk_feature_usage_counters_feature", "feature_usage_counters", type_="foreignkey")
            op.drop_constraint("fk_feature_usage_counters_tenant", "feature_usage_counters", type_="foreignkey")
        op.drop_index("ix_feature_usage_counters_counter_key", table_name="feature_usage_counters")
        op.drop_index("ix_feature_usage_counters_feature_key", table_name="feature_usage_counters")
        op.drop_index("ix_feature_usage_counters_tenant_id", table_name="feature_usage_counters")
        op.drop_table("feature_usage_counters")

    if "tenant_features" in existing_tables:
        if not is_sqlite:
            op.drop_constraint("fk_tenant_features_feature", "tenant_features", type_="foreignkey")
            op.drop_constraint("fk_tenant_features_tenant", "tenant_features", type_="foreignkey")
        op.drop_index("ix_tenant_features_feature_key", table_name="tenant_features")
        op.drop_index("ix_tenant_features_tenant_id", table_name="tenant_features")
        op.drop_table("tenant_features")

    if "features" in existing_tables:
        op.drop_table("features")
