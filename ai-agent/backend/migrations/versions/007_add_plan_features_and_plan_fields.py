"""Add plan feature table and plan fields.

Revision ID: 007_add_plan_features_and_plan_fields
Revises: 006_harden_invitations_and_permissions_version
Create Date: 2026-02-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "007_add_plan_features_and_plan_fields"
down_revision = "006_harden_invitations_and_permissions_version"
branch_labels = None
depends_on = None


def upgrade():
    """Add plan fields and plan_features table."""
    from sqlalchemy import inspect

    conn = op.get_bind()
    inspector = inspect(conn)
    is_sqlite = conn.dialect.name == "sqlite"
    existing_tables = inspector.get_table_names()

    if "plans" in existing_tables:
        plan_columns = [col["name"] for col in inspector.get_columns("plans")]
        if "plan_type" not in plan_columns:
            op.add_column("plans", sa.Column("plan_type", sa.String(length=50), server_default="company"))
        if "max_requests_daily" not in plan_columns:
            op.add_column("plans", sa.Column("max_requests_daily", sa.BigInteger(), nullable=True))
        if "max_devices" not in plan_columns:
            op.add_column("plans", sa.Column("max_devices", sa.Integer(), nullable=True))
        if "log_retention_days" not in plan_columns:
            op.add_column("plans", sa.Column("log_retention_days", sa.Integer(), nullable=True))

    if "plan_features" not in existing_tables:
        op.create_table(
            "plan_features",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("feature_key", sa.String(length=100), nullable=False),
            sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("limit_value", sa.BigInteger(), nullable=True),
            sa.Column("unit", sa.String(length=50), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
        op.create_index("ix_plan_features_plan_id", "plan_features", ["plan_id"])
        op.create_index("ix_plan_features_feature_key", "plan_features", ["feature_key"])
        op.create_index(
            "idx_plan_feature_unique",
            "plan_features",
            ["plan_id", "feature_key"],
            unique=True,
        )
        if not is_sqlite:
            op.create_foreign_key(
                "fk_plan_features_plan",
                "plan_features",
                "plans",
                ["plan_id"],
                ["id"],
            )


def downgrade():
    """Drop plan fields and plan_features table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    is_sqlite = conn.dialect.name == "sqlite"
    existing_tables = inspector.get_table_names()

    if "plan_features" in existing_tables:
        if not is_sqlite:
            op.drop_constraint("fk_plan_features_plan", "plan_features", type_="foreignkey")
        op.drop_index("idx_plan_feature_unique", table_name="plan_features")
        op.drop_index("ix_plan_features_feature_key", table_name="plan_features")
        op.drop_index("ix_plan_features_plan_id", table_name="plan_features")
        op.drop_table("plan_features")

    if "plans" in existing_tables:
        plan_columns = [col["name"] for col in inspector.get_columns("plans")]
        if "log_retention_days" in plan_columns:
            op.drop_column("plans", "log_retention_days")
        if "max_devices" in plan_columns:
            op.drop_column("plans", "max_devices")
        if "max_requests_daily" in plan_columns:
            op.drop_column("plans", "max_requests_daily")
        if "plan_type" in plan_columns:
            op.drop_column("plans", "plan_type")
