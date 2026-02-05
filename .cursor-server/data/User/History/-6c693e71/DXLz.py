"""Audit Models - AuditLog, LoginLog for Accounting and Audit Trail."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class AuditLog(Base):
    """AuditLog model - tracks all user actions for audit trail."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # NULL = system action
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    # What
    action = Column(String(100), nullable=False, index=True)  # "login", "create_project", "run_workflow", etc.
    resource_type = Column(String(100), nullable=True)  # "project", "workflow", "user", etc.
    resource_id = Column(String(255), nullable=True)  # ID of the resource
    
    # Where/How
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)  # API endpoint
    
    # Details
    metadata_json = Column(JSON, nullable=True)  # Additional context
    status = Column(String(50), default="success")  # success, failed, error
    error_message = Column(Text, nullable=True)
    
    # When
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    tenant = relationship("Tenant", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id}, created_at={self.created_at})>"


class LoginLog(Base):
    """LoginLog model - tracks login attempts and sessions."""
    __tablename__ = "login_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # NULL = failed login attempt
    
    # Login details
    email = Column(String(255), nullable=False, index=True)  # Email used in login attempt
    status = Column(String(50), nullable=False)  # success, failed, blocked
    failure_reason = Column(String(255), nullable=True)  # "invalid_password", "account_disabled", etc.
    
    # Location/Device
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    location_country = Column(String(100), nullable=True)
    location_city = Column(String(100), nullable=True)
    
    # MFA
    mfa_used = Column(Boolean, default=False)
    mfa_method = Column(String(50), nullable=True)  # "totp", "email", "sms"
    
    # Session
    session_id = Column(UUID(as_uuid=True), nullable=True)
    
    # When
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="login_logs")

    def __repr__(self):
        return f"<LoginLog(id={self.id}, email={self.email}, status={self.status}, created_at={self.created_at})>"

