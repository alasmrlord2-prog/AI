"""Authentication-related models."""
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


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
    user: dict

