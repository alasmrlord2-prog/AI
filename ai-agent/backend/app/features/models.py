"""Feature entitlement models."""
from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Feature(Base):
    """Feature catalog entry."""
    __tablename__ = "features"

    key = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant_features = relationship("TenantFeature", back_populates="feature", lazy="select")

    def __repr__(self) -> str:
        return f"<Feature(key={self.key}, name={self.name})>"


class TenantFeature(Base):
    """Feature enablement per tenant."""
    __tablename__ = "tenant_features"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True)
    feature_key = Column(String(100), ForeignKey("features.key"), primary_key=True)
    enabled = Column(Boolean, default=True, nullable=False)
    limits = Column(JSON, nullable=True)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", lazy="select")
    feature = relationship("Feature", back_populates="tenant_features", lazy="select")

    def __repr__(self) -> str:
        return f"<TenantFeature(tenant_id={self.tenant_id}, feature={self.feature_key}, enabled={self.enabled})>"


class FeatureUsageCounter(Base):
    """Usage counters per tenant feature."""
    __tablename__ = "feature_usage_counters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    feature_key = Column(String(100), ForeignKey("features.key"), nullable=False, index=True)
    counter_key = Column(String(100), nullable=False, index=True)
    value = Column(BigInteger, default=0)
    reset_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<FeatureUsageCounter(tenant_id={self.tenant_id}, feature={self.feature_key}, "
            f"counter={self.counter_key}, value={self.value})>"
        )
