"""Access Service - RBAC business logic."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Set
from datetime import datetime
from uuid import UUID

from app.access.models import Role, Permission, UserRole, UserPermission
from app.access.schemas import RoleCreate, PermissionCreate, UserRoleCreate, UserPermissionCreate
from app.identity.models import User, Tenant


class AccessService:
    """Service for managing RBAC (roles, permissions)."""

    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """Create a new role."""
        role = Role(
            name=role_data.name,
            description=role_data.description,
            is_system=False,
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_role_by_id(db: Session, role_id: UUID) -> Optional[Role]:
        """Get role by ID."""
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        """Get role by name."""
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_all_roles(db: Session, include_inactive: bool = False) -> List[Role]:
        """Get all roles."""
        query = db.query(Role)
        if not include_inactive:
            query = query.filter(Role.is_active == True)
        return query.all()

    @staticmethod
    def get_all_permissions(db: Session, include_inactive: bool = False) -> List[Permission]:
        """Get all permissions."""
        query = db.query(Permission)
        if not include_inactive:
            query = query.filter(Permission.is_active == True)
        return query.all()

    @staticmethod
    def assign_permission_to_role(db: Session, role_id: UUID, permission_id: UUID) -> bool:
        """Assign permission to role."""
        role = db.query(Role).filter(Role.id == role_id).first()
        permission = db.query(Permission).filter(Permission.id == permission_id).first()

        if not role or not permission:
            return False

        if permission not in role.permissions:
            role.permissions.append(permission)
            db.commit()

        return True

    @staticmethod
    def remove_permission_from_role(db: Session, role_id: UUID, permission_id: UUID) -> bool:
        """Remove permission from role."""
        role = db.query(Role).filter(Role.id == role_id).first()
        permission = db.query(Permission).filter(Permission.id == permission_id).first()

        if not role or not permission:
            return False

        if permission in role.permissions:
            role.permissions.remove(permission)
            db.commit()

        return True

    @staticmethod
    def create_permission(db: Session, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        permission = Permission(
            name=permission_data.name,
            resource=permission_data.resource,
            action=permission_data.action,
            description=permission_data.description,
            is_active=True
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return db.query(Permission).filter(Permission.name == name).first()

    @staticmethod
    def assign_role_to_user(
        db: Session,
        user_id: UUID,
        role_id: UUID,
        tenant_id: Optional[UUID] = None,
        assigned_by: Optional[UUID] = None
    ) -> UserRole:
        """Assign role to user."""
        user_role = UserRole(
            user_id=user_id,
            tenant_id=tenant_id,
            role_id=role_id,
            assigned_by=assigned_by,
            is_active=True
        )
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        return user_role

    @staticmethod
    def get_user_roles(
        db: Session,
        user_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> List[UserRole]:
        """Get all roles for a user (optionally filtered by tenant)."""
        query = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True
        )

        if tenant_id is not None:
            query = query.filter(
                or_(
                    UserRole.tenant_id == tenant_id,
                    UserRole.tenant_id.is_(None)  # Global roles
                )
            )

        return query.all()

    @staticmethod
    def get_user_permissions(
        db: Session,
        user_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> List[UserPermission]:
        """Get all direct permissions for a user."""
        query = db.query(UserPermission).filter(
            UserPermission.user_id == user_id
        )

        if tenant_id is not None:
            query = query.filter(
                or_(
                    UserPermission.tenant_id == tenant_id,
                    UserPermission.tenant_id.is_(None)  # Global permissions
                )
            )

        return query.all()

    @staticmethod
    def has_permission(
        db: Session,
        user_id: UUID,
        resource: str,
        action: str,
        tenant_id: Optional[UUID] = None
    ) -> bool:
        """Check if user has permission (via roles or direct assignment)."""
        # Get user roles
        user_roles = AccessService.get_user_roles(db, user_id, tenant_id)

        # Collect all permissions from roles
        role_permissions: Set[str] = set()
        for user_role in user_roles:
            role = user_role.role
            if role and role.is_active:
                for permission in role.permissions:
                    if permission.is_active:
                        role_permissions.add(f"{permission.resource}:{permission.action}")

        # Check direct permissions
        direct_permissions = AccessService.get_user_permissions(db, user_id, tenant_id)
        for user_perm in direct_permissions:
            permission = user_perm.permission
            if permission and permission.is_active:
                perm_key = f"{permission.resource}:{permission.action}"
                if user_perm.granted:
                    role_permissions.add(perm_key)
                else:
                    role_permissions.discard(perm_key)  # Deny overrides

        # Check if permission exists
        target_permission = f"{resource}:{action}"
        return target_permission in role_permissions

    @staticmethod
    def grant_permission(
        db: Session,
        user_id: UUID,
        permission_id: UUID,
        tenant_id: Optional[UUID] = None,
        granted: bool = True,
        assigned_by: Optional[UUID] = None
    ) -> UserPermission:
        """Grant or deny permission directly to user."""
        # Check if already exists
        existing = db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id,
            UserPermission.tenant_id == tenant_id
        ).first()

        if existing:
            existing.granted = granted
            existing.assigned_by = assigned_by
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        user_permission = UserPermission(
            user_id=user_id,
            tenant_id=tenant_id,
            permission_id=permission_id,
            granted=granted,
            assigned_by=assigned_by
        )
        db.add(user_permission)
        db.commit()
        db.refresh(user_permission)
        return user_permission

