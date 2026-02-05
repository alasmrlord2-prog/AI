"""Authentication API endpoints - Enterprise SaaS Grade."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional, Dict, Any
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from app.models.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    AcceptInvitationRequest,
    MfaVerifyRequest,
    TenantSelectRequest,
)
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.database import get_db
from app.core.session_manager import SessionManager
from app.exceptions import AuthenticationError, AuthorizationError
from app.audit.service import AuditService
from app.identity.models import Tenant
from app.features.models import TenantFeature
from app.core.config import get_settings
from app.services.auth_login import perform_login, verify_mfa_ticket, verify_tenant_ticket

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["auth"])

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Get current user from JWT token.
    
    ✅ FIXED: Guest users now have role="guest" instead of "admin"
    ✅ ENHANCED: Requires tenant_id in token for multi-tenancy
    """
    if credentials is None:
        raise AuthenticationError("Missing authentication credentials")
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise AuthenticationError("Invalid authentication credentials")

    # Enforce active session to support logout/revocation
    try:
        db = next(get_db())
        try:
            session = SessionManager.get_session_by_token(db, token)
            if not session or session.revoked:
                raise AuthenticationError("Session expired or revoked")
            SessionManager.update_last_used(db, token)
        finally:
            db.close()
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Session validation failed: {e}", exc_info=True)
        raise AuthenticationError("Session validation failed")
    
    # ✅ ENHANCED: Require tenant_id in token
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise AuthenticationError("Token missing tenant_id - multi-tenant isolation required")
    
    # ✅ IMPROVED: Enrich payload with user data from Identity Service if available
    try:
        from app.identity import service as identity_service
        from app.identity.models import TenantUser
        from uuid import UUID
        db = next(get_db())
        try:
            user_id = payload.get("sub")
            if user_id:
                try:
                    user_uuid = UUID(str(user_id))
                except ValueError:
                    logger.warning(f"Invalid user_id in token: {user_id}")
                    user_uuid = None

                user = identity_service.IdentityService.get_user_by_id(db, user_uuid) if user_uuid else None
                if user:
                    # Get active tenant
                    tenant_users = identity_service.IdentityService.get_user_tenant_memberships(db, user.id)
                    active_tenant_user = tenant_users[0] if tenant_users else None

                    # Enforce permissions_version per tenant membership
                    token_version = payload.get("permissions_version")
                    try:
                        token_version = int(token_version) if token_version is not None else 1
                    except (TypeError, ValueError):
                        token_version = 1
                    if active_tenant_user:
                        membership = db.query(TenantUser).filter(
                            TenantUser.user_id == user.id,
                            TenantUser.tenant_id == active_tenant_user.tenant_id,
                            TenantUser.status == "active",
                        ).first()
                        if membership and token_version < (membership.permissions_version or 1):
                            raise AuthenticationError("Token permissions have been revoked")
                    
                    return {
                        "email": user.email,
                        "name": user.full_name or user.email,
                        "role": active_tenant_user.role if active_tenant_user else "member",
                        "id": str(user.id),
                        "tenant_id": str(active_tenant_user.tenant_id) if active_tenant_user else tenant_id,
                        "sub": str(user.id)
                    }
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not enrich user data from Identity Service: {e}")
    
    # Return token payload as fallback
    return {
        "email": payload.get("email", "unknown"),
        "name": payload.get("name", "Unknown"),
        "role": payload.get("role", "member"),
        "id": payload.get("sub"),
        "tenant_id": tenant_id,
        "sub": payload.get("sub")
    }


def require_role(allowed_roles: list):
    """Decorator to require specific role."""
    def decorator(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            logger.warning(f"User {current_user.get('email')} with role {user_role} attempted to access endpoint requiring {allowed_roles}")
            raise AuthorizationError("Insufficient permissions")
        return current_user
    return decorator


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Login endpoint - Production-grade with brute force protection.
    
    ✅ FEATURES:
    - Rate limiting per IP
    - Account lockout after failed attempts
    - Refresh token support
    - Session management
    - Multi-tenant isolation (tenant_id required)
    """
    result = perform_login(
        db,
        email=req.email,
        password=req.password,
        request=request,
        mfa_code=req.mfa_code,
        tenant_id=req.tenant_id,
    )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result.get("refresh_token"),
        token_type="bearer",
        expires_in=result.get("expires_in", 0),
        requires_mfa=result.get("requires_mfa", False),
        mfa_ticket=result.get("mfa_ticket"),
        requires_tenant_selection=result.get("requires_tenant_selection", False),
        tenant_ticket=result.get("tenant_ticket"),
        tenants=result.get("tenants"),
    )


@router.post("/mfa/verify", response_model=TokenResponse)
async def verify_mfa(
    req: MfaVerifyRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Verify MFA ticket and return tokens."""
    result = verify_mfa_ticket(
        db,
        request=request,
        mfa_ticket=req.mfa_ticket,
        mfa_code=req.mfa_code,
        tenant_id=getattr(req, "tenant_id", None),
    )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result.get("refresh_token"),
        token_type="bearer",
        expires_in=result.get("expires_in", 0),
        requires_mfa=False,
        mfa_ticket=None,
        requires_tenant_selection=result.get("requires_tenant_selection", False),
        tenant_ticket=result.get("tenant_ticket"),
        tenants=result.get("tenants"),
    )


