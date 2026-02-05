"""Subscription Schemas - Plans, Subscriptions, Usage."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# Plan Feature Schemas
class PlanFeatureBase(BaseModel):
    feature_key: str
    enabled: bool = True
    limit_value: Optional[int] = None
    unit: Optional[str] = None


class PlanFeatureCreate(PlanFeatureBase):
    pass


class PlanFeatureResponse(PlanFeatureBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Plan Schemas
class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    plan_type: str = "company"
    price_monthly: Optional[Decimal] = None
    price_yearly: Optional[Decimal] = None
    max_users: Optional[int] = None
    max_requests: Optional[int] = None
    max_requests_daily: Optional[int] = None
    max_tokens: Optional[int] = None
    max_storage_gb: Optional[Decimal] = None
    max_workflow_runs: Optional[int] = None
    max_agents: Optional[int] = None
    max_log_volume_gb: Optional[Decimal] = None
    max_devices: Optional[int] = None
    log_retention_days: Optional[int] = None
    features_json: Optional[Dict[str, Any]] = None
    plan_features: Optional[List[PlanFeatureCreate]] = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    plan_type: Optional[str] = None
    price_monthly: Optional[Decimal] = None
    price_yearly: Optional[Decimal] = None
    max_users: Optional[int] = None
    max_requests: Optional[int] = None
    max_requests_daily: Optional[int] = None
    max_tokens: Optional[int] = None
    max_storage_gb: Optional[Decimal] = None
    max_workflow_runs: Optional[int] = None
    max_agents: Optional[int] = None
    max_log_volume_gb: Optional[Decimal] = None
    max_devices: Optional[int] = None
    log_retention_days: Optional[int] = None
    features_json: Optional[Dict[str, Any]] = None
    plan_features: Optional[List[PlanFeatureCreate]] = None
    status: Optional[str] = None
    is_public: Optional[bool] = None


class PlanResponse(PlanBase):
    id: UUID
    status: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    plan_features: Optional[List[PlanFeatureResponse]] = None

    class Config:
        from_attributes = True


# Subscription Schemas
class SubscriptionBase(BaseModel):
    tenant_id: UUID
    plan_id: UUID
    start_at: datetime
    end_at: datetime
    renewal_type: str = "manual"
    grace_end_at: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan_id: Optional[UUID] = None
    end_at: Optional[datetime] = None
    grace_end_at: Optional[datetime] = None
    renewal_type: Optional[str] = None
    status: Optional[str] = None


class SubscriptionResponse(SubscriptionBase):
    id: UUID
    status: str
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    plan: Optional[PlanResponse] = None

    class Config:
        from_attributes = True


# UsageCounter Schemas
class UsageCounterBase(BaseModel):
    subscription_id: UUID
    resource_type: str
    value: int
    period_start: datetime
    period_end: datetime


class UsageCounterCreate(UsageCounterBase):
    pass


class UsageCounterUpdate(BaseModel):
    value: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class UsageCounterResponse(UsageCounterBase):
    id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True


# UsageQuota Schemas
class UsageQuotaBase(BaseModel):
    subscription_id: UUID
    resource_type: str
    limit: Optional[int] = None
    warning_threshold: Decimal = Field(default=Decimal("80.0"), decimal_places=2)


class UsageQuotaCreate(UsageQuotaBase):
    pass


class UsageQuotaResponse(UsageQuotaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Subscription Status Check
class SubscriptionStatusResponse(BaseModel):
    is_active: bool
    is_expired: bool
    is_in_grace: bool
    days_until_expiry: Optional[int] = None
    subscription: SubscriptionResponse
    usage: Dict[str, Any] = {}  # Current usage per resource type
    limits: Dict[str, Any] = {}  # Limits per resource type

