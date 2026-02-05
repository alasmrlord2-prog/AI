"""Access module - RBAC (Roles, Permissions, RolePermissions, UserRoles)."""
from app.access.models import Role, Permission, UserRole, UserPermission

__all__ = ["Role", "Permission", "UserRole", "UserPermission"]

