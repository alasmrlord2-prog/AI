"""Tenant-aware Base Model for SQLAlchemy."""
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base
from uuid import uuid4


class TenantMixin:
    """Mixin to add tenant_id to models."""
    
    @declared_attr
    def tenant_id(cls):
        """Tenant ID column - required for multi-tenancy."""
        return Column(
            UUID(as_uuid=True),
            nullable=False,
            index=True,
            comment="Tenant ID for multi-tenant isolation"
        )


class TenantBase(Base, TenantMixin):
    """Base class for tenant-aware models."""
    __abstract__ = True
    
    def __init__(self, *args, **kwargs):
        """Ensure tenant_id is set."""
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'tenant_id') or self.tenant_id is None:
            raise ValueError(f"{self.__class__.__name__} requires tenant_id")


def apply_tenant_filter(query, model_class, tenant_id):
    """Apply tenant filter to query."""
    from app.core.tenant_middleware import TenantQueryFilter
    return TenantQueryFilter.filter_by_tenant(query, model_class, tenant_id)

