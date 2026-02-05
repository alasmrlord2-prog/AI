"""Access API Routes - RBAC."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.access import service as access_service
from app.access import schemas

router = APIRouter(prefix="/api/access", tags=["Access"])


# Roles
@router.get("/roles", response_model=List[schemas.RoleResponse])
async def get_roles(
    db: Session = Depends(get_db)
):
    """Get all roles."""
    roles = access_service.AccessService.get_all_roles(db)
    return [schemas.RoleResponse.from_orm(r) for r in roles]


@router.post("/roles", response_model=schemas.RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: schemas.RoleCreate,
    db: Session = Depends(get_db)
):
    """Create a new role."""
    role = access_service.AccessService.create_role(db, role_data)
    return schemas.RoleResponse.from_orm(role)


@router.get("/roles/{role_id}", response_model=schemas.RoleResponse)
async def get_role(
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """Get role by ID."""
    role = access_service.AccessService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return schemas.RoleResponse.from_orm(role)


@router.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(
    role_id: UUID,
    permission_id: UUID,
    db: Session = Depends(get_db)
):
    """Assign permission to role."""
    success = access_service.AccessService.assign_permission_to_role(db, role_id, permission_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to assign permission")
    return {"message": "Permission assigned"}


# Permissions
@router.post("/permissions", response_model=schemas.PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: schemas.PermissionCreate,
    db: Session = Depends(get_db)
):
    """Create a new permission."""
    permission = access_service.AccessService.create_permission(db, permission_data)
    return schemas.PermissionResponse.from_orm(permission)


# User Roles
@router.post("/user-roles", response_model=schemas.UserRoleResponse)
async def assign_role_to_user(
    user_role_data: schemas.UserRoleCreate,
    db: Session = Depends(get_db)
):
    """Assign role to user."""
    user_role = access_service.AccessService.assign_role_to_user(
        db,
        user_role_data.user_id,
        user_role_data.role_id,
        user_role_data.tenant_id
    )
    return schemas.UserRoleResponse.from_orm(user_role)


@router.get("/users/{user_id}/roles", response_model=List[schemas.UserRoleResponse])
async def get_user_roles(
    user_id: UUID,
    tenant_id: UUID = None,
    db: Session = Depends(get_db)
):
    """Get all roles for a user."""
    user_roles = access_service.AccessService.get_user_roles(db, user_id, tenant_id)
    return [schemas.UserRoleResponse.from_orm(ur) for ur in user_roles]


# Permission Check
@router.post("/check", response_model=schemas.PermissionCheckResponse)
async def check_permission(
    check_request: schemas.PermissionCheckRequest,
    db: Session = Depends(get_db)
):
    """Check if user has permission."""
    allowed = access_service.AccessService.has_permission(
        db,
        check_request.user_id,
        check_request.resource,
        check_request.action,
        check_request.tenant_id
    )

    # Get user roles for context
    user_roles = access_service.AccessService.get_user_roles(
        db, check_request.user_id, check_request.tenant_id
    )
    roles = [ur.role.name for ur in user_roles if ur.role]

    return {
        "allowed": allowed,
        "reason": "Permission granted" if allowed else "Permission denied",
        "roles": roles,
        "permissions": []
    }

