"""Shared API dependencies for auth and feature gating."""
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.api.auth import get_current_user
from app.core.database import get_db
from app.core.features import get_tenant_feature
from app.audit.service import AuditService
from app.exceptions import AuthenticationError

security = HTTPBearer(auto_error=False)


def _log_access_denied(
    request: Request,
    user_id: Optional[str],
    tenant_id: Optional[str],
    reason: str,
    feature_key: Optional[str] = None,
) -> None:
    try:
        db = next(get_db())
        try:
            AuditService.log_action(
                db,
                action="access_denied",
                user_id=user_id,
                tenant_id=tenant_id,
                feature_key=feature_key,
                endpoint=str(request.url.path),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                metadata={"reason": reason},
                status="failed",
                error_message=reason,
            )
        finally:
            db.close()
    except Exception:
        # Avoid blocking auth flow on audit logging failures.
        return


def require_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Require authentication for protected routes."""
    try:
        return get_current_user(credentials)
    except AuthenticationError as exc:
        _log_access_denied(request, None, None, exc.message)
        raise


def require_feature(feature_key: str):
    """Require a tenant feature to be enabled before accessing an endpoint."""
    def _dependency(
        request: Request,
        current_user: Dict[str, Any] = Depends(require_auth),
    ) -> Dict[str, Any]:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            _log_access_denied(request, current_user.get("id"), None, "missing tenant_id")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant context required",
            )

        db = next(get_db())
        try:
            tenant_feature = get_tenant_feature(db, tenant_id, feature_key)
        finally:
            db.close()

        if not tenant_feature or not tenant_feature.enabled:
            _log_access_denied(
                request,
                current_user.get("id"),
                tenant_id,
                f"feature {feature_key} not enabled",
                feature_key=feature_key,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_key}' not enabled",
            )

        if tenant_feature.ends_at and tenant_feature.ends_at < datetime.utcnow():
            _log_access_denied(
                request,
                current_user.get("id"),
                tenant_id,
                f"feature {feature_key} expired",
                feature_key=feature_key,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_key}' expired",
            )

        return {
            "user": current_user,
            "tenant_feature": tenant_feature,
            "limits": tenant_feature.limits or {},
        }

    return _dependency
