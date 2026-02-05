"""Multi-Tenancy Isolation Middleware - Enforces tenant boundaries."""
import logging
from fastapi import Request, HTTPException, status
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import inspect

logger = logging.getLogger(__name__)


class TenantIsolationMiddleware:
    """Middleware to enforce tenant isolation in all requests."""
    
    @staticmethod
    def require_tenant(user_context: Dict[str, Any]) -> UUID:
        """Require tenant_id in user context - reject if missing."""
        tenant_id = user_context.get("tenant_id")
        
        if not tenant_id:
            logger.warning(
                "Request rejected: Missing tenant_id",
                extra={
                    "user_id": str(user_context.get("user_id")),
                    "path": getattr(user_context, "path", "unknown")
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant context required. This is a multi-tenant application."
            )
        
        if isinstance(tenant_id, str):
            try:
                tenant_id = UUID(tenant_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tenant_id format"
                )
        
        return tenant_id
    
    @staticmethod
    def validate_tenant_access(
        db: Session,
        user_context: Dict[str, Any],
        requested_tenant_id: Optional[UUID] = None
    ) -> UUID:
        """Validate user has access to requested tenant."""
        user_tenant_id = TenantIsolationMiddleware.require_tenant(user_context)
        
        # If specific tenant requested, verify access
        if requested_tenant_id:
            if user_tenant_id != requested_tenant_id:
                logger.warning(
                    "Tenant access violation attempt",
                    extra={
                        "user_id": str(user_context.get("user_id")),
                        "user_tenant_id": str(user_tenant_id),
                        "requested_tenant_id": str(requested_tenant_id)
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Tenant isolation violation"
                )
        
        return user_tenant_id


class TenantQueryFilter:
    """Automatic tenant filtering for SQLAlchemy queries."""
    
    @staticmethod
    def filter_by_tenant(query, model_class, tenant_id: UUID):
        """Apply tenant filter to query if model has tenant_id column."""
        # Check if model has tenant_id attribute
        mapper = inspect(model_class)
        if 'tenant_id' in mapper.columns:
            return query.filter(model_class.tenant_id == tenant_id)
        return query
    
    @staticmethod
    def ensure_tenant_filter(query, model_class, tenant_id: UUID):
        """Ensure query has tenant filter - add if missing."""
        mapper = inspect(model_class)
        if 'tenant_id' not in mapper.columns:
            logger.warning(
                f"Model {model_class.__name__} does not have tenant_id column"
            )
            return query
        
        # Check if filter already applied
        for criterion in query.whereclause.children if hasattr(query.whereclause, 'children') else []:
            if hasattr(criterion, 'left') and str(criterion.left) == f"{model_class.__name__}.tenant_id":
                return query
        
        return query.filter(model_class.tenant_id == tenant_id)


def get_tenant_id(user_context: Dict[str, Any]) -> UUID:
    """Dependency to get and validate tenant_id from user context."""
    return TenantIsolationMiddleware.require_tenant(user_context)


def validate_tenant_access_dependency(
    user_context: Dict[str, Any],
    tenant_id: Optional[UUID] = None
) -> UUID:
    """Dependency to validate tenant access."""
    from app.core.database import get_db
    db = next(get_db())
    try:
        return TenantIsolationMiddleware.validate_tenant_access(
            db, user_context, tenant_id
        )
    finally:
        db.close()

