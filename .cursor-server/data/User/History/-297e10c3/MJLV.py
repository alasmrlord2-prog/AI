"""CRM Service - Facade for tenant dashboard and management."""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from app.identity import service as identity_service
from app.subscription import service as subscription_service
from app.audit import service as audit_service
from app.access import service as access_service
from app.identity.models import Tenant, User, TenantUser, Department, Project, APIToken, Session as UserSession
from app.subscription.models import Subscription, UsageCounter
from app.audit.models import AuditLog, LoginLog


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

    @staticmethod
    def get_tenant_users_detailed(
        db: Session,
        tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get detailed users list for tenant with sessions and devices."""
        tenant_users = identity_service.IdentityService.get_tenant_users(db, tenant_id)
        users_data = []
        
        for tu in tenant_users:
            user = identity_service.IdentityService.get_user_by_id(db, tu.user_id)
            if not user:
                continue

            # Get active sessions
            sessions = identity_service.IdentityService.get_active_sessions(db, user.id)
            sessions_data = []
            for session in sessions:
                sessions_data.append({
                    "id": str(session.id),
                    "device_info": session.device_info,
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "last_activity_at": session.last_activity_at.isoformat() if session.last_activity_at else None,
                    "expires_at": session.expires_at.isoformat() if session.expires_at else None
                })

            # Get API tokens
            api_tokens = db.query(APIToken).filter(
                APIToken.user_id == user.id,
                APIToken.tenant_id == tenant_id,
                APIToken.is_active == True
            ).all()
            
            tokens_count = len(api_tokens)

            # Get last login log
            last_login = db.query(LoginLog).filter(
                LoginLog.user_id == user.id,
                LoginLog.status == "success"
            ).order_by(LoginLog.created_at.desc()).first()

            users_data.append({
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": tu.role,
                "status": tu.status,
                "mfa_enabled": user.mfa_enabled,
                "email_verified": user.email_verified,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "last_login_ip": last_login.ip_address if last_login else None,
                "last_login_location": f"{last_login.location_city}, {last_login.location_country}" if last_login and last_login.location_city else None,
                "sessions": sessions_data,
                "active_sessions_count": len(sessions_data),
                "api_tokens_count": tokens_count,
                "created_at": tu.created_at.isoformat() if tu.created_at else None,
                "accepted_at": tu.accepted_at.isoformat() if tu.accepted_at else None
            })

        return users_data

    @staticmethod
    def get_tenant_departments(
        db: Session,
        tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get departments for tenant."""
        departments = db.query(Department).filter(
            Department.tenant_id == tenant_id,
            Department.status == "active"
        ).all()

        departments_data = []
        for dept in departments:
            # Count projects
            projects_count = db.query(Project).filter(
                Project.department_id == dept.id,
                Project.status == "active"
            ).count()

            departments_data.append({
                "id": str(dept.id),
                "name": dept.name,
                "description": dept.description,
                "parent_department_id": str(dept.parent_department_id) if dept.parent_department_id else None,
                "projects_count": projects_count,
                "created_at": dept.created_at.isoformat() if dept.created_at else None
            })

        return departments_data

    @staticmethod
    def get_tenant_projects(
        db: Session,
        tenant_id: UUID,
        department_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get projects for tenant."""
        query = db.query(Project).filter(
            Project.tenant_id == tenant_id,
            Project.status == "active"
        )

        if department_id:
            query = query.filter(Project.department_id == department_id)

        projects = query.all()

        projects_data = []
        for project in projects:
            projects_data.append({
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "department_id": str(project.department_id) if project.department_id else None,
                "status": project.status,
                "created_at": project.created_at.isoformat() if project.created_at else None
            })

        return projects_data

    @staticmethod
    def get_tenant_usage_analytics(
        db: Session,
        tenant_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get usage analytics for tenant."""
        subscription = subscription_service.SubscriptionService.get_active_subscription(db, tenant_id)
        if not subscription:
            return {"error": "No active subscription"}

        # Get usage counters for the period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        counters = db.query(UsageCounter).filter(
            UsageCounter.subscription_id == subscription.id,
            UsageCounter.period_start >= start_date
        ).all()

        # Group by resource type
        usage_by_resource = {}
        for counter in counters:
            if counter.resource_type not in usage_by_resource:
                usage_by_resource[counter.resource_type] = []
            usage_by_resource[counter.resource_type].append({
                "date": counter.period_start.isoformat(),
                "value": counter.value
            })

        # Get current usage
        current_usage = subscription_service.SubscriptionService.get_usage(db, subscription.id)

        # Get limits from plan
        limits = {}
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

        return {
            "current_usage": current_usage,
            "limits": limits,
            "usage_history": usage_by_resource,
            "period_days": days
        }

    @staticmethod
    def get_tenant_incidents(
        db: Session,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get incidents for tenant."""
        # Try to get incidents from audit logs or incidents table
        # This is a flexible implementation that works with or without incidents model
        try:
            # Option 1: Try to use incidents API if available
            from app.api.incidents import service as incidents_service
            # This would require incidents service to have a get_tenant_incidents method
            # For now, return empty list - can be extended later
            return [], 0
        except (ImportError, AttributeError):
            # Option 2: Use audit logs as incidents (security-related events)
            # Filter audit logs for security/error events
            security_actions = ["security_alert", "threat_detected", "unauthorized_access", "error"]
            logs = db.query(AuditLog).filter(
                AuditLog.tenant_id == tenant_id,
                AuditLog.action.in_(security_actions),
                AuditLog.status.in_(["failed", "error"])
            ).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
            
            total = db.query(AuditLog).filter(
                AuditLog.tenant_id == tenant_id,
                AuditLog.action.in_(security_actions),
                AuditLog.status.in_(["failed", "error"])
            ).count()

            incidents_data = []
            for log in logs:
                incidents_data.append({
                    "id": str(log.id),
                    "title": f"{log.action} - {log.resource_type or 'Unknown'}",
                    "severity": "high" if "threat" in log.action or "unauthorized" in log.action else "medium",
                    "status": "open",
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "resolved_at": None
                })

            return incidents_data, total

    @staticmethod
    def get_tenant_audit_logs(
        db: Session,
        tenant_id: UUID,
        limit: int = 100,
        offset: int = 0,
        action: Optional[str] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get audit logs for tenant with filters."""
        query = db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id
        )

        if action:
            query = query.filter(AuditLog.action == action)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

        logs_data = []
        for log in logs:
            logs_data.append({
                "id": str(log.id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "user_id": str(log.user_id) if log.user_id else None,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "endpoint": log.endpoint,
                "status": log.status,
                "error_message": log.error_message,
                "metadata": log.metadata_json,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })

        return logs_data, total

    @staticmethod
    def get_tenant_summary_stats(
        db: Session,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Get summary statistics for tenant."""
        tenant = identity_service.IdentityService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            return None

        # User count
        user_count = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.status == "active"
        ).count()

        # Department count
        dept_count = db.query(Department).filter(
            Department.tenant_id == tenant_id,
            Department.status == "active"
        ).count()

        # Project count
        project_count = db.query(Project).filter(
            Project.tenant_id == tenant_id,
            Project.status == "active"
        ).count()

        # Subscription status
        subscription_status = subscription_service.SubscriptionService.check_subscription_status(
            db, tenant_id
        )

        # Recent activity count (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        activity_count = db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.created_at >= week_ago
        ).count()

        # Active sessions count
        active_sessions = db.query(UserSession).join(User).join(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).count()

        return {
            "user_count": user_count,
            "department_count": dept_count,
            "project_count": project_count,
            "active_sessions": active_sessions,
            "recent_activity_count": activity_count,
            "subscription_status": subscription_status.get("status", "inactive"),
            "is_active": subscription_status.get("is_active", False),
            "days_until_expiry": subscription_status.get("days_until_expiry")
        }

