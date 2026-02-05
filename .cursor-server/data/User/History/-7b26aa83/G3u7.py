"""CRM API Routes - Tenant management dashboard."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.crm import service as crm_service

router = APIRouter(prefix="/api/crm", tags=["CRM"])


@router.get("/tenants", response_model=dict)
async def list_tenants(
    limit: int = 100,
    offset: int = 0,
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

