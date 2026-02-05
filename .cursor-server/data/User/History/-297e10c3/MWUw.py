"""CRM Service - Facade for tenant dashboard and management."""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.identity import service as identity_service
from app.subscription import service as subscription_service
from app.audit import service as audit_service
from app.access import service as access_service
from app.identity.models import Tenant, User, TenantUser
from app.subscription.models import Subscription


class CRMService:
    """Service for CRM operations - aggregates data from multiple modules."""

    @staticmethod
    def get_tenant_dashboard(
        db: Session,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Get comprehensive tenant dashboard data."""
        # Get tenant
        tenant = identity_service.IdentityService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            return None

        # Get subscription
        subscription_status = subscription_service.SubscriptionService.check_subscription_status(
            db, tenant_id
        )
        subscription = subscription_status.get("subscription")

        # Get users
        tenant_users = identity_service.IdentityService.get_tenant_users(db, tenant_id)
        users_data = []
        for tu in tenant_users:
            user = identity_service.IdentityService.get_user_by_id(db, tu.user_id)
            if user:
                users_data.append({
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": tu.role,
                    "status": tu.status,
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
                })

        # Get usage
        usage = {}
        limits = {}
        if subscription:
            usage = subscription_service.SubscriptionService.get_usage(db, subscription.id)
            if subscription.plan:
                plan = subscription.plan
                limits = {
                    "requests": plan.max_requests,
                    "tokens": plan.max_tokens,
                    "storage_gb": plan.max_storage_gb,
                    "workflow_runs": plan.max_workflow_runs,
                    "agents": plan.max_agents,
                    "log_volume_gb": plan.max_log_volume_gb,
                }

        # Get recent audit logs
        from app.audit.schemas import AuditLogQuery
        audit_query = AuditLogQuery(
            tenant_id=tenant_id,
            limit=10,
            offset=0
        )
        recent_logs, _ = audit_service.AuditService.query_audit_logs(db, audit_query)

        return {
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name,
                "type": tenant.type,
                "status": tenant.status,
                "contact_email": tenant.contact_email,
                "contact_phone": tenant.contact_phone,
                "created_at": tenant.created_at.isoformat() if tenant.created_at else None
            },
            "subscription": {
                "id": str(subscription.id) if subscription else None,
                "plan_name": subscription.plan.name if subscription and subscription.plan else None,
                "status": subscription_status.get("status", "inactive"),
                "is_active": subscription_status.get("is_active", False),
                "is_expired": subscription_status.get("is_expired", True),
                "is_in_grace": subscription_status.get("is_in_grace", False),
                "days_until_expiry": subscription_status.get("days_until_expiry"),
                "start_at": subscription.start_at.isoformat() if subscription else None,
                "end_at": subscription.end_at.isoformat() if subscription else None
            },
            "users": users_data,
            "usage": usage,
            "limits": limits,
            "recent_activity": [
                {
                    "action": log.action,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in recent_logs[:10]
            ]
        }

    @staticmethod
    def list_tenants(
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """List all tenants with summary info."""
        from app.identity.models import Tenant
        tenants = db.query(Tenant).offset(offset).limit(limit).all()
        total = db.query(Tenant).count()

        tenants_data = []
        for tenant in tenants:
            # Get subscription status
            subscription_status = subscription_service.SubscriptionService.check_subscription_status(
                db, tenant.id
            )
            subscription = subscription_status.get("subscription")

            # Count users
            tenant_users = identity_service.IdentityService.get_tenant_users(db, tenant.id)
            user_count = len(tenant_users)

            tenants_data.append({
                "id": str(tenant.id),
                "name": tenant.name,
                "type": tenant.type,
                "status": tenant.status,
                "subscription_status": subscription_status.get("status", "inactive"),
                "plan_name": subscription.plan.name if subscription and subscription.plan else None,
                "user_count": user_count,
                "days_until_expiry": subscription_status.get("days_until_expiry"),
                "created_at": tenant.created_at.isoformat() if tenant.created_at else None
            })

        return tenants_data, total

