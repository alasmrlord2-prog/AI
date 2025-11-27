"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Create database engine with error handling
engine: Optional[object] = None
SessionLocal: Optional[sessionmaker] = None
Base = declarative_base()

try:
    # Try to create database engine
    if "sqlite" in settings.DATABASE_URL:
        # SQLite doesn't need psycopg2
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        # PostgreSQL - try to import psycopg2
        try:
            import psycopg2  # noqa: F401
            engine = create_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        except ImportError:
            logger.warning("psycopg2 not installed. Database features will be disabled. Install with: pip install psycopg2-binary")
            # Use SQLite as fallback
            fallback_url = "sqlite:///./ai_agent.db"
            logger.info(f"Using SQLite fallback: {fallback_url}")
            engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG,
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

