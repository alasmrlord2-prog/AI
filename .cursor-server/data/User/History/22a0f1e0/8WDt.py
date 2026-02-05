"""CRM Schemas - Pydantic models for CRM responses."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# Tenant Dashboard Schemas
class TenantDetails(BaseModel):
    """Tenant details for dashboard."""
    id: UUID
    name: str
    type: str
    status: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionDetails(BaseModel):
    """Subscription details for dashboard."""
    id: Optional[UUID] = None
    plan_name: Optional[str] = None
    status: str
    is_active: bool
    is_expired: bool
    is_in_grace: bool
    days_until_expiry: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDetails(BaseModel):
    """User details for CRM."""
    id: UUID
    email: str
    full_name: Optional[str] = None
    role: str
    status: str
    last_login_at: Optional[datetime] = None
    mfa_enabled: bool = False
    email_verified: bool = False
    last_login_ip: Optional[str] = None
    last_login_location: Optional[str] = None
    active_sessions_count: int = 0
    api_tokens_count: int = 0
    created_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionDetails(BaseModel):
    """Session details."""
    id: UUID
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    last_activity_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DepartmentDetails(BaseModel):
    """Department details."""
    id: UUID
    name: str
    description: Optional[str] = None
    parent_department_id: Optional[UUID] = None
    projects_count: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectDetails(BaseModel):
    """Project details."""
    id: UUID
    name: str
    description: Optional[str] = None
    department_id: Optional[UUID] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsageDetails(BaseModel):
    """Usage details."""
    current_usage: Dict[str, Any]
    limits: Dict[str, Any]
    usage_history: Dict[str, List[Dict[str, Any]]]
    period_days: int

    class Config:
        from_attributes = True


class IncidentDetails(BaseModel):
    """Incident details."""
    id: UUID
    title: str
    severity: str
    status: str
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditLogDetails(BaseModel):
    """Audit log details."""
    id: UUID
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TenantDashboardResponse(BaseModel):
    """Complete tenant dashboard response."""
    tenant: TenantDetails
    subscription: SubscriptionDetails
    users: List[UserDetails]
    usage: Dict[str, Any]
    limits: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class TenantSummaryStats(BaseModel):
    """Tenant summary statistics."""
    user_count: int
    department_count: int
    project_count: int
    active_sessions: int
    recent_activity_count: int
    subscription_status: str
    is_active: bool
    days_until_expiry: Optional[int] = None

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Tenant list item."""
    id: UUID
    name: str
    type: str
    status: str
    subscription_status: str
    plan_name: Optional[str] = None
    user_count: int
    days_until_expiry: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

