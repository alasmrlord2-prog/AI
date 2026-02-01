"""Audit Service - Audit logging and accounting."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.audit.models import AuditLog, LoginLog
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

