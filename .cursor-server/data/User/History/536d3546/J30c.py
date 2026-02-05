"""Access Schemas - RBAC schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: UUID
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Permission Schemas
class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Role with Permissions
class RoleWithPermissions(RoleResponse):
    permissions: List[PermissionResponse] = []


# UserRole Schemas
class UserRoleCreate(BaseModel):
    user_id: UUID
    tenant_id: Optional[UUID] = None
    role_id: UUID


class UserRoleResponse(BaseModel):
    id: UUID
    user_id: UUID
    tenant_id: Optional[UUID] = None
    role_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True


# UserPermission Schemas
class UserPermissionCreate(BaseModel):
    user_id: UUID
    tenant_id: Optional[UUID] = None
    permission_id: UUID
    granted: bool = True


class UserPermissionResponse(BaseModel):
    id: UUID
    user_id: UUID
    tenant_id: Optional[UUID] = None
    permission_id: UUID
    granted: bool
    created_at: datetime
    updated_at: datetime
    permission: Optional[PermissionResponse] = None

    class Config:
        from_attributes = True


# Permission Check
class PermissionCheckRequest(BaseModel):
    user_id: UUID
    tenant_id: Optional[UUID] = None
    resource: str
    action: str


class PermissionCheckResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []

