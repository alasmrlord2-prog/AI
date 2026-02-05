"""Identity API Routes - Users, Tenants, Sessions."""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.identity import service as identity_service
from app.identity import schemas
from app.core.security import create_access_token, verify_token
from app.core.aaa_middleware import get_current_user_context
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
    # Check if no users exist - create default admin user
    from app.identity.models import User
    user_count = db.query(User).count()
    if user_count == 0:
        # Create default admin user and tenant
        from app.identity.schemas import UserCreate, TenantCreate
        from app.core.security import get_password_hash
        
        # Create tenant
        tenant = identity_service.IdentityService.create_tenant(
            db,
            TenantCreate(
                name="Default Organization",
                type="company",
                contact_email=login_data.email,
                contact_phone="+1234567890"
            )
        )
        
        # Create user
        user_data = UserCreate(
            email=login_data.email,
            password=login_data.password,
            full_name="Admin User",
            tenant_id=tenant.id
        )
        user = identity_service.IdentityService.create_user(db, user_data)
        user.status = "active"
        user.email_verified = True
        db.commit()
        db.refresh(user)
        
        # Add user as owner
        identity_service.IdentityService.add_user_to_tenant(db, tenant.id, user.id, role="owner")
    
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


@router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all users with pagination."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    users = identity_service.IdentityService.list_users(db, limit=limit, offset=offset)
    return [schemas.UserResponse.from_orm(user) for user in users]


@router.get("/users/count", response_model=dict)
async def get_users_count(
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Get total count of users."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    count = identity_service.IdentityService.count_users(db)
    return {"total_users": count}


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
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    user_id: Optional[UUID] = Query(None),  # Optional: for admin access
    active_only: bool = Query(False),  # If True, only return active sessions
    db: Session = Depends(get_db)
):
    """Get sessions for a user (all sessions by default, or active only if active_only=True)."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    # Use provided user_id if admin, otherwise use authenticated user
    target_user_id = user_id if user_id else user_context["user_id"]
    
    if active_only:
        sessions = identity_service.IdentityService.get_active_sessions(db, target_user_id)
    else:
        sessions = identity_service.IdentityService.get_all_sessions(db, target_user_id)
    
    return [schemas.SessionResponse.from_orm(s) for s in sessions]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Revoke a session."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    # Verify session belongs to user
    from app.identity.models import Session
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Check if user owns the session (or is admin)
    if str(session.user_id) != str(user_context["user_id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to revoke this session")
    
    success = identity_service.IdentityService.revoke_session(db, session_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"message": "Session revoked"}


# API Tokens
@router.post("/api-tokens", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_api_token(
    token_data: schemas.APITokenCreate,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Create API token."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    user_id = user_context["user_id"]
    api_token, plain_token = identity_service.IdentityService.create_api_token(
        db, user_id, token_data
    )
    # Return token object and plain token (shown only once)
    return {
        "token": schemas.APITokenResponse.from_orm(api_token),
        "plain_token": plain_token,  # Show only once - store securely
        "message": "Token created. Store the plain_token securely - it won't be shown again."
    }


@router.get("/api-tokens", response_model=List[schemas.APITokenResponse])
async def list_api_tokens(
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    tenant_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """List API tokens for user."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    user_id = user_context["user_id"]
    from app.identity.models import APIToken
    query = db.query(APIToken).filter(APIToken.user_id == user_id)
    if tenant_id:
        query = query.filter(APIToken.tenant_id == tenant_id)
    tokens = query.all()
    return [schemas.APITokenResponse.from_orm(t) for t in tokens]


@router.get("/api-tokens/{token_id}", response_model=schemas.APITokenResponse)
async def get_api_token(
    token_id: UUID,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Get API token by ID."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    user_id = user_context["user_id"]
    from app.identity.models import APIToken
    token = db.query(APIToken).filter(
        APIToken.id == token_id,
        APIToken.user_id == user_id
    ).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    return schemas.APITokenResponse.from_orm(token)


@router.delete("/api-tokens/{token_id}")
async def revoke_api_token(
    token_id: UUID,
    user_context: Dict[str, Any] = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """Revoke API token."""
    if not user_context:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    user_id = user_context["user_id"]
    from app.identity.models import APIToken
    token = db.query(APIToken).filter(
        APIToken.id == token_id,
        APIToken.user_id == user_id
    ).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    
    token.is_active = False
    db.commit()
    return {"message": "Token revoked"}


# Departments & Projects
@router.post("/tenants/{tenant_id}/departments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_department(
    tenant_id: UUID,
    name: str,
    description: Optional[str] = None,
    parent_department_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Create a department."""
    department = identity_service.IdentityService.create_department(
        db, tenant_id, name, description, parent_department_id
    )
    return {
        "id": str(department.id),
        "name": department.name,
        "description": department.description,
        "tenant_id": str(department.tenant_id),
        "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None
    }


@router.post("/tenants/{tenant_id}/projects", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_project(
    tenant_id: UUID,
    name: str,
    description: Optional[str] = None,
    department_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Create a project."""
    project = identity_service.IdentityService.create_project(
        db, tenant_id, name, description, department_id
    )
    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "tenant_id": str(project.tenant_id),
        "department_id": str(project.department_id) if project.department_id else None
    }

