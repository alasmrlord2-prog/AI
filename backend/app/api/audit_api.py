"""Audit API Routes - Audit logs and accounting."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.audit import service as audit_service
from app.audit import schemas

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.post("/logs", response_model=schemas.AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    log_data: schemas.AuditLogCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create an audit log entry."""
    log = audit_service.AuditService.log_action(
        db,
        action=log_data.action,
        user_id=log_data.user_id,
        tenant_id=log_data.tenant_id,
        resource_type=log_data.resource_type,
        resource_id=log_data.resource_id,
        ip_address=log_data.ip_address or (request.client.host if request.client else None),
        user_agent=log_data.user_agent or request.headers.get("user-agent"),
        endpoint=log_data.endpoint,
        metadata=log_data.metadata_json,
        status=log_data.status,
        error_message=log_data.error_message
    )
    return schemas.AuditLogResponse.from_orm(log)


@router.get("/logs", response_model=schemas.AuditLogListResponse)
async def query_audit_logs(
    query: schemas.AuditLogQuery = Depends(),
    db: Session = Depends(get_db)
):
    """Query audit logs."""
    logs, total = audit_service.AuditService.query_audit_logs(db, query)
    return {
        "logs": [schemas.AuditLogResponse.from_orm(log) for log in logs],
        "total": total,
        "limit": query.limit,
        "offset": query.offset
    }


@router.post("/login-logs", response_model=schemas.LoginLogResponse, status_code=status.HTTP_201_CREATED)
async def create_login_log(
    log_data: schemas.LoginLogCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a login log entry."""
    log = audit_service.AuditService.log_login(
        db,
        email=log_data.email,
        status=log_data.status,
        user_id=log_data.user_id,
        failure_reason=log_data.failure_reason,
        ip_address=log_data.ip_address or (request.client.host if request.client else None),
        user_agent=log_data.user_agent or request.headers.get("user-agent"),
        location_country=log_data.location_country,
        location_city=log_data.location_city,
        mfa_used=log_data.mfa_used,
        mfa_method=log_data.mfa_method,
        session_id=log_data.session_id
    )
    return schemas.LoginLogResponse.from_orm(log)


@router.get("/login-logs", response_model=schemas.LoginLogListResponse)
async def query_login_logs(
    query: schemas.LoginLogQuery = Depends(),
    db: Session = Depends(get_db)
):
    """Query login logs."""
    logs, total = audit_service.AuditService.query_login_logs(db, query)
    return {
        "logs": [schemas.LoginLogResponse.from_orm(log) for log in logs],
        "total": total,
        "limit": query.limit,
        "offset": query.offset
    }

