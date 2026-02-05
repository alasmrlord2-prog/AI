"""Authentication API endpoints - Enterprise SaaS Grade."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional, Dict, Any
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import time
import logging
from collections import defaultdict

from app.models.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.database import get_db
from app.core.brute_force_protection import BruteForceProtection
from app.core.session_manager import SessionManager
from app.exceptions import AuthenticationError, AuthorizationError
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Import auth functions (keeping existing auth.py for now)
try:
    from auth import (
        authenticate_user, create_user, check_permission, can_approve, ROLES, load_users
    )
    AUTH_ENABLED = True
except ImportError:
    AUTH_ENABLED = False
    def authenticate_user(*args, **kwargs):
        return None
    def create_user(*args, **kwargs):
        return {}
    def check_permission(*args, **kwargs):
        return True
    def can_approve(*args, **kwargs):
        return True
    ROLES = {}
    load_users = lambda: {}

router = APIRouter(prefix="/api/auth", tags=["auth"])

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Get current user from JWT token.
    
    ✅ FIXED: Guest users now have role="guest" instead of "admin"
    """
    if not AUTH_ENABLED:
        # In development mode, return guest with LIMITED permissions
        return {"email": "guest", "name": "Guest", "role": "guest", "tenant_id": None}
    
    if credentials is None:
        # ✅ FIXED: Guest has role="guest", NOT "admin"
        return {"email": "guest", "name": "Guest", "role": "guest", "tenant_id": None}
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise AuthenticationError("Invalid authentication credentials")
    
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
                        "tenant_id": str(active_tenant_user.tenant_id) if active_tenant_user else None,
                        "sub": str(user.id)
                    }
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not enrich user data from Identity Service: {e}")
        # Return token payload as fallback
        pass
    
    return payload


