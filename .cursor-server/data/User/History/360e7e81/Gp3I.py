"""AAA Middleware - Authentication, Authorization, Accounting."""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import verify_token
from app.identity import service as identity_service
from app.subscription import service as subscription_service
from app.access import service as access_service
from app.audit import service as audit_service

security = HTTPBearer(auto_error=False)


class AAAMiddleware:
    """AAA Middleware for request authentication, authorization, and accounting."""

    @staticmethod
    async def authenticate_request(request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate request and return user context."""
        # Get token from header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None

        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)

        if not payload:
            return None

        # Get user from database
        db: Session = next(get_db())
        try:
            user_id = UUID(payload.get("sub"))
            user = identity_service.IdentityService.get_user_by_id(db, user_id)

            if not user or user.status != "active":
                return None

            # Get tenant
            tenant_id = None
            if payload.get("tenant_id"):
                tenant_id = UUID(payload.get("tenant_id"))

            return {
                "user_id": user_id,
                "user": user,
                "tenant_id": tenant_id,
                "token": token
            }
        finally:
            db.close()

    @staticmethod
    async def authorize_request(
        request: Request,
        user_context: Dict[str, Any],
        resource: str,
        action: str
    ) -> bool:
        """Authorize request based on user permissions."""
        db: Session = next(get_db())
        try:
            # Check RBAC permissions
            has_permission = access_service.AccessService.has_permission(
                db,
                user_context["user_id"],
                resource,
                action,
                user_context.get("tenant_id")
            )

            return has_permission
        finally:
            db.close()

    @staticmethod
    async def account_request(
        request: Request,
        user_context: Dict[str, Any],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        usage_resource_type: Optional[str] = None,
        usage_amount: int = 1
    ):
        """Account for request (audit logging + resource-based usage tracking)."""
        db: Session = next(get_db())
        try:
            # Log audit
            audit_service.AuditService.log_action(
                db,
                action=action,
                user_id=user_context["user_id"],
                tenant_id=user_context.get("tenant_id"),
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                endpoint=str(request.url.path),
                metadata={"method": request.method},
                status=status,
                error_message=error_message
            )

            # Resource-based usage tracking if tenant has subscription
            if user_context.get("tenant_id"):
                subscription = subscription_service.SubscriptionService.get_active_subscription(
                    db, user_context["tenant_id"]
                )
                if subscription:
                    # Map action to resource type if not provided
                    if not usage_resource_type:
                        usage_resource_type = AAAMiddleware._map_action_to_resource_type(action, request)
                    
                    # Increment usage counter for the specific resource type
                    if usage_resource_type:
                        subscription_service.SubscriptionService.increment_usage(
                            db, subscription.id, usage_resource_type, usage_amount
                        )
        finally:
            db.close()

    @staticmethod
    def _map_action_to_resource_type(action: str, request: Request) -> Optional[str]:
        """Map action/endpoint to resource type for usage tracking."""
        # Default mapping
        if "workflow" in action.lower() or "/workflow" in str(request.url.path):
            return "workflow_runs"
        elif "agent" in action.lower() or "/agent" in str(request.url.path):
            return "agents"
        elif "ai" in action.lower() or "/ai" in str(request.url.path):
            return "tokens"  # AI operations consume tokens
        elif "storage" in action.lower() or "/storage" in str(request.url.path):
            return "storage_gb"
        elif "log" in action.lower() or "/log" in str(request.url.path):
            return "log_volume_gb"
        else:
            return "requests"  # Default to requests

    @staticmethod
    async def check_subscription(
        request: Request,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check subscription status for tenant."""
        if not user_context.get("tenant_id"):
            return {
                "allowed": False,
                "reason": "No tenant associated with user"
            }

        db: Session = next(get_db())
        try:
            subscription_status = subscription_service.SubscriptionService.check_subscription_status(
                db, user_context["tenant_id"]
            )

            is_active = subscription_status.get("is_active", False)
            is_expired = subscription_status.get("is_expired", False)
            is_in_grace = subscription_status.get("is_in_grace", False)

            # Allow if active or in grace period
            allowed = is_active or is_in_grace

            return {
                "allowed": allowed,
                "is_active": is_active,
                "is_expired": is_expired,
                "is_in_grace": is_in_grace,
                "days_until_expiry": subscription_status.get("days_until_expiry"),
                "reason": "Subscription active" if allowed else "Subscription expired"
            }
        finally:
            db.close()

    @staticmethod
    async def check_usage_limit(
        request: Request,
        user_context: Dict[str, Any],
        resource_type: str,
        requested_amount: int = 1
    ) -> Dict[str, Any]:
        """Check if usage is within limits for a specific resource type."""
        if not user_context.get("tenant_id"):
            return {"allowed": True, "reason": "No tenant - unlimited"}

        db: Session = next(get_db())
        try:
            subscription = subscription_service.SubscriptionService.get_active_subscription(
                db, user_context["tenant_id"]
            )

            if not subscription:
                return {"allowed": False, "reason": "No active subscription"}

            result = subscription_service.SubscriptionService.check_usage_limit(
                db, subscription.id, resource_type, requested_amount
            )

            return result
        finally:
            db.close()

    @staticmethod
    async def get_user_context_with_subscription(
        request: Request
    ) -> Dict[str, Any]:
        """Get full user context including subscription and usage info."""
        user_context = await AAAMiddleware.authenticate_request(request)
        if not user_context:
            return None

        db: Session = next(get_db())
        try:
            # Get subscription status
            subscription_info = {}
            if user_context.get("tenant_id"):
                subscription_status = subscription_service.SubscriptionService.check_subscription_status(
                    db, user_context["tenant_id"]
                )
                subscription = subscription_status.get("subscription")
                
                if subscription:
                    # Get usage for all resource types
                    usage = subscription_service.SubscriptionService.get_usage(db, subscription.id)
                    
                    subscription_info = {
                        "subscription_id": str(subscription.id),
                        "plan_name": subscription.plan.name if subscription.plan else None,
                        "status": subscription_status,
                        "usage": usage,
                        "features": subscription.plan.features_json if subscription.plan else {}
                    }

            # Get user roles and permissions
            roles = access_service.AccessService.get_user_roles(
                db, user_context["user_id"], user_context.get("tenant_id")
            )
            permissions = access_service.AccessService.get_user_permissions(
                db, user_context["user_id"], user_context.get("tenant_id")
            )

            user_context.update({
                "subscription": subscription_info,
                "roles": [{"id": str(r.role.id), "name": r.role.name} for r in roles if r.role],
                "permissions": [{"id": str(p.permission.id), "name": p.permission.name} for p in permissions if p.permission]
            })

            return user_context
        finally:
            db.close()


# Dependency for getting current user context
async def get_current_user_context(request: Request) -> Dict[str, Any]:
    """Dependency to get current user context from request."""
    user_context = await AAAMiddleware.authenticate_request(request)
    if not user_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user_context


# Dependency for checking subscription
async def require_active_subscription(request: Request, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Dependency to require active subscription."""
    if not user_context:
        user_context = await get_current_user_context(request)

    subscription_check = await AAAMiddleware.check_subscription(request, user_context)
    if not subscription_check["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=subscription_check["reason"]
        )
    return subscription_check

