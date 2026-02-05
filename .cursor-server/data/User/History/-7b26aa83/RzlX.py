"""CRM API Routes - Tenant management dashboard."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.crm import service as crm_service

router = APIRouter(prefix="/api/crm", tags=["CRM"])

# Debug: Print when router is created
print(f"[CRM_API] Router created with prefix: {router.prefix}")


# ==================== Tenants ====================

@router.get("/tenants", response_model=dict)
async def list_tenants(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all tenants with summary info."""
    tenants, total = crm_service.CRMService.list_tenants(db, limit, offset)
    return {
        "tenants": tenants,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/tenants/{tenant_id}/dashboard", response_model=dict)
async def get_tenant_dashboard(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get comprehensive tenant dashboard."""
    dashboard = crm_service.CRMService.get_tenant_dashboard(db, tenant_id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return dashboard


@router.get("/tenants/{tenant_id}/summary", response_model=dict)
async def get_tenant_summary(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get tenant summary statistics."""
    summary = crm_service.CRMService.get_tenant_summary_stats(db, tenant_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return summary


# ==================== Users ====================

@router.get("/tenants/{tenant_id}/users", response_model=dict)
async def get_tenant_users(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed users list for tenant."""
    users = crm_service.CRMService.get_tenant_users_detailed(db, tenant_id)
    return {
        "users": users,
        "count": len(users)
    }


# ==================== Departments & Projects ====================

@router.get("/tenants/{tenant_id}/departments", response_model=dict)
async def get_tenant_departments(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get departments for tenant."""
    departments = crm_service.CRMService.get_tenant_departments(db, tenant_id)
    return {
        "departments": departments,
        "count": len(departments)
    }


@router.get("/tenants/{tenant_id}/projects", response_model=dict)
async def get_tenant_projects(
    tenant_id: UUID,
    department_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Get projects for tenant."""
    projects = crm_service.CRMService.get_tenant_projects(db, tenant_id, department_id)
    return {
        "projects": projects,
        "count": len(projects)
    }


# ==================== Usage & Analytics ====================

@router.get("/tenants/{tenant_id}/usage", response_model=dict)
async def get_tenant_usage(
    tenant_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get usage analytics for tenant."""
    analytics = crm_service.CRMService.get_tenant_usage_analytics(db, tenant_id, days)
    if "error" in analytics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=analytics["error"])
    return analytics


# ==================== Incidents ====================

@router.get("/tenants/{tenant_id}/incidents", response_model=dict)
async def get_tenant_incidents(
    tenant_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get incidents for tenant."""
    incidents, total = crm_service.CRMService.get_tenant_incidents(db, tenant_id, limit, offset)
    return {
        "incidents": incidents,
        "total": total,
        "limit": limit,
        "offset": offset
    }


# ==================== Audit Logs ====================

@router.get("/tenants/{tenant_id}/audit-logs", response_model=dict)
async def get_tenant_audit_logs(
    tenant_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    user_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get audit logs for tenant with filters."""
    logs, total = crm_service.CRMService.get_tenant_audit_logs(
        db, tenant_id, limit, offset, action, user_id, start_date, end_date
    )
    return {
        "logs": logs,
        "total": total,
        "limit": limit,
        "offset": offset
    }

