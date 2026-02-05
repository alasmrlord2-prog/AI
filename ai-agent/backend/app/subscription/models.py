"""Subscription Models - Plans, Subscriptions, Usage Counters (Resource-based)."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer, Numeric, BigInteger, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Plan(Base):
    """Plan model - subscription plans/packages."""
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    plan_type = Column(String(50), default="company")  # company, user
    price_monthly = Column(Numeric(10, 2), nullable=True)
    price_yearly = Column(Numeric(10, 2), nullable=True)
    
    # Limits
    max_users = Column(Integer, nullable=True)  # NULL = unlimited
    max_requests = Column(BigInteger, nullable=True)  # NULL = unlimited
    max_requests_daily = Column(BigInteger, nullable=True)  # NULL = unlimited
    max_tokens = Column(BigInteger, nullable=True)  # NULL = unlimited
    max_storage_gb = Column(Numeric(10, 2), nullable=True)  # NULL = unlimited
    max_workflow_runs = Column(Integer, nullable=True)  # NULL = unlimited
    max_agents = Column(Integer, nullable=True)  # NULL = unlimited
    max_log_volume_gb = Column(Numeric(10, 2), nullable=True)  # NULL = unlimited
    max_devices = Column(Integer, nullable=True)  # NULL = unlimited
    log_retention_days = Column(Integer, nullable=True)  # NULL = unlimited
    
    # Features (JSON)
    features_json = Column(JSON, nullable=True)  # {"ai_debugger": true, "cicd": false, ...}
    
    # Status
    status = Column(String(50), default="active")  # active, deprecated
    is_public = Column(Boolean, default=True)  # Visible to customers
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    plan_features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plan(id={self.id}, name={self.name}, status={self.status})>"


class PlanFeature(Base):
    """PlanFeature model - feature entitlements per plan."""
    __tablename__ = "plan_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False, index=True)
    feature_key = Column(String(100), nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    limit_value = Column(BigInteger, nullable=True)
    unit = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("Plan", back_populates="plan_features")

    __table_args__ = (
        Index("idx_plan_feature_unique", "plan_id", "feature_key", unique=True),
    )

    def __repr__(self):
        return f"<PlanFeature(plan_id={self.plan_id}, feature_key={self.feature_key}, enabled={self.enabled})>"


class Subscription(Base):
    """Subscription model - tenant subscriptions to plans."""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    
    # Dates
    start_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_at = Column(DateTime, nullable=False)  # This is the expiry date
    grace_end_at = Column(DateTime, nullable=True)  # End of grace period
    renewal_type = Column(String(50), default="manual")  # manual, auto
    
    # Status
    status = Column(String(50), default="trial")  # active, expired, cancelled, trial, suspended
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), nullable=True)  # User ID (avoid circular import)

    # Relationships (lazy loading to avoid circular imports)
    # tenant relationship modified to avoid circular import - using backref instead
    tenant = relationship("Tenant", lazy="select")
    plan = relationship("Plan", back_populates="subscriptions", lazy="select")
    usage_counters = relationship("UsageCounter", back_populates="subscription", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<Subscription(id={self.id}, tenant_id={self.tenant_id}, plan_id={self.plan_id}, status={self.status}, end_at={self.end_at})>"


class UsageCounter(Base):
    """UsageCounter model - Resource-based usage tracking."""
    __tablename__ = "usage_counters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # Resource type and value
    resource_type = Column(String(100), nullable=False)  # "requests", "tokens", "storage_gb", "workflow_runs", "log_volume_gb", "agents"
    value = Column(BigInteger, default=0)
    
    # Period
    period_start = Column(DateTime, nullable=False)  # Start of billing period
    period_end = Column(DateTime, nullable=False)  # End of billing period
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="usage_counters")

    # Composite index for efficient lookups
    __table_args__ = (
        Index("idx_usage_counter_lookup", "subscription_id", "resource_type", "period_start", "period_end"),
    )

    def __repr__(self):
        return f"<UsageCounter(subscription_id={self.subscription_id}, resource_type={self.resource_type}, value={self.value})>"


class UsageEvent(Base):
    """UsageEvent model - event-based usage tracking."""
    __tablename__ = "usage_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    service = Column(String(100), nullable=False)  # "api", "ui", "worker"
    action = Column(String(100), nullable=False)  # "request", "query", "export"
    units = Column(Integer, default=1)
    source = Column(String(100), nullable=True)  # "api", "ui"

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<UsageEvent(tenant_id={self.tenant_id}, action={self.action}, units={self.units})>"


class UsageQuota(Base):
    """UsageQuota model - Defines quotas per resource type for a subscription."""
    __tablename__ = "usage_quotas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # Resource quota
    resource_type = Column(String(100), nullable=False)  # "requests", "tokens", "storage_gb", etc.
    limit = Column(BigInteger, nullable=True)  # NULL = unlimited
    warning_threshold = Column(Numeric(5, 2), default=80.0)  # Percentage (e.g., 80% = warn at 80%)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription")

    def __repr__(self):
        return f"<UsageQuota(subscription_id={self.subscription_id}, resource_type={self.resource_type}, limit={self.limit})>"

