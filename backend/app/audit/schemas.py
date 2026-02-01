"""Audit Schemas - AuditLog, LoginLog schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# AuditLog Schemas
class AuditLogBase(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    feature_key: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    status: str = "success"
    error_message: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None


class AuditLogResponse(AuditLogBase):
    id: UUID
    user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# LoginLog Schemas
class LoginLogBase(BaseModel):
    email: str
    status: str
    failure_reason: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    mfa_used: bool = False
    mfa_method: Optional[str] = None
    session_id: Optional[UUID] = None


class LoginLogCreate(LoginLogBase):
    user_id: Optional[UUID] = None


class LoginLogResponse(LoginLogBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Audit Query Schemas
class AuditLogQuery(BaseModel):
    user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    feature_key: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = 0


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    limit: int
    offset: int


# Login Query Schemas
class LoginLogQuery(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = 0


class LoginLogListResponse(BaseModel):
    logs: List[LoginLogResponse]
    total: int
    limit: int
    offset: int

