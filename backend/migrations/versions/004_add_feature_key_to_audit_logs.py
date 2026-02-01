"""Add feature_key to audit logs.

Revision ID: 004_add_feature_key_to_audit_logs
Revises: 003_add_feature_entitlements
Create Date: 2026-01-21
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004_add_feature_key_to_audit_logs"
down_revision = "003_add_feature_entitlements"
branch_labels = None
depends_on = None


def upgrade():
    """Add feature_key column to audit_logs."""
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.add_column(sa.Column("feature_key", sa.String(length=100), nullable=True))
        batch_op.create_index("ix_audit_logs_feature_key", ["feature_key"])


def downgrade():
    """Remove feature_key column from audit_logs."""
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.drop_index("ix_audit_logs_feature_key")
        batch_op.drop_column("feature_key")
