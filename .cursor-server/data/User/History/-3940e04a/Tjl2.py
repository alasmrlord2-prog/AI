"""Database connection and session management with connection pooling optimization."""
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from typing import Generator, Optional
from app.core.config import get_settings
import logging
import time

logger = logging.getLogger(__name__)

settings = get_settings()

# Create database engine with error handling and connection pooling
engine: Optional[object] = None
SessionLocal: Optional[sessionmaker] = None
Base = declarative_base()


# Connection pool event listeners for monitoring
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for better performance."""
    if "sqlite" in str(connection_record.engine.url):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkout for monitoring."""
    if settings.DEBUG:
        logger.debug("Connection checked out from pool")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log connection checkin for monitoring."""
    if settings.DEBUG:
        logger.debug("Connection returned to pool")


try:
    # Try to create database engine with optimized connection pooling
    if "sqlite" in settings.DATABASE_URL:
        # SQLite configuration
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        # PostgreSQL - optimized connection pooling
        try:
            import psycopg2  # noqa: F401
            engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
                # Connection pool settings for production
                pool_size=20,  # Number of connections to maintain
                max_overflow=40,  # Additional connections allowed
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,  # Recycle connections after 1 hour
                pool_timeout=30,  # Timeout for getting connection from pool
                # PostgreSQL-specific optimizations
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "shiftwave_backend",
                    "options": "-c statement_timeout=30000"  # 30 second query timeout
                }
            )
            SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
                expire_on_commit=False  # Don't expire objects on commit for better performance
            )
            logger.info("PostgreSQL engine created with optimized connection pooling")
        except ImportError:
            logger.warning("psycopg2 not installed. Database features will be disabled. Install with: pip install psycopg2-binary")
            # Use SQLite as fallback
            fallback_url = "sqlite:///./ai_agent.db"
            logger.info(f"Using SQLite fallback: {fallback_url}")
            engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.error(f"Failed to initialize database: {e}. Using SQLite fallback.")
    # Use SQLite as fallback
    fallback_url = "sqlite:///./ai_agent.db"
    try:
        engine = create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as fallback_error:
        logger.error(f"Failed to initialize SQLite fallback: {fallback_error}")
        engine = None
        SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Please check database configuration.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

