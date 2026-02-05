"""Feature entitlement and usage utilities."""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.features.models import Feature, TenantFeature, FeatureUsageCounter


def get_tenant_feature(
    db: Session,
    tenant_id: str,
    feature_key: str,
) -> Optional[TenantFeature]:
    """Fetch the tenant feature record if enabled and within time window."""
    return (
        db.query(TenantFeature)
        .filter(
            TenantFeature.tenant_id == tenant_id,
            TenantFeature.feature_key == feature_key,
        )
        .first()
    )


def tenant_has_feature(db: Session, tenant_id: str, feature_key: str) -> bool:
    """Check if a tenant has a feature enabled and active."""
    tenant_feature = get_tenant_feature(db, tenant_id, feature_key)
    if not tenant_feature or not tenant_feature.enabled:
        return False
    if tenant_feature.starts_at and tenant_feature.starts_at > datetime.utcnow():
        return False
    if tenant_feature.ends_at and tenant_feature.ends_at < datetime.utcnow():
        return False
    return True


def get_usage_counter(
    db: Session,
    tenant_id: str,
    feature_key: str,
    counter_key: str,
) -> Optional[FeatureUsageCounter]:
    return (
        db.query(FeatureUsageCounter)
        .filter(
            FeatureUsageCounter.tenant_id == tenant_id,
            FeatureUsageCounter.feature_key == feature_key,
            FeatureUsageCounter.counter_key == counter_key,
        )
        .first()
    )


def check_limit(
    db: Session,
    tenant_id: str,
    feature_key: str,
    counter_key: str,
    max_value: Optional[int],
) -> None:
    """Raise if the usage counter exceeds the limit."""
    if max_value is None:
        return

    counter = get_usage_counter(db, tenant_id, feature_key, counter_key)
    current_value = counter.value if counter else 0

    if current_value >= max_value:
        raise ValueError("limit_exceeded")


def increment_counter(
    db: Session,
    tenant_id: str,
    feature_key: str,
    counter_key: str,
    increment_by: int = 1,
    reset_at: Optional[datetime] = None,
) -> FeatureUsageCounter:
    """Increment a usage counter, creating it if needed."""
    counter = get_usage_counter(db, tenant_id, feature_key, counter_key)
    if counter:
        counter.value += increment_by
        if reset_at:
            counter.reset_at = reset_at
    else:
        counter = FeatureUsageCounter(
            tenant_id=tenant_id,
            feature_key=feature_key,
            counter_key=counter_key,
            value=increment_by,
            reset_at=reset_at,
        )
        db.add(counter)

    db.commit()
    db.refresh(counter)
    return counter
