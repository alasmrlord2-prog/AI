"""Identity Models - Users, Tenants, Sessions, TenantUsers."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class User(Base):
    """User model - represents a user account in the system."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")  # active, disabled, pending, suspended
    last_login_at = Column(DateTime, nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (lazy loading to avoid circular imports)
    tenant_users = relationship("TenantUser", back_populates="user", cascade="all, delete-orphan", lazy="select")
    tenant = relationship("Tenant", lazy="select")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan", lazy="select")
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"


class Tenant(Base):
    """Tenant model - represents a customer/organization."""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), default="company")  # company, individual, partner
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    status = Column(String(50), default="trial")  # active, suspended, trial, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (lazy loading to avoid circular imports)
    tenant_users = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan", lazy="select")
    # subscriptions relationship removed temporarily to avoid circular import issues
    # subscriptions = relationship("Subscription", back_populates="tenant", cascade="all, delete-orphan", lazy="select")
    departments = relationship("Department", back_populates="tenant", cascade="all, delete-orphan", lazy="select")
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, status={self.status})>"


class TenantUser(Base):
    """TenantUser model - links users to tenants with roles."""
    __tablename__ = "tenant_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member, viewer
    status = Column(String(50), default="invited")  # active, disabled, invited
    invited_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="tenant_users")
    user = relationship("User", back_populates="tenant_users")

    def __repr__(self):
        return f"<TenantUser(tenant_id={self.tenant_id}, user_id={self.user_id}, role={self.role})>"


class Session(Base):
    """Session model - tracks user login sessions.
    
    NOTE: This model matches the database schema from migration 002.
    For new code, prefer using SessionModel from app.core.session_manager.
    """
    __table_args__ = {'extend_existing': True}
    __tablename__ = "sessions"

    # Match the actual database schema from migration 002
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=True, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    refresh_expires_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    revoked = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Legacy properties for backward compatibility
    @property
    def token(self):
        """Legacy property - returns token_hash for compatibility."""
        return self.token_hash
    
    @property
    def is_active(self):
        """Legacy property - returns not revoked for compatibility."""
        return not self.revoked
    
    @property
    def last_activity_at(self):
        """Legacy property - returns last_used_at for compatibility."""
        return self.last_used_at
    
    @property
    def device_info(self):
        """Legacy property - returns user_agent for compatibility."""
        return self.user_agent

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"


class APIToken(Base):
    """API Token model - for programmatic access."""
    __tablename__ = "api_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    name = Column(String(255), nullable=False)  # Token name/description
    token_hash = Column(String(512), unique=True, nullable=False, index=True)
    scopes = Column(Text, nullable=True)  # JSON array of scopes
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_tokens")

    def __repr__(self):
        return f"<APIToken(id={self.id}, name={self.name}, is_active={self.is_active})>"


class Department(Base):
    """Department model - organizational units within a tenant."""
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    status = Column(String(50), default="active")  # active, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="departments")
    parent = relationship("Department", remote_side="Department.id", backref="children")
    projects = relationship("Project", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"


class Project(Base):
    """Project model - projects within a tenant/department."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, archived, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="projects")
    department = relationship("Department", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"