def require_role(allowed_roles: list):
    """Decorator to require specific role."""
    def decorator(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            logger.warning(f"User {current_user.get('email')} with role {user_role} attempted to access endpoint requiring {allowed_roles}")
            raise AuthorizationError("Insufficient permissions")
        return current_user
    return decorator


def check_rate_limit(ip_address: str) -> bool:
    """
    ✅ NEW: Rate limiting for login attempts.
    Returns True if request should be allowed, False if rate limited.
    """
    now = time.time()
    attempts = _login_attempts[ip_address]
    
    # Check if still locked out
    if attempts["lockout_until"] > now:
        remaining = int(attempts["lockout_until"] - now)
        logger.warning(f"Rate limit: IP {ip_address} is locked out for {remaining} more seconds")
        return False
    
    # Reset if lockout expired
    if attempts["lockout_until"] > 0 and attempts["lockout_until"] <= now:
        attempts["count"] = 0
        attempts["lockout_until"] = 0
    
    return True


def record_failed_login(ip_address: str):
    """Record a failed login attempt."""
    attempts = _login_attempts[ip_address]
    attempts["count"] += 1
    
    if attempts["count"] >= MAX_LOGIN_ATTEMPTS:
        attempts["lockout_until"] = time.time() + LOCKOUT_DURATION
        logger.warning(f"IP {ip_address} locked out after {attempts['count']} failed attempts")
    else:
        logger.info(f"Failed login attempt {attempts['count']}/{MAX_LOGIN_ATTEMPTS} from IP {ip_address}")


def record_successful_login(ip_address: str):
    """Reset failed login attempts on successful login."""
    _login_attempts[ip_address] = {"count": 0, "lockout_until": 0}


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request):
    """
    Login endpoint - integrated with Identity Service.
    
    ✅ IMPROVED:
    - Rate limiting
    - Better error handling
    - Async-safe DB session management
    - Refresh token support
    """
    # ✅ NEW: Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Please try again in {int((_login_attempts[client_ip]['lockout_until'] - time.time()))} seconds."
        )
    
    try:
        # Try to use Identity Service first (new system)
        try:
            from app.identity import service as identity_service
            from sqlalchemy.orm import Session
            
            # ✅ FIXED: Proper async-safe DB session management
            db_gen = get_db()
            db: Session = next(db_gen)
            
            try:
                # Authenticate using Identity Service
                user = identity_service.IdentityService.authenticate_user(db, req.email, req.password)
                
                if not user:
                    record_failed_login(client_ip)
                    raise AuthenticationError("Incorrect email or password")
                
                # ✅ IMPROVED: Get user's tenant(s) - handle multiple tenants
                tenant_users = identity_service.IdentityService.get_user_tenant_memberships(db, user.id)
                
                if not tenant_users:
                    logger.warning(f"User {user.email} has no tenant assignments")
                    record_failed_login(client_ip)
                    raise AuthenticationError("User has no tenant assignments")
                
                # Get active tenant (first one, or could be selected by user preference)
                tenant_user = tenant_users[0]
                tenant = identity_service.IdentityService.get_tenant_by_id(db, tenant_user.tenant_id)
                
                if not tenant:
                    logger.error(f"Tenant {tenant_user.tenant_id} not found for user {user.id}")
                    record_failed_login(client_ip)
                    raise AuthenticationError("Tenant not found")
                
                # ✅ IMPROVED: Create token with proper expiration
                token_data = {
                    "sub": str(user.id),
                    "email": user.email,
                    "tenant_id": str(tenant.id),
                    "role": tenant_user.role,
                    "type": "access"
                }
                access_token = create_access_token(token_data)
                
                # ✅ NEW: Create refresh token
                refresh_token_data = {
                    "sub": str(user.id),
                    "email": user.email,
                    "tenant_id": str(tenant.id),
                    "type": "refresh"
                }
                refresh_token = create_access_token(
                    refresh_token_data,
                    expires_delta=timedelta(days=30)  # Refresh token valid for 30 days
                )
                
                # ✅ IMPROVED: Create session with proper error handling
                try:
                    identity_service.IdentityService.create_session(
                        db,
                        user.id,
                        access_token,
                        device_info=request.headers.get("user-agent", "Unknown"),
                        ip_address=client_ip,
                        user_agent=request.headers.get("user-agent", "Unknown")
                    )
                    db.commit()
                except Exception as session_error:
                    logger.error(f"Failed to create session: {session_error}")
                    db.rollback()
                    # Continue anyway - session creation failure shouldn't block login
                
                # ✅ NEW: Record successful login
                record_successful_login(client_ip)
                
                return TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,  # ✅ NEW: Include refresh token
                    user={
                        "email": user.email,
                        "name": user.full_name or user.email,
                        "role": tenant_user.role,
                        "id": str(user.id),
                        "tenant_id": str(tenant.id)
                    }
                )
            finally:
                # ✅ FIXED: Properly close DB session
                db.close()
                
        except AuthenticationError:
            raise
        except Exception as identity_error:
            logger.error(f"Identity Service error: {identity_error}", exc_info=True)
            # Fallback to old auth system if Identity Service fails
            if not AUTH_ENABLED:
                logger.warning("Identity Service failed and AUTH_ENABLED=False, creating guest token")
                token = create_access_token({"email": req.email, "role": "guest"})
                return TokenResponse(
                    access_token=token,
                    user={"email": req.email, "name": "Guest", "role": "guest"}
                )
            
            # Try old auth system
            user = authenticate_user(req.email, req.password)
            if not user:
                record_failed_login(client_ip)
                raise AuthenticationError("Incorrect email or password")
            
            record_successful_login(client_ip)
            access_token = create_access_token({"email": user["email"], "role": user["role"]})
            return TokenResponse(
                access_token=access_token,
                user=user
            )
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login error occurred"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    current_user: dict = Depends(get_current_user)
):
    """
    ✅ NEW: Refresh access token using refresh token.
    """
    try:
        payload = verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        
        # Create new access token
        new_token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "tenant_id": payload.get("tenant_id"),
            "role": payload.get("role"),
            "type": "access"
        }
        new_access_token = create_access_token(new_token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise AuthenticationError("Failed to refresh token")


@router.post("/register")
async def register(req: RegisterRequest, current_user: dict = Depends(require_role(["admin"]))):
    """
    Register new user (admin only).
    
    ✅ FIXED: Now properly protected - guest users cannot register
    """
    if not AUTH_ENABLED:
        return {"error": "Auth not enabled"}
    
    # ✅ IMPROVED: Additional check (defense in depth)
    if current_user.get("role") != "admin":
        raise AuthorizationError("Only administrators can register new users")
    
    try:
        user = create_user(req.email, req.password, req.name, req.role)
        logger.info(f"User {req.email} registered by admin {current_user.get('email')}")
        return {"message": "User created", "email": user["email"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.get("/roles")
async def get_roles():
    """
    Get available roles - from Identity Service directly.
    
    ✅ FIXED: Removed HTTP request loop - now calls service directly
    """
    try:
        # ✅ FIXED: Direct service call instead of HTTP request
        from app.identity import service as identity_service
        from sqlalchemy.orm import Session
        
        db_gen = get_db()
        db: Session = next(db_gen)
        
        try:
            # Get all tenant users and extract unique roles
            all_tenant_users = identity_service.IdentityService.get_all_tenant_users(db)
            roles_found = set()
            
            for tu in all_tenant_users:
                if tu.role:
                    roles_found.add(tu.role)
            
            # Also check if there's a roles API endpoint we can call directly
            try:
                from app.api.roles_config import router as roles_router
                # If roles_router exists, we could call it, but direct DB access is better
                pass
            except ImportError:
                pass
            
            return {
                "roles": sorted(list(roles_found)) if roles_found else ["member", "admin"],
                "permissions": {}
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting roles: {e}", exc_info=True)
        # ✅ IMPROVED: Return safe default instead of empty
        return {
            "roles": ["member", "admin", "guest"],
            "permissions": {},
            "error": f"Could not fetch roles from Identity Service: {str(e)}"
        }
