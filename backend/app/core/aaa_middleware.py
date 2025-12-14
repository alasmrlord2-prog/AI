"""AAA Middleware - Authentication, Authorization, Accounting."""
import logging

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import verify_token
from app.identity import service as identity_service
from app.subscription import service as subscription_service
from app.access import service as access_service
from app.audit import service as audit_service

security = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)

settings = get_settings()


class AAAMiddleware:
    """AAA Middleware for request authentication, authorization, and accounting."""

    @staticmethod
    def _set_auth_error(
        request: Request,
        code: str,
        message: str,
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist structured auth error and log it."""
        request.state.auth_error = {"code": code, "message": message}
        logger.warning(
            "AAA authentication failed: %s",
            message,
            extra={"code": code, **(extra or {})},
        )

    @staticmethod
    def _decode_token_with_reason(token: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """Decode JWT token and return payload or structured error."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload, None
        except ExpiredSignatureError:
            return None, {"code": "token_expired", "message": "Token has expired"}
        except JWTError as exc:  # includes JWTClaimsError, JWTSignatureError, etc.
            return None, {"code": "invalid_token", "message": f"Token verification failed: {exc}"}

    @staticmethod
    async def authenticate_request(request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate request and return user context."""
        # Get token from header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.lower().startswith("bearer "):
            AAAMiddleware._set_auth_error(
                request,
                "missing_authorization",
                "Missing or invalid Authorization header",
            )
            return None

        token = authorization.split(" ", 1)[1]
        payload, token_error = AAAMiddleware._decode_token_with_reason(token)

        if token_error:
            AAAMiddleware._set_auth_error(
                request,
                token_error["code"],
                token_error["message"],
            )
            return None

        # Get user from database
        db: Session = next(get_db())
        try:
            # Validate and parse user_id from token
            sub = payload.get("sub")
            if not sub:
                AAAMiddleware._set_auth_error(
                    request,
                    "missing_subject",
                    "Token missing 'sub' claim",
                )
                return None
            

            try:
                user_id = UUID(sub)
            except (ValueError, TypeError):
                AAAMiddleware._set_auth_error(
                    request,
                    "invalid_subject_format",
                    "Token 'sub' is not a valid UUID",
                    extra={"sub": sub},
                )
                return None
            

            user = identity_service.IdentityService.get_user_by_id(db, user_id)

            if not user or user.status != "active":
                AAAMiddleware._set_auth_error(
                    request,
                    "user_inactive_or_missing",
                    "User not found or inactive",
                    extra={"user_id": str(user_id)},
                )
                return None

            # Get tenant
            tenant_id = None
            tenant_id_str = payload.get("tenant_id")
            if tenant_id_str:
                try:
                    tenant_id = UUID(tenant_id_str)
                except (ValueError, TypeError):
                    tenant_id = None

            # Clear any previous authentication error on successful authentication
            if hasattr(request.state, "auth_error"):
                request.state.auth_error = None

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
        detail = getattr(request.state, "auth_error", {"code": "not_authenticated", "message": "Not authenticated"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
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

