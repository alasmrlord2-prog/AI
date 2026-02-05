"""Identity API Routes - Users, Tenants, Sessions."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.identity import service as identity_service
from app.identity import schemas
from app.core.security import create_access_token, verify_token
from datetime import timedelta
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/identity", tags=["Identity"])


# Authentication
@router.post("/login", response_model=schemas.LoginResponse)
async def login(
    login_data: schemas.LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login endpoint."""
    # Authenticate user
    user = identity_service.IdentityService.authenticate_user(
        db, login_data.email, login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check MFA if enabled
    if user.mfa_enabled and not login_data.mfa_code:
        return {
            "access_token": "",
            "token_type": "bearer",
            "user": schemas.UserResponse.from_orm(user),
            "tenant": None,
            "requires_mfa": True
        }

    # Get user's tenant
    tenant_users = identity_service.IdentityService.get_tenant_users(db, user.id)
    tenant = None
    if tenant_users:
        tenant_user = tenant_users[0]
        tenant = identity_service.IdentityService.get_tenant_by_id(db, tenant_user.tenant_id)

    # Create token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(tenant.id) if tenant else None
    }
    access_token = create_access_token(token_data)

    # Create session
    identity_service.IdentityService.create_session(
        db,
        user.id,
        access_token,
        device_info=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.from_orm(user),
        "tenant": schemas.TenantResponse.from_orm(tenant) if tenant else None,
        "requires_mfa": False
    }


# Users
@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    try:
        user = identity_service.IdentityService.create_user(db, user_data)
        return schemas.UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    user = identity_service.IdentityService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return schemas.UserResponse.from_orm(user)


@router.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: UUID,
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user."""
    user = identity_service.IdentityService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return schemas.UserResponse.from_orm(user)


# Tenants
@router.post("/tenants", response_model=schemas.TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: schemas.TenantCreate,
    db: Session = Depends(get_db)
):
    """Create a new tenant."""
    tenant = identity_service.IdentityService.create_tenant(db, tenant_data)
    return schemas.TenantResponse.from_orm(tenant)


@router.get("/tenants/{tenant_id}", response_model=schemas.TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get tenant by ID."""
    tenant = identity_service.IdentityService.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return schemas.TenantResponse.from_orm(tenant)


@router.put("/tenants/{tenant_id}", response_model=schemas.TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: schemas.TenantUpdate,
    db: Session = Depends(get_db)
):
    """Update tenant."""
    tenant = identity_service.IdentityService.update_tenant(db, tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return schemas.TenantResponse.from_orm(tenant)


@router.get("/tenants/{tenant_id}/users", response_model=List[schemas.TenantUserResponse])
async def get_tenant_users(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all users for a tenant."""
    tenant_users = identity_service.IdentityService.get_tenant_users(db, tenant_id)
    return [schemas.TenantUserResponse.from_orm(tu) for tu in tenant_users]


@router.post("/tenants/{tenant_id}/users", response_model=schemas.TenantUserResponse)
async def add_user_to_tenant(
    tenant_id: UUID,
    user_id: UUID,
    role: str = "member",
    db: Session = Depends(get_db)
):
    """Add user to tenant."""
    tenant_user = identity_service.IdentityService.add_user_to_tenant(
        db, tenant_id, user_id, role
    )
    return schemas.TenantUserResponse.from_orm(tenant_user)


# Sessions
@router.get("/sessions", response_model=List[schemas.SessionResponse])
async def get_sessions(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get active sessions for a user."""
    sessions = identity_service.IdentityService.get_active_sessions(db, user_id)
    return [schemas.SessionResponse.from_orm(s) for s in sessions]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Revoke a session."""
    success = identity_service.IdentityService.revoke_session(db, session_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"message": "Session revoked"}


# API Tokens
@router.post("/api-tokens", response_model=schemas.APITokenResponse)
async def create_api_token(
    token_data: schemas.APITokenCreate,
    user_id: UUID,  # Should come from auth token
    db: Session = Depends(get_db)
):
    """Create API token."""
    api_token, plain_token = identity_service.IdentityService.create_api_token(
        db, user_id, token_data
    )
    # In production, return plain_token only once
    response = schemas.APITokenResponse.from_orm(api_token)
    response.token_hash = plain_token  # For demo only - remove in production
    return response