@router.post("/select-tenant", response_model=TokenResponse)
async def select_tenant(
    req: TenantSelectRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Select tenant after multi-tenant login."""
    result = verify_tenant_ticket(
        db,
        request=request,
        tenant_ticket=req.tenant_ticket,
        tenant_id=req.tenant_id,
    )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result.get("refresh_token"),
        token_type="bearer",
        expires_in=result.get("expires_in", 0),
        requires_mfa=False,
        mfa_ticket=None,
        requires_tenant_selection=False,
        tenant_ticket=None,
        tenants=None,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, refresh_token: str):
    """
    Refresh access token using refresh token.
    
    ✅ FEATURES:
    - Validates refresh token
    - Creates new access token
    - Updates session
    - Multi-tenant isolation
    """
    from app.core.session_manager import SessionManager
    from sqlalchemy.orm import Session
    from uuid import UUID
    
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get session
        session = SessionManager.get_session_by_refresh_token(db, refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or expired"
            )
        
        if session.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session revoked"
            )
        
        # Require tenant_id
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token missing tenant_id"
            )
        
        # Load membership to enforce permissions_version
        from app.identity.models import TenantUser
        from uuid import UUID
        try:
            user_id = UUID(str(payload.get("sub")))
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user id in refresh token",
            )
        membership = db.query(TenantUser).filter(
            TenantUser.user_id == user_id,
            TenantUser.tenant_id == tenant_id,
            TenantUser.status == "active",
        ).first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not assigned to tenant",
            )

        token_version = payload.get("permissions_version")
        try:
            token_version = int(token_version) if token_version is not None else 1
        except (TypeError, ValueError):
            token_version = 1
        if token_version < (membership.permissions_version or 1):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token permissions have been revoked",
            )

        # Create new access token
        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "tenant_id": tenant_id,
            "type": "access",
            "permissions_version": membership.permissions_version or 1
        }
        access_token = create_access_token(token_data)

        # Rotate refresh token
        refresh_token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "tenant_id": tenant_id,
            "permissions_version": membership.permissions_version or 1,
        }
        new_refresh_token = create_refresh_token(
            refresh_token_data,
            expires_delta=timedelta(days=30),
        )

        # Update session with new token hashes
        from app.core.security import hash_token
        session.token_hash = hash_token(access_token)
        session.refresh_token_hash = hash_token(new_refresh_token)
        session.expires_at = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        session.refresh_expires_at = datetime.utcnow() + timedelta(days=30)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=int(settings.JWT_EXPIRATION_HOURS * 3600),
            requires_mfa=False,
            mfa_ticket=None,
            requires_tenant_selection=False,
            tenant_ticket=None,
            tenants=None,
        )
        
    finally:
        db.close()


@router.post("/logout")
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    """Logout - revoke current session."""
    from app.core.session_manager import SessionManager
    from fastapi.security import HTTPBearer
    
    security = HTTPBearer()
    credentials = await security(request)
    
    if credentials:
        db_gen = get_db()
        db = next(db_gen)
        try:
            SessionManager.revoke_session(db, credentials.credentials)
            try:
                AuditService.log_action(
                    db,
                    action="logout",
                    user_id=current_user.get("id"),
                    tenant_id=current_user.get("tenant_id"),
                    endpoint=request.url.path,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    status="success",
                )
            except Exception:
                logger.warning("Failed to write logout audit log", exc_info=True)
        finally:
            db.close()
    
    return {"message": "Logged out successfully"}


@router.post("/register", response_model=Dict[str, Any])
async def register(req: RegisterRequest, request: Request):
    """Register new user - requires tenant context."""
    # Implementation depends on your registration flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration endpoint - implement based on your requirements"
    )


@router.post("/accept-invitation", response_model=Dict[str, Any])
async def accept_invitation(
    req: AcceptInvitationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Accept a tenant invitation and activate the user."""
    from app.identity import service as identity_service

    try:
        user = identity_service.IdentityService.accept_invitation(
            db, req.token, req.password
        )

        # Audit invitation acceptance
        try:
            AuditService.log_action(
                db,
                action="invitation_accepted",
                user_id=user.id,
                tenant_id=user.tenant_id,
                endpoint=request.url.path,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                status="success",
            )
        except Exception:
            logger.warning("Failed to write invitation audit log", exc_info=True)

        return {
            "message": "Invitation accepted",
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "status": user.status,
            "email_verified": user.email_verified
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return current user context, tenant info, and feature entitlements."""
    db = next(get_db())
    try:
        tenant = None
        tenant_id = current_user.get("tenant_id")
        if tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

        features = (
            db.query(TenantFeature)
            .filter(TenantFeature.tenant_id == tenant_id)
            .all()
            if tenant_id
            else []
        )
        features_payload = {
            feature.feature_key: {
                "enabled": feature.enabled,
                "limits": feature.limits or {},
                "starts_at": feature.starts_at.isoformat() if feature.starts_at else None,
                "ends_at": feature.ends_at.isoformat() if feature.ends_at else None,
            }
            for feature in features
        }

        tenant_payload = None
        if tenant:
            tenant_payload = {
                "id": str(tenant.id),
                "name": tenant.name,
                "status": tenant.status,
            }

        return {
            "user": current_user,
            "tenant": tenant_payload,
            "features": features_payload,
        }
    finally:
        db.close()
