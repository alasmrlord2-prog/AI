"""Audit Service - Audit logging and accounting."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.audit.models import AuditLog, LoginLog
from app.core.config import get_settings

settings = get_settings()
_last_retention_run: Optional[datetime] = None
_retention_interval_seconds = 3600


def _maybe_enforce_retention(db: Session) -> None:
    global _last_retention_run
    if not settings.AUDIT_RETENTION_ENABLED:
        return
    now = datetime.utcnow()
    if _last_retention_run and (now - _last_retention_run).total_seconds() < _retention_interval_seconds:
        return
    _last_retention_run = now
    AuditService.prune_expired_logs(db)
    AuditService.prune_expired_login_logs(db)
from app.audit.schemas import AuditLogCreate, LoginLogCreate, AuditLogQuery, LoginLogQuery


class AuditService:
    """Service for audit logging and accounting."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        user_id: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        feature_key: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an action."""
        _maybe_enforce_retention(db)
        audit_log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            feature_key=feature_key,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            metadata_json=metadata,
            status=status,
            error_message=error_message
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def log_login(
        db: Session,
        email: str,
        status: str,
        user_id: Optional[UUID] = None,
        failure_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        location_country: Optional[str] = None,
        location_city: Optional[str] = None,
        mfa_used: bool = False,
        mfa_method: Optional[str] = None,
        session_id: Optional[UUID] = None
    ) -> LoginLog:
        """Log a login attempt."""
        _maybe_enforce_retention(db)
        login_log = LoginLog(
            user_id=user_id,
            email=email,
            status=status,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            location_country=location_country,
            location_city=location_city,
            mfa_used=mfa_used,
            mfa_method=mfa_method,
            session_id=session_id
        )
        db.add(login_log)
        db.commit()
        db.refresh(login_log)
        return login_log

    @staticmethod
    def prune_expired_logs(db: Session) -> int:
        """Delete audit logs older than retention period."""
        retention_days = settings.AUDIT_RETENTION_DAYS
        if not retention_days or retention_days <= 0:
            return 0
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        db.info["allow_audit_retention"] = True
        try:
            deleted = db.query(AuditLog).filter(AuditLog.created_at < cutoff).delete(
                synchronize_session=False
            )
            db.commit()
            return deleted or 0
        finally:
            db.info.pop("allow_audit_retention", None)

    @staticmethod
    def prune_expired_login_logs(db: Session) -> int:
        """Delete login logs older than retention period."""
        retention_days = settings.LOGIN_LOG_RETENTION_DAYS
        if not retention_days or retention_days <= 0:
            return 0
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        db.info["allow_audit_retention"] = True
        try:
            deleted = db.query(LoginLog).filter(LoginLog.created_at < cutoff).delete(
                synchronize_session=False
            )
            db.commit()
            return deleted or 0
        finally:
            db.info.pop("allow_audit_retention", None)

    @staticmethod
    def query_audit_logs(
        db: Session,
        query: AuditLogQuery
    ) -> tuple[List[AuditLog], int]:
        """Query audit logs with filters."""
        db_query = db.query(AuditLog)

        # Apply filters
        if query.user_id:
            db_query = db_query.filter(AuditLog.user_id == query.user_id)
        if query.tenant_id:
            db_query = db_query.filter(AuditLog.tenant_id == query.tenant_id)
        if query.action:
            db_query = db_query.filter(AuditLog.action == query.action)
        if query.resource_type:
            db_query = db_query.filter(AuditLog.resource_type == query.resource_type)
        if query.resource_id:
            db_query = db_query.filter(AuditLog.resource_id == query.resource_id)
        if query.feature_key:
            db_query = db_query.filter(AuditLog.feature_key == query.feature_key)
        if query.start_date:
            db_query = db_query.filter(AuditLog.created_at >= query.start_date)
        if query.end_date:
            db_query = db_query.filter(AuditLog.created_at <= query.end_date)

        # Get total count
        total = db_query.count()

        # Apply pagination
        logs = db_query.order_by(AuditLog.created_at.desc()).offset(query.offset).limit(query.limit).all()

        return logs, total

    @staticmethod
    def query_login_logs(
        db: Session,
        query: LoginLogQuery
    ) -> tuple[List[LoginLog], int]:
        """Query login logs with filters."""
        db_query = db.query(LoginLog)

        # Apply filters
        if query.user_id:
            db_query = db_query.filter(LoginLog.user_id == query.user_id)
        if query.email:
            db_query = db_query.filter(LoginLog.email == query.email)
        if query.status:
            db_query = db_query.filter(LoginLog.status == query.status)
        if query.start_date:
            db_query = db_query.filter(LoginLog.created_at >= query.start_date)
        if query.end_date:
            db_query = db_query.filter(LoginLog.created_at <= query.end_date)

        # Get total count
        total = db_query.count()

        # Apply pagination
        logs = db_query.order_by(LoginLog.created_at.desc()).offset(query.offset).limit(query.limit).all()

        return logs, total

