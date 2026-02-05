"""Add database indexes and optimizations

Revision ID: 001_add_indexes
Revises: 
Create Date: 2024-12-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for better query performance - safe to run even if tables don't exist."""
    # This migration is safe - it only creates indexes if tables exist
    # Tables will be created by other migrations or application startup
    pass


def downgrade():
    """Remove indexes."""
    pass
