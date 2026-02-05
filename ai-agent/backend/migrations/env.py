"""Alembic environment configuration."""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from app.core.config import get_settings
settings = get_settings()

# Import Base and models
# NOTE: We import Base directly without event listeners to avoid issues during migrations
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Import all database models to register them with Base
try:
    from app.identity.models import User, Tenant, TenantUser
    from app.audit.models import AuditLog
except ImportError:
    # Models not yet created, that's OK
    pass

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url from environment (always use DATABASE_URL from settings)
if settings.DATABASE_URL:
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
elif not config.get_main_option("sqlalchemy.url"):
    # Fallback to SQLite if no DATABASE_URL set
    config.set_main_option("sqlalchemy.url", "sqlite:///./ai_agent.db")

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Get database URL
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        url = settings.DATABASE_URL or "sqlite:///./ai_agent.db"
    
    # Create engine with NullPool for migrations (no connection pooling)
    # Disable event listeners that might cause issues
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        echo=False,
        connect_args={"connect_timeout": 10} if "postgresql" in url else {}
    )

    with connectable.connect() as connection:
        # Use autocommit mode for PostgreSQL to avoid transaction issues
        if "postgresql" in url:
            connection = connection.execution_options(autocommit=True)
        
        # Configure context
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            transaction_per_migration=True if "postgresql" not in url else False
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

