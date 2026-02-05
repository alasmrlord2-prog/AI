"""Session Management - Production-grade session handling."""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.core.database import Base
from app.core.cache import get_cache, set_cache, delete_cache, cache_key
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SessionModel(Base):
    """Database model for active sessions - matches migration 002."""
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=True, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token_hash = Column(String(255), nullable=True, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    refresh_expires_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    revoked = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Note: Do NOT add is_active, last_activity_at, or token columns here
    # These are from identity.models.Session which uses the same table
    # We use extend_existing=True to avoid conflicts


class SessionManager:
    """Manage user sessions with refresh tokens."""
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage."""
        from app.core.security import hash_token as _hash_token
        return _hash_token(token)
    
    @staticmethod
    def create_session(
        db: Session,
        user_id: UUID,
        tenant_id: Optional[UUID],
        access_token: str,
        refresh_token: str,
        access_expires: datetime,
        refresh_expires: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> SessionModel:
        """Create a new session."""
        from app.core.security import hash_token
        
        session = SessionModel(
            user_id=user_id,
            tenant_id=tenant_id,
            token_hash=hash_token(access_token),
            refresh_token_hash=hash_token(refresh_token),
            expires_at=access_expires,
            refresh_expires_at=refresh_expires,
            ip_address=ip_address,
            user_agent=user_agent,
            revoked=False
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Cache session
        cache_key_str = cache_key("session", token_hash=session.token_hash)
        set_cache(cache_key_str, {
            "user_id": str(session.user_id),
            "tenant_id": str(session.tenant_id) if session.tenant_id else None,
            "expires_at": session.expires_at.isoformat(),
            "revoked": session.revoked
        }, ttl=int((access_expires - datetime.utcnow()).total_seconds()))
        
        logger.info(f"Session created for user {user_id}")
        return session
    
    @staticmethod
    def get_session_by_token(db: Session, token: str) -> Optional[SessionModel]:
        """Get session by access token."""
        from app.core.security import hash_token
        
        token_hash = hash_token(token)
        
        # Try cache first
        cache_key_str = cache_key("session", token_hash=token_hash)
        cached = get_cache(cache_key_str)
        if cached:
            if cached.get("revoked"):
                return None
            # Get from DB
            session = db.query(SessionModel).filter(
                SessionModel.token_hash == token_hash,
                SessionModel.expires_at > datetime.utcnow()
            ).first()
            return session
        
        session = db.query(SessionModel).filter(
            SessionModel.token_hash == token_hash,
            SessionModel.revoked == False,
            SessionModel.expires_at > datetime.utcnow()
        ).first()
        
        return session
    
    @staticmethod
    def get_session_by_refresh_token(db: Session, refresh_token: str) -> Optional[SessionModel]:
        """Get session by refresh token."""
        from app.core.security import hash_token
        
        refresh_token_hash = hash_token(refresh_token)
        
        session = db.query(SessionModel).filter(
            SessionModel.refresh_token_hash == refresh_token_hash,
            SessionModel.revoked == False,
            SessionModel.refresh_expires_at > datetime.utcnow()
        ).first()
        
        return session
    
    @staticmethod
    def revoke_session(db: Session, token: str) -> bool:
        """Revoke a session."""
        session = SessionManager.get_session_by_token(db, token)
        if not session:
            return False
        
        session.revoked = True
        db.commit()
        
        # Invalidate cache
        from app.core.security import hash_token
        token_hash = hash_token(token)
        cache_key_str = cache_key("session", token_hash=token_hash)
        delete_cache(cache_key_str)
        
        logger.info(f"Session revoked for user {session.user_id}")
        return True
    
    @staticmethod
    def revoke_user_sessions(db: Session, user_id: UUID, keep_current_token: Optional[str] = None) -> int:
        """Revoke all sessions for a user (except current)."""
        query = db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.revoked == False
        )
        
        if keep_current_token:
            from app.core.security import hash_token
            current_hash = hash_token(keep_current_token)
            query = query.filter(SessionModel.token_hash != current_hash)
        
        sessions = query.all()
        count = len(sessions)
        
        for session in sessions:
            session.revoked = True
            # Invalidate cache
            cache_key_str = cache_key("session", token_hash=session.token_hash)
            delete_cache(cache_key_str)
        
        db.commit()
        logger.info(f"Revoked {count} sessions for user {user_id}")
        return count
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """Clean up expired sessions."""
        expired = db.query(SessionModel).filter(
            SessionModel.expires_at < datetime.utcnow(),
            SessionModel.revoked == False
        ).all()
        
        count = len(expired)
        for session in expired:
            db.delete(session)
        
        db.commit()
        logger.info(f"Cleaned up {count} expired sessions")
        return count
    
    @staticmethod
    def update_last_used(db: Session, token: str):
        """Update last used timestamp."""
        session = SessionManager.get_session_by_token(db, token)
        if session:
            session.last_used_at = datetime.utcnow()
            db.commit()

