"""CRM API Routes - Tenant management dashboard with caching."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.aaa_middleware import get_current_user_context
from app.core.cache import get_cache, set_cache, cache_key, invalidate_cache
from app.crm import service as crm_service
from app.crm.schemas import TenantUserCreate

router = APIRouter(prefix="/api/crm", tags=["CRM"])

# Debug: Print when router is created
print(f"[CRM_API] Router created with prefix: {router.prefix}")


# ==================== Tenants ====================

@router.get("/tenants", response_model=dict)
async def list_tenants(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """List all tenants with summary info - cached for performance."""
    # Generate cache key
    cache_key_str = cache_key("crm:tenants:list", limit=limit, offset=offset)
    
    # Try cache first
    cached_result = get_cache(cache_key_str)
    if cached_result is not None:
        return cached_result
    
    try:
        tenants, total = crm_service.CRMService.list_tenants(db, limit, offset)
        result = {
            "tenants": tenants,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
        # Cache for 30 seconds
        set_cache(cache_key_str, result, ttl=30)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.post("/tenants", response_model=dict)
async def create_tenant(
    tenant_data: dict,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Create a new tenant and invalidate cache."""
    from app.identity import service as identity_service
    from app.identity.schemas import TenantCreate
    
    try:
        tenant_create = TenantCreate(
            name=tenant_data.get("name"),
            type=tenant_data.get("type", "company"),
            contact_email=tenant_data.get("contact_email"),
            contact_phone=tenant_data.get("contact_phone")
        )
        
        tenant = identity_service.IdentityService.create_tenant(db, tenant_create)
        
        # Invalidate tenants list cache
        invalidate_cache("crm:tenants:*")
        
        return {
            "id": str(tenant.id),
            "name": tenant.name,
            "type": tenant.type,
            "status": tenant.status,
            "contact_email": tenant.contact_email,
            "contact_phone": tenant.contact_phone,
            "created_at": tenant.created_at.isoformat() if tenant.created_at else None
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating tenant: {str(e)}"
        )


@router.get("/tenants/{tenant_id}/dashboard", response_model=dict)
async def get_tenant_dashboard(
    tenant_id: UUID,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Get comprehensive tenant dashboard - cached for 60 seconds."""
    # Generate cache key
    cache_key_str = cache_key("crm:tenant:dashboard", tenant_id=str(tenant_id))
    
    # Try cache first
    cached_result = get_cache(cache_key_str)
    if cached_result is not None:
        return cached_result
    
    try:
        dashboard = crm_service.CRMService.get_tenant_dashboard(db, tenant_id)
        if not dashboard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
        
        # Cache for 60 seconds
        set_cache(cache_key_str, dashboard, ttl=60)
        
        return dashboard
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard: {str(e)}"
        )


@router.get("/tenants/{tenant_id}/summary", response_model=dict)
async def get_tenant_summary(
    tenant_id: UUID,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
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
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Get detailed users list for tenant."""
    users = crm_service.CRMService.get_tenant_users_detailed(db, tenant_id)
    return {
        "users": users,
        "count": len(users)
    }


@router.post("/tenants/{tenant_id}/users", response_model=dict)
async def create_tenant_user(
    tenant_id: UUID,
    user_data: TenantUserCreate,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Create a new user for a tenant."""
    from app.identity import service as identity_service
    from app.identity.schemas import UserCreate
    from pydantic import ValidationError
    
    try:
        # Create user using Identity Service
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            tenant_id=tenant_id
        )
        
        user = identity_service.IdentityService.create_user(db, user_create)
        
        # Add user to tenant with role
        tenant_user = identity_service.IdentityService.add_user_to_tenant(
            db, tenant_id, user.id, user_data.role
        )
        
        # Activate user if specified
        if user_data.status == "active":
            user.status = "active"
            user.email_verified = user_data.email_verified
            db.commit()
            db.refresh(user)
        
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "status": user.status,
            "role": tenant_user.role,
            "tenant_id": str(tenant_id)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== Departments & Projects ====================

@router.get("/tenants/{tenant_id}/departments", response_model=dict)
async def get_tenant_departments(
    tenant_id: UUID,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
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
    user_context: Dict[str, Any] = Depends(get_current_user_context),
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
    user_context: Dict[str, Any] = Depends(get_current_user_context),
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
    user_context: Dict[str, Any] = Depends(get_current_user_context),
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
    user_context: Dict[str, Any] = Depends(get_current_user_context),
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

