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
        error_message: Optional[str] = None
    ):
        """Account for request (audit logging + usage tracking)."""
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

            # Increment usage if tenant has subscription
            if user_context.get("tenant_id"):
                subscription = subscription_service.SubscriptionService.get_active_subscription(
                    db, user_context["tenant_id"]
                )
                if subscription:
                    # Increment request counter
                    subscription_service.SubscriptionService.increment_usage(
                        db, subscription.id, "requests", 1
                    )
        finally:
            db.close()

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
        """Check if usage is within limits."""
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
    async def trigger_workflow_event(
        db: Session,
        event_type: str,
        tenant_id: UUID,
        user_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trigger workflow event from CRM/AAA events."""
        try:
            # Check if workflow engine is available
            from app.api.workflows import service as workflow_service
            
            # Find workflows that listen to this event
            # This is a placeholder - actual implementation depends on workflow engine
            workflows = []  # workflow_service.get_workflows_by_trigger(event_type, tenant_id)
            
            for workflow in workflows:
                # Execute workflow
                # workflow_service.execute_workflow(workflow.id, metadata)
                pass
        except ImportError:
            # Workflow engine not available
            pass
        except Exception as e:
            # Log error but don't fail the main request
            import logging
            logging.error(f"Failed to trigger workflow event: {e}")

    @staticmethod
    async def handle_subscription_expired(
        db: Session,
        tenant_id: UUID
    ):
        """Handle subscription expired event - trigger workflows."""
        await AAAMiddleware.trigger_workflow_event(
            db,
            "subscription.expired",
            tenant_id,
            metadata={"event": "subscription_expired", "tenant_id": str(tenant_id)}
        )

    @staticmethod
    async def handle_user_added(
        db: Session,
        tenant_id: UUID,
        user_id: UUID
    ):
        """Handle user added event - trigger workflows."""
        await AAAMiddleware.trigger_workflow_event(
            db,
            "user.added",
            tenant_id,
            user_id,
            metadata={"event": "user_added", "tenant_id": str(tenant_id), "user_id": str(user_id)}
        )

    @staticmethod
    async def handle_user_disabled(
        db: Session,
        tenant_id: UUID,
        user_id: UUID
    ):
        """Handle user disabled event - trigger workflows."""
        await AAAMiddleware.trigger_workflow_event(
            db,
            "user.disabled",
            tenant_id,
            user_id,
            metadata={"event": "user_disabled", "tenant_id": str(tenant_id), "user_id": str(user_id)}
        )

    @staticmethod
    async def handle_usage_limit_exceeded(
        db: Session,
        tenant_id: UUID,
        resource_type: str,
        current_usage: int,
        limit: int
    ):
        """Handle usage limit exceeded event - trigger workflows."""
        await AAAMiddleware.trigger_workflow_event(
            db,
            "usage.limit_exceeded",
            tenant_id,
            metadata={
                "event": "usage_limit_exceeded",
                "tenant_id": str(tenant_id),
                "resource_type": resource_type,
                "current_usage": current_usage,
                "limit": limit
            }
        )


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

