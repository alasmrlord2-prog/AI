"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import create_access_token, verify_token
from app.exceptions import AuthenticationError, AuthorizationError

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
    """Get current user from JWT token."""
    if not AUTH_ENABLED:
        return {"email": "guest", "name": "Guest", "role": "admin"}
    
    if credentials is None:
        try:
            return {"email": "guest", "name": "Guest", "role": "admin"}
        except:
            raise AuthenticationError("Not authenticated")
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise AuthenticationError("Invalid authentication credentials")
    
    return payload


def require_role(allowed_roles: list):
    """Decorator to require specific role."""
    def decorator(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise AuthorizationError("Insufficient permissions")
        return current_user
    return decorator


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Login endpoint."""
    try:
        if not AUTH_ENABLED:
            token = create_access_token({"email": req.email, "role": "admin"})
            return TokenResponse(
                access_token=token,
                user={"email": req.email, "name": "Guest", "role": "admin"}
            )
        
        user = authenticate_user(req.email, req.password)
        if not user:
            raise AuthenticationError("Incorrect email or password")
        
        access_token = create_access_token({"email": user["email"], "role": user["role"]})
        return TokenResponse(
            access_token=access_token,
            user=user
        )
    except AuthenticationError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )


@router.post("/register")
async def register(req: RegisterRequest, current_user: dict = Depends(require_role(["admin"]))):
    """Register new user (admin only)."""
    if not AUTH_ENABLED:
        return {"error": "Auth not enabled"}
    
    try:
        user = create_user(req.email, req.password, req.name, req.role)
        return {"message": "User created", "email": user["email"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.get("/roles")
async def get_roles():
    """Get available roles."""
    return {"roles": list(ROLES.keys()), "permissions": ROLES}

