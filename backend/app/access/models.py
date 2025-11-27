"""Access Models - RBAC (Roles, Permissions, RolePermissions, UserRoles)."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

# Association table for many-to-many relationship
role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    """Role model - represents a role in the system."""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, is_system={self.is_system})>"


class Permission(Base):
    """Permission model - represents a permission/action in the system."""
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(100), nullable=False)  # e.g., "dashboard", "workflow", "agent"
    action = Column(String(50), nullable=False)  # e.g., "read", "write", "delete", "execute"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")
    user_permissions = relationship("UserPermission", back_populates="permission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, resource={self.resource}, action={self.action})>"


class UserRole(Base):
    """UserRole model - assigns roles to users within a tenant context."""
    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)  # NULL = global role
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (lazy loading to avoid circular imports)
    user = relationship("User", foreign_keys=[user_id], lazy="select")
    tenant = relationship("Tenant", lazy="select")
    role = relationship("Role", back_populates="user_roles", lazy="select")
    assigner = relationship("User", foreign_keys=[assigned_by], lazy="select")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, tenant_id={self.tenant_id}, role_id={self.role_id})>"


class UserPermission(Base):
    """UserPermission model - direct permission assignment (bypasses roles)."""
    __tablename__ = "user_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)  # NULL = global permission
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False)
    granted = Column(Boolean, default=True)  # True = grant, False = deny
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (lazy loading to avoid circular imports)
    user = relationship("User", foreign_keys=[user_id], lazy="select")
    tenant = relationship("Tenant", lazy="select")
    permission = relationship("Permission", back_populates="user_permissions", lazy="select")
    assigner = relationship("User", foreign_keys=[assigned_by], lazy="select")

    def __repr__(self):
        return f"<UserPermission(user_id={self.user_id}, permission_id={self.permission_id}, granted={self.granted})>"

