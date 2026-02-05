"""Authentication-related models."""
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str
    mfa_code: Optional[str] = None
    tenant_id: Optional[str] = None


class RegisterRequest(BaseModel):
    """Register request model."""
    email: str
    password: str
    name: str
    role: str = "viewer"


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: Optional[str] = None  # ✅ NEW: Refresh token support
    token_type: str = "bearer"
    expires_in: int
    requires_mfa: Optional[bool] = False
    mfa_ticket: Optional[str] = None
    requires_tenant_selection: Optional[bool] = False
    tenant_ticket: Optional[str] = None
    tenants: Optional[list[dict]] = None


class AcceptInvitationRequest(BaseModel):
    """Accept invitation request model."""
    token: str
    password: Optional[str] = None


class MfaVerifyRequest(BaseModel):
    """MFA verification request model."""
    mfa_ticket: str
    mfa_code: str
    tenant_id: Optional[str] = None


class TenantSelectRequest(BaseModel):
    """Tenant selection request model."""
    tenant_ticket: str
    tenant_id: str

