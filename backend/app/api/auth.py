"""Authentication API endpoints - Enterprise SaaS Grade."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional, Dict, Any
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import time
import logging

from app.models.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.database import get_db
from app.core.brute_force_protection import BruteForceProtection
from app.core.session_manager import SessionManager
from app.exceptions import AuthenticationError, AuthorizationError
from app.audit.service import AuditService
from app.identity.models import Tenant
from app.features.models import TenantFeature
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["auth"])

security = HTTPBearer(auto_error=False)

# Brute force protection instance
brute_force_protection = BruteForceProtection()


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
async def login(req: LoginRequest, request: Request):
    """
    Login endpoint - Production-grade with brute force protection.
    
    ✅ FEATURES:
    - Rate limiting per IP
    - Account lockout after failed attempts
    - Refresh token support
    - Session management
    - Multi-tenant isolation (tenant_id required)
    """
    # ✅ Rate limiting and brute force protection
    client_ip = request.client.host if request.client else "unknown"
    
    # Check IP rate limit
    if not brute_force_protection.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    
    # Check account lockout
    lockout_check = brute_force_protection.check_lockout(req.email)
    if lockout_check["locked"]:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {lockout_check['remaining_seconds']} seconds."
        )
    
    try:
        # Try to use Identity Service first (new system)
        try:
            from app.identity import service as identity_service
            from sqlalchemy.orm import Session
            from uuid import UUID
            
            # ✅ Proper async-safe DB session management
            db_gen = get_db()
            db: Session = next(db_gen)
            
            try:
                # Authenticate using Identity Service
                user = identity_service.IdentityService.authenticate_user(db, req.email, req.password)
                
                if not user:
                    attempt_result = brute_force_protection.record_failed_attempt(req.email, client_ip)
                    if attempt_result["locked"]:
                        raise HTTPException(
                            status_code=status.HTTP_423_LOCKED,
                            detail=f"Account locked after {attempt_result.get('remaining_attempts', 0)} failed attempts."
                        )
                    raise AuthenticationError("Incorrect email or password")
                
                # ✅ Get user's tenant(s) - handle multiple tenants
                tenant_users = identity_service.IdentityService.get_user_tenant_memberships(db, user.id)
                
                if not tenant_users:
                    logger.warning(f"User {user.email} has no tenant assignments")
                    brute_force_protection.record_failed_attempt(req.email, client_ip)
                    raise AuthenticationError("User has no tenant assignments")
                
                # Get active tenant (first one, or could be selected by user preference)
                tenant_user = tenant_users[0]
                tenant = identity_service.IdentityService.get_tenant_by_id(db, tenant_user.tenant_id)
                
                if not tenant:
                    logger.error(f"Tenant {tenant_user.tenant_id} not found for user {user.id}")
                    brute_force_protection.record_failed_attempt(req.email, client_ip)
                    raise AuthenticationError("Tenant not found")
                
                # ✅ Create token with tenant_id (REQUIRED for multi-tenancy)
                token_data = {
                    "sub": str(user.id),
                    "email": user.email,
                    "tenant_id": str(tenant.id),  # REQUIRED
                    "role": tenant_user.role,
                    "type": "access"
                }
                access_token = create_access_token(token_data)
                
                # ✅ Create refresh token
                refresh_token_data = {
                    "sub": str(user.id),
                    "email": user.email,
                    "tenant_id": str(tenant.id),
                }
                refresh_token = create_refresh_token(
                    refresh_token_data,
                    expires_delta=timedelta(days=30)
                )
                
                # Create session with refresh token
                access_expires = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
                refresh_expires = datetime.utcnow() + timedelta(days=30)
                
                # Create session using SessionManager (matches migration 002 schema)
                try:
                    SessionManager.create_session(
                        db,
                        user.id,
                        tenant.id,
                        access_token,
                        refresh_token,
                        access_expires,
                        refresh_expires,
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent")
                    )
                except Exception as session_error:
                    logger.warning(f"Session creation failed (non-critical): {session_error}")
                    # Continue without session - login should still succeed
                
                # ✅ Clear failed attempts on successful login
                brute_force_protection.clear_attempts(req.email)

                # ✅ Audit: login success
                try:
                    AuditService.log_login(
                        db,
                        email=user.email,
                        status="success",
                        user_id=user.id,
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent"),
                        session_id=None,
                    )
                    AuditService.log_action(
                        db,
                        action="login_success",
                        user_id=user.id,
                        tenant_id=tenant.id,
                        endpoint=request.url.path,
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent"),
                        metadata={"email": user.email},
                        status="success",
                    )
                except Exception:
                    logger.warning("Failed to write login audit log", exc_info=True)
                
                return TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=int(settings.JWT_EXPIRATION_HOURS * 3600)
                )
                
            finally:
                db.close()
                
        except HTTPException as http_exc:
            try:
                db = next(get_db())
                try:
                    AuditService.log_login(
                        db,
                        email=req.email,
                        status="blocked" if http_exc.status_code == status.HTTP_423_LOCKED else "failed",
                        failure_reason=str(http_exc.detail),
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent"),
                    )
                finally:
                    db.close()
            except Exception:
                logger.warning("Failed to write login audit log", exc_info=True)
            raise
        except AuthenticationError as auth_exc:
            try:
                db = next(get_db())
                try:
                    AuditService.log_login(
                        db,
                        email=req.email,
                        status="failed",
                        failure_reason=auth_exc.message,
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent"),
                    )
                finally:
                    db.close()
            except Exception:
                logger.warning("Failed to write login audit log", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            brute_force_protection.record_failed_attempt(req.email, client_ip)
            try:
                db = next(get_db())
                try:
                    AuditService.log_login(
                        db,
                        email=req.email,
                        status="failed",
                        failure_reason="login_error",
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent"),
                    )
                finally:
                    db.close()
            except Exception:
                logger.warning("Failed to write login audit log", exc_info=True)
            raise AuthenticationError("Login failed")
            
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
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
        
        # Create new access token
        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "tenant_id": tenant_id,
            "type": "access"
        }
        access_token = create_access_token(token_data)
        
        # Update session
        from app.core.security import hash_token
        session.token_hash = hash_token(access_token)
        session.expires_at = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Return same refresh token
            token_type="bearer",
            expires_in=int(settings.JWT_EXPIRATION_HOURS * 3600)
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
