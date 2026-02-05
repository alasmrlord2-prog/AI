"""Subscription Service - Plans, Subscriptions, Usage management."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.subscription.models import Plan, PlanFeature, Subscription, UsageCounter, UsageQuota, UsageEvent
from app.subscription.schemas import PlanCreate, SubscriptionCreate, UsageCounterCreate
from app.identity.models import Tenant
from app.features.models import Feature, TenantFeature


class SubscriptionService:
    """Service for managing subscriptions and usage."""

    @staticmethod
    def create_plan(db: Session, plan_data: PlanCreate) -> Plan:
        """Create a new plan."""
        plan = Plan(
            name=plan_data.name,
            description=plan_data.description,
            plan_type=plan_data.plan_type,
            price_monthly=plan_data.price_monthly,
            price_yearly=plan_data.price_yearly,
            max_users=plan_data.max_users,
            max_requests=plan_data.max_requests,
            max_requests_daily=plan_data.max_requests_daily,
            max_tokens=plan_data.max_tokens,
            max_storage_gb=plan_data.max_storage_gb,
            max_workflow_runs=plan_data.max_workflow_runs,
            max_agents=plan_data.max_agents,
            max_log_volume_gb=plan_data.max_log_volume_gb,
            max_devices=plan_data.max_devices,
            log_retention_days=plan_data.log_retention_days,
            features_json=plan_data.features_json,
            status="active",
            is_public=True
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        if plan_data.plan_features:
            for feature in plan_data.plan_features:
                plan_feature = PlanFeature(
                    plan_id=plan.id,
                    feature_key=feature.feature_key,
                    enabled=feature.enabled,
                    limit_value=feature.limit_value,
                    unit=feature.unit,
                )
                db.add(plan_feature)
            db.commit()
            db.refresh(plan)

        return plan

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: UUID) -> Optional[Plan]:
        """Get plan by ID."""
        return db.query(Plan).filter(Plan.id == plan_id).first()

    @staticmethod
    def get_active_plans(db: Session, plan_type: Optional[str] = None) -> List[Plan]:
        """Get all active public plans."""
        query = db.query(Plan).filter(
            Plan.status == "active",
            Plan.is_public == True
        )
        if plan_type:
            query = query.filter(Plan.plan_type == plan_type)
        return query.all()

    @staticmethod
    def create_subscription(
        db: Session,
        subscription_data: SubscriptionCreate
    ) -> Subscription:
        """Create a new subscription."""
        subscription = Subscription(
            tenant_id=subscription_data.tenant_id,
            plan_id=subscription_data.plan_id,
            start_at=subscription_data.start_at,
            end_at=subscription_data.end_at,
            grace_end_at=subscription_data.grace_end_at,
            renewal_type=subscription_data.renewal_type,
            status="trial" if subscription_data.end_at > datetime.utcnow() else "active"
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        # Create usage quotas from plan limits
        plan = subscription.plan
        if plan:
            SubscriptionService._create_quotas_from_plan(db, subscription.id, plan)
            SubscriptionService._apply_plan_features_to_tenant(db, subscription.tenant_id, plan)

        return subscription

    @staticmethod
    def _create_quotas_from_plan(db: Session, subscription_id: UUID, plan: Plan):
        """Create usage quotas from plan limits."""
        resource_mappings = {
            "requests": plan.max_requests,
            "requests_daily": plan.max_requests_daily,
            "tokens": plan.max_tokens,
            "storage_gb": plan.max_storage_gb,
            "workflow_runs": plan.max_workflow_runs,
            "agents": plan.max_agents,
            "log_volume_gb": plan.max_log_volume_gb,
        }

        for resource_type, limit in resource_mappings.items():
            if limit is not None:
                quota = UsageQuota(
                    subscription_id=subscription_id,
                    resource_type=resource_type,
                    limit=int(limit) if isinstance(limit, (int, float)) else None
                )
                db.add(quota)

        db.commit()

    @staticmethod
    def _apply_plan_features_to_tenant(db: Session, tenant_id: UUID, plan: Plan) -> None:
        """Apply plan feature entitlements to tenant feature flags."""
        plan_features = list(plan.plan_features or [])

        if plan.log_retention_days is not None:
            plan_features.append(
                PlanFeature(
                    plan_id=plan.id,
                    feature_key="logs.retention_days",
                    enabled=True,
                    limit_value=int(plan.log_retention_days),
                    unit="days",
                )
            )

        if plan.max_devices is not None:
            plan_features.append(
                PlanFeature(
                    plan_id=plan.id,
                    feature_key="devices.max",
                    enabled=True,
                    limit_value=int(plan.max_devices),
                    unit="count",
                )
            )

        if not plan_features:
            return

        for plan_feature in plan_features:
            feature = db.query(Feature).filter(Feature.key == plan_feature.feature_key).first()
            if not feature:
                feature = Feature(
                    key=plan_feature.feature_key,
                    name=plan_feature.feature_key,
                    description=f"Auto-created from plan {plan.name}",
                )
                db.add(feature)
                db.flush()

            tenant_feature = db.query(TenantFeature).filter(
                TenantFeature.tenant_id == tenant_id,
                TenantFeature.feature_key == plan_feature.feature_key,
            ).first()

            limits_payload = None
            if plan_feature.limit_value is not None or plan_feature.unit:
                limits_payload = {
                    "limit": plan_feature.limit_value,
                    "unit": plan_feature.unit,
                }

            if tenant_feature:
                tenant_feature.enabled = plan_feature.enabled
                tenant_feature.limits = limits_payload
                tenant_feature.updated_at = datetime.utcnow()
            else:
                tenant_feature = TenantFeature(
                    tenant_id=tenant_id,
                    feature_key=plan_feature.feature_key,
                    enabled=plan_feature.enabled,
                    limits=limits_payload,
                )
                db.add(tenant_feature)

        db.commit()

    @staticmethod
    def get_active_subscription(
        db: Session,
        tenant_id: UUID
    ) -> Optional[Subscription]:
        """Get active subscription for tenant."""
        now = datetime.utcnow()
        return db.query(Subscription).filter(
            Subscription.tenant_id == tenant_id,
            Subscription.status.in_(["active", "trial"]),
            Subscription.end_at >= now
        ).order_by(Subscription.created_at.desc()).first()

    @staticmethod
    def check_subscription_status(
        db: Session,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Check subscription status and return detailed info."""
        subscription = SubscriptionService.get_active_subscription(db, tenant_id)

        if not subscription:
            return {
                "is_active": False,
                "is_expired": True,
                "is_in_grace": False,
                "days_until_expiry": None,
                "subscription": None
            }

        now = datetime.utcnow()
        is_expired = now > subscription.end_at
        is_in_grace = (
            subscription.grace_end_at and
            now > subscription.end_at and
            now <= subscription.grace_end_at
        )
        days_until_expiry = (subscription.end_at - now).days if not is_expired else 0

        return {
            "is_active": subscription.status == "active" and not is_expired,
            "is_expired": is_expired and not is_in_grace,
            "is_in_grace": is_in_grace,
            "days_until_expiry": days_until_expiry,
            "subscription": subscription
        }

    @staticmethod
    def increment_usage(
        db: Session,
        subscription_id: UUID,
        resource_type: str,
        amount: int = 1
    ) -> UsageCounter:
        """Increment usage counter for a resource."""
        now = datetime.utcnow()
        period_start, period_end = SubscriptionService._get_period_window(resource_type, now)

        # Find or create counter
        counter = db.query(UsageCounter).filter(
            UsageCounter.subscription_id == subscription_id,
            UsageCounter.resource_type == resource_type,
            UsageCounter.period_start == period_start,
            UsageCounter.period_end == period_end
        ).first()

        if counter:
            counter.value += amount
            counter.updated_at = now
        else:
            counter = UsageCounter(
                subscription_id=subscription_id,
                resource_type=resource_type,
                value=amount,
                period_start=period_start,
                period_end=period_end
            )
            db.add(counter)

        db.commit()
        db.refresh(counter)
        return counter

    @staticmethod
    def emit_usage_event(
        db: Session,
        tenant_id: UUID,
        user_id: Optional[UUID],
        service: str,
        action: str,
        units: int = 1,
        source: Optional[str] = None
    ) -> UsageEvent:
        """Record a usage event (event-based accounting)."""
        event = UsageEvent(
            tenant_id=tenant_id,
            user_id=user_id,
            service=service,
            action=action,
            units=units,
            source=source
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_usage(
        db: Session,
        subscription_id: UUID,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage for subscription."""
        now = datetime.utcnow()
        period_start, period_end = SubscriptionService._get_period_window(resource_type, now)

        query = db.query(UsageCounter).filter(
            UsageCounter.subscription_id == subscription_id,
            UsageCounter.period_start == period_start,
            UsageCounter.period_end == period_end
        )

        if resource_type:
            query = query.filter(UsageCounter.resource_type == resource_type)

        counters = query.all()

        usage = {}
        for counter in counters:
            usage[counter.resource_type] = counter.value

        return usage

    @staticmethod
    def check_usage_limit(
        db: Session,
        subscription_id: UUID,
        resource_type: str,
        requested_amount: int = 1
    ) -> Dict[str, Any]:
        """Check if usage is within limits."""
        # Get quota
        quota = db.query(UsageQuota).filter(
            UsageQuota.subscription_id == subscription_id,
            UsageQuota.resource_type == resource_type
        ).first()

        if not quota or quota.limit is None:
            return {"allowed": True, "reason": "No limit set"}

        # Get current usage
        usage = SubscriptionService.get_usage(db, subscription_id, resource_type)
        current_usage = usage.get(resource_type, 0)

        # Check limit
        new_usage = current_usage + requested_amount
        allowed = new_usage <= quota.limit

        return {
            "allowed": allowed,
            "current_usage": current_usage,
            "limit": quota.limit,
            "remaining": max(0, quota.limit - current_usage),
            "warning_threshold": quota.warning_threshold,
            "is_warning": current_usage >= (quota.limit * quota.warning_threshold / 100)
        }

    @staticmethod
    def _get_period_window(resource_type: Optional[str], now: datetime) -> tuple[datetime, datetime]:
        """Get period window for usage counters (daily vs monthly)."""
        if resource_type and resource_type.endswith("_daily"):
            period_start = datetime(now.year, now.month, now.day)
            period_end = period_start + timedelta(days=1)
            return period_start, period_end

        period_start = datetime(now.year, now.month, 1)
        period_end = (period_start + timedelta(days=32)).replace(day=1)
        return period_start, period_end

    @staticmethod
    def renew_subscription(
        db: Session,
        subscription_id: UUID,
        new_end_date: datetime
    ) -> Optional[Subscription]:
        """Renew subscription."""
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()

        if not subscription:
            return None

        subscription.end_at = new_end_date
        subscription.status = "active"
        subscription.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(subscription)
        return subscription

