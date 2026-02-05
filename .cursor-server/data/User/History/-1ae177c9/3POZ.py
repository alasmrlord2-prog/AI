"""Workflow Triggers from CRM events - Subscription, User, Tenant events."""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import json

from app.identity.models import Tenant, User, TenantUser
from app.subscription.models import Subscription
from app.audit.models import AuditLog


class WorkflowTriggerService:
    """Service for triggering workflows based on CRM events."""

    # Event types
    EVENT_SUBSCRIPTION_EXPIRED = "subscription.expired"
    EVENT_SUBSCRIPTION_EXPIRING_SOON = "subscription.expiring_soon"
    EVENT_SUBSCRIPTION_ACTIVATED = "subscription.activated"
    EVENT_SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    EVENT_USER_ADDED = "user.added"
    EVENT_USER_DISABLED = "user.disabled"
    EVENT_USER_REMOVED = "user.removed"
    EVENT_TENANT_CREATED = "tenant.created"
    EVENT_TENANT_SUSPENDED = "tenant.suspended"
    EVENT_USAGE_LIMIT_REACHED = "usage.limit_reached"
    EVENT_USAGE_WARNING = "usage.warning"

    @staticmethod
    def check_subscription_expiry_triggers(db: Session) -> List[Dict[str, Any]]:
        """Check for subscription expiry events and return triggers."""
        triggers = []
        now = datetime.utcnow()

        # Get subscriptions expiring in next 7 days
        expiring_soon = db.query(Subscription).filter(
            Subscription.status.in_(["active", "trial"]),
            Subscription.end_at > now,
            Subscription.end_at <= datetime(now.year, now.month, now.day + 7)
        ).all()

        for subscription in expiring_soon:
            days_until = (subscription.end_at - now).days
            triggers.append({
                "event": WorkflowTriggerService.EVENT_SUBSCRIPTION_EXPIRING_SOON,
                "tenant_id": str(subscription.tenant_id),
                "subscription_id": str(subscription.id),
                "metadata": {
                    "days_until_expiry": days_until,
                    "plan_name": subscription.plan.name if subscription.plan else None,
                    "end_at": subscription.end_at.isoformat()
                }
            })

        # Get expired subscriptions (within grace period)
        expired = db.query(Subscription).filter(
            Subscription.status.in_(["active", "trial"]),
            Subscription.end_at < now,
            Subscription.grace_end_at > now if Subscription.grace_end_at else False
        ).all()

        for subscription in expired:
            triggers.append({
                "event": WorkflowTriggerService.EVENT_SUBSCRIPTION_EXPIRED,
                "tenant_id": str(subscription.tenant_id),
                "subscription_id": str(subscription.id),
                "metadata": {
                    "plan_name": subscription.plan.name if subscription.plan else None,
                    "end_at": subscription.end_at.isoformat(),
                    "grace_end_at": subscription.grace_end_at.isoformat() if subscription.grace_end_at else None
                }
            })

        return triggers

    @staticmethod
    def trigger_on_user_added(
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        role: str = "member"
    ) -> Dict[str, Any]:
        """Trigger workflow when user is added to tenant."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        user = db.query(User).filter(User.id == user_id).first()

        if not tenant or not user:
            return None

        return {
            "event": WorkflowTriggerService.EVENT_USER_ADDED,
            "tenant_id": str(tenant_id),
            "user_id": str(user_id),
            "metadata": {
                "tenant_name": tenant.name,
                "user_email": user.email,
                "user_name": user.full_name,
                "role": role
            }
        }

    @staticmethod
    def trigger_on_user_disabled(
        db: Session,
        tenant_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Trigger workflow when user is disabled."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        user = db.query(User).filter(User.id == user_id).first()

        if not tenant or not user:
            return None

        return {
            "event": WorkflowTriggerService.EVENT_USER_DISABLED,
            "tenant_id": str(tenant_id),
            "user_id": str(user_id),
            "metadata": {
                "tenant_name": tenant.name,
                "user_email": user.email,
                "user_name": user.full_name
            }
        }

    @staticmethod
    def trigger_on_usage_limit_reached(
        db: Session,
        subscription_id: UUID,
        resource_type: str,
        current_usage: int,
        limit: int
    ) -> Dict[str, Any]:
        """Trigger workflow when usage limit is reached."""
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            return None

        return {
            "event": WorkflowTriggerService.EVENT_USAGE_LIMIT_REACHED,
            "tenant_id": str(subscription.tenant_id),
            "subscription_id": str(subscription_id),
            "metadata": {
                "resource_type": resource_type,
                "current_usage": current_usage,
                "limit": limit,
                "plan_name": subscription.plan.name if subscription.plan else None
            }
        }

    @staticmethod
    def trigger_on_usage_warning(
        db: Session,
        subscription_id: UUID,
        resource_type: str,
        current_usage: int,
        limit: int,
        threshold_percentage: float
    ) -> Dict[str, Any]:
        """Trigger workflow when usage warning threshold is reached."""
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            return None

        return {
            "event": WorkflowTriggerService.EVENT_USAGE_WARNING,
            "tenant_id": str(subscription.tenant_id),
            "subscription_id": str(subscription_id),
            "metadata": {
                "resource_type": resource_type,
                "current_usage": current_usage,
                "limit": limit,
                "threshold_percentage": threshold_percentage,
                "plan_name": subscription.plan.name if subscription.plan else None
            }
        }

    @staticmethod
    def trigger_on_subscription_activated(
        db: Session,
        subscription_id: UUID
    ) -> Dict[str, Any]:
        """Trigger workflow when subscription is activated."""
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            return None

        return {
            "event": WorkflowTriggerService.EVENT_SUBSCRIPTION_ACTIVATED,
            "tenant_id": str(subscription.tenant_id),
            "subscription_id": str(subscription_id),
            "metadata": {
                "plan_name": subscription.plan.name if subscription.plan else None,
                "start_at": subscription.start_at.isoformat(),
                "end_at": subscription.end_at.isoformat()
            }
        }

    @staticmethod
    def trigger_on_tenant_created(
        db: Session,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Trigger workflow when tenant is created."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return None

        return {
            "event": WorkflowTriggerService.EVENT_TENANT_CREATED,
            "tenant_id": str(tenant_id),
            "metadata": {
                "tenant_name": tenant.name,
                "tenant_type": tenant.type,
                "contact_email": tenant.contact_email
            }
        }

