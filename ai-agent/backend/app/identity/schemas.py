"""Identity Schemas - Pydantic models for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    tenant_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    status: Optional[str] = None
    mfa_enabled: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    status: str
    email_verified: bool
    mfa_enabled: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tenant Schemas
class TenantBase(BaseModel):
    name: str
    type: str = "company"
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None


class TenantResponse(TenantBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# TenantUser Schemas
class TenantUserBase(BaseModel):
    role: str = "member"
    status: str = "invited"


class TenantUserCreate(TenantUserBase):
    user_id: UUID
    tenant_id: UUID


class TenantUserResponse(TenantUserBase):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    invited_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Session Schemas
class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool
    expires_at: datetime
    created_at: datetime
    last_activity_at: datetime

    class Config:
        from_attributes = True


# APIToken Schemas
class APITokenCreate(BaseModel):
    name: str
    tenant_id: Optional[UUID] = None
    scopes: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class APITokenResponse(BaseModel):
    id: UUID
    name: str
    token_hash: str  # Only show partial hash for security
    scopes: Optional[List[str]] = None
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_department_id: Optional[UUID] = None


class DepartmentCreate(DepartmentBase):
    tenant_id: UUID


class DepartmentResponse(DepartmentBase):
    id: UUID
    tenant_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: Optional[UUID] = None


class ProjectCreate(ProjectBase):
    tenant_id: UUID


class ProjectResponse(ProjectBase):
    id: UUID
    tenant_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Login Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None
    tenant_id: Optional[UUID] = None


class TenantSummary(BaseModel):
    id: UUID
    name: str
    status: Optional[str] = None


class TenantSelectRequest(BaseModel):
    tenant_ticket: str
    tenant_id: UUID


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: UserResponse
    tenant: Optional[TenantResponse] = None
    requires_mfa: bool = False
    mfa_ticket: Optional[str] = None
    requires_tenant_selection: bool = False
    tenant_ticket: Optional[str] = None
    tenants: Optional[List[TenantSummary]] = None

