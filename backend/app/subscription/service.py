"""Subscription Service - Plans, Subscriptions, Usage management."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.subscription.models import Plan, Subscription, UsageCounter, UsageQuota
from app.subscription.schemas import PlanCreate, SubscriptionCreate, UsageCounterCreate
from app.identity.models import Tenant


class SubscriptionService:
    """Service for managing subscriptions and usage."""

    @staticmethod
    def create_plan(db: Session, plan_data: PlanCreate) -> Plan:
        """Create a new plan."""
        plan = Plan(
            name=plan_data.name,
            description=plan_data.description,
            price_monthly=plan_data.price_monthly,
            price_yearly=plan_data.price_yearly,
            max_users=plan_data.max_users,
            max_requests=plan_data.max_requests,
            max_tokens=plan_data.max_tokens,
            max_storage_gb=plan_data.max_storage_gb,
            max_workflow_runs=plan_data.max_workflow_runs,
            max_agents=plan_data.max_agents,
            max_log_volume_gb=plan_data.max_log_volume_gb,
            features_json=plan_data.features_json,
            status="active",
            is_public=True
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: UUID) -> Optional[Plan]:
        """Get plan by ID."""
        return db.query(Plan).filter(Plan.id == plan_id).first()

    @staticmethod
    def get_active_plans(db: Session) -> List[Plan]:
        """Get all active public plans."""
        return db.query(Plan).filter(
            Plan.status == "active",
            Plan.is_public == True
        ).all()

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

        return subscription

    @staticmethod
    def _create_quotas_from_plan(db: Session, subscription_id: UUID, plan: Plan):
        """Create usage quotas from plan limits."""
        resource_mappings = {
            "requests": plan.max_requests,
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
        # Get current period (monthly)
        now = datetime.utcnow()
        period_start = datetime(now.year, now.month, 1)
        period_end = (period_start + timedelta(days=32)).replace(day=1)

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
    def get_usage(
        db: Session,
        subscription_id: UUID,
        resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage for subscription."""
        now = datetime.utcnow()
        period_start = datetime(now.year, now.month, 1)
        period_end = (period_start + timedelta(days=32)).replace(day=1)

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

