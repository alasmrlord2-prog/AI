#!/usr/bin/env python3
"""Script to setup initial data for CRM + AAA system."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine, Base, engine
from app.identity.service import IdentityService
from app.identity.schemas import UserCreate, TenantCreate
from app.subscription.service import SubscriptionService
from app.subscription.schemas import PlanCreate, SubscriptionCreate, PlanFeatureCreate
from app.access.service import AccessService
from app.access.schemas import RoleCreate, PermissionCreate
from datetime import datetime, timedelta
import getpass

# Create tables if they don't exist
print("📦 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created")


def setup_initial_data():
    """Setup initial data: Tenant, User, Plan, Subscription, Roles, Permissions."""
    # Create tables if they don't exist
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created\n")
    
    db = SessionLocal()
    
    try:
        print("🚀 Starting initial data setup...\n")
        
        # 1. Create Tenant
        print("1️⃣ Creating Tenant...")
        tenant_email = input("Enter tenant contact email (default: admin@example.com): ").strip() or "admin@example.com"
        tenant_name = input("Enter tenant name (default: Admin Organization): ").strip() or "Admin Organization"
        
        tenant_data = TenantCreate(
            name=tenant_name,
            type="company",
            contact_email=tenant_email,
            contact_phone="+1234567890"
        )
        tenant = IdentityService.create_tenant(db, tenant_data)
        print(f"   ✅ Tenant created: {tenant.id} - {tenant.name}\n")
        
        # 2. Create User
        print("2️⃣ Creating Admin User...")
        user_email = input("Enter admin email (default: admin@example.com): ").strip() or "admin@example.com"
        password = getpass.getpass("Enter admin password (min 8 chars): ")
        if len(password) < 8:
            print("   ❌ Password must be at least 8 characters!")
            return
        
        user_data = UserCreate(
            email=user_email,
            password=password,
            full_name="Super Admin",
            tenant_id=tenant.id
        )
        user = IdentityService.create_user(db, user_data)
        user.status = "active"
        user.email_verified = True
        db.commit()
        print(f"   ✅ User created: {user.id} - {user.email}\n")
        
        # 3. Add User as Owner
        print("3️⃣ Adding User as Tenant Owner...")
        IdentityService.add_user_to_tenant(db, tenant.id, user.id, role="owner")
        print(f"   ✅ User added as owner\n")
        
        # 4. Create Plans
        print("4️⃣ Creating Plans...")
        plans_data = [
            # User Plans
            PlanCreate(
                name="Free",
                plan_type="user",
                description="Free User Plan - Basic access",
                price_monthly=0,
                max_users=1,
                max_requests_daily=100,
                max_devices=1,
                log_retention_days=7,
                plan_features=[
                    PlanFeatureCreate(feature_key="auth.email_password", enabled=True),
                    PlanFeatureCreate(feature_key="logs.login", enabled=True),
                ],
            ),
            PlanCreate(
                name="Pro User",
                plan_type="user",
                description="Pro User Plan - Extended usage",
                price_monthly=19.99,
                max_users=1,
                max_requests=10000,
                max_devices=5,
                log_retention_days=30,
                plan_features=[
                    PlanFeatureCreate(feature_key="auth.email_password", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa", enabled=True),
                    PlanFeatureCreate(feature_key="auth.social_login", enabled=True),
                    PlanFeatureCreate(feature_key="logs.export", enabled=True),
                ],
            ),
            PlanCreate(
                name="Power User",
                plan_type="user",
                description="Power User Plan - Advanced access",
                price_monthly=49.99,
                max_users=1,
                max_requests=100000,
                max_devices=None,
                log_retention_days=90,
                plan_features=[
                    PlanFeatureCreate(feature_key="auth.email_password", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa_required", enabled=True),
                    PlanFeatureCreate(feature_key="auth.social_login", enabled=True),
                    PlanFeatureCreate(feature_key="auth.api_keys", enabled=True),
                    PlanFeatureCreate(feature_key="logs.export", enabled=True),
                    PlanFeatureCreate(feature_key="logs.audit_full", enabled=True),
                ],
            ),
            # Company Plans
            PlanCreate(
                name="Starter Company",
                plan_type="company",
                description="Starter Company Plan - Small teams",
                price_monthly=99.99,
                max_users=5,
                max_requests=50000,
                log_retention_days=30,
                plan_features=[
                    PlanFeatureCreate(feature_key="auth.email_password", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa", enabled=True),
                    PlanFeatureCreate(feature_key="roles.predefined", enabled=True),
                    PlanFeatureCreate(feature_key="logs.audit", enabled=True),
                ],
            ),
            PlanCreate(
                name="Business Company",
                plan_type="company",
                description="Business Company Plan - Growing teams",
                price_monthly=299.99,
                max_users=25,
                max_requests=500000,
                log_retention_days=90,
                plan_features=[
                    PlanFeatureCreate(feature_key="auth.email_password", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa_required", enabled=True),
                    PlanFeatureCreate(feature_key="auth.sso", enabled=True),
                    PlanFeatureCreate(feature_key="roles.custom", enabled=True),
                    PlanFeatureCreate(feature_key="policies.pbac", enabled=True),
                    PlanFeatureCreate(feature_key="logs.audit", enabled=True),
                    PlanFeatureCreate(feature_key="logs.export", enabled=True),
                    PlanFeatureCreate(feature_key="integrations.siem_export", enabled=True),
                    PlanFeatureCreate(feature_key="integrations.webhooks", enabled=True),
                ],
            ),
            PlanCreate(
                name="Enterprise",
                plan_type="company",
                description="Enterprise Plan - Unlimited",
                price_monthly=999.99,
                max_users=None,  # Unlimited
                max_requests=None,
                log_retention_days=None,
                plan_features=[
                    PlanFeatureCreate(feature_key="auth.email_password", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa", enabled=True),
                    PlanFeatureCreate(feature_key="auth.mfa_required", enabled=True),
                    PlanFeatureCreate(feature_key="auth.sso", enabled=True),
                    PlanFeatureCreate(feature_key="auth.hardware_mfa", enabled=True),
                    PlanFeatureCreate(feature_key="roles.custom", enabled=True),
                    PlanFeatureCreate(feature_key="policies.abac", enabled=True),
                    PlanFeatureCreate(feature_key="logs.audit_immutable", enabled=True),
                    PlanFeatureCreate(feature_key="logs.export", enabled=True),
                    PlanFeatureCreate(feature_key="integrations.siem_export", enabled=True),
                    PlanFeatureCreate(feature_key="integrations.webhooks", enabled=True),
                    PlanFeatureCreate(feature_key="integrations.custom_api", enabled=True),
                ],
            ),
        ]
        
        created_plans = []
        for plan_data in plans_data:
            plan = SubscriptionService.create_plan(db, plan_data)
            created_plans.append(plan)
            print(f"   ✅ Plan created: {plan.name}")
        
        print()
        
        # 5. Create Subscription (Enterprise Plan)
        print("5️⃣ Creating Subscription...")
        enterprise_plan = next((p for p in created_plans if p.name == "Enterprise"), created_plans[0])
        
        subscription_data = SubscriptionCreate(
            tenant_id=tenant.id,
            plan_id=enterprise_plan.id,
            start_at=datetime.utcnow(),
            end_at=datetime.utcnow() + timedelta(days=365),
            grace_end_at=datetime.utcnow() + timedelta(days=380),
            renewal_type="manual"
        )
        subscription = SubscriptionService.create_subscription(db, subscription_data)
        print(f"   ✅ Subscription created: {subscription.id} - {enterprise_plan.name}\n")
        
        # 6. Create Default Roles
        print("6️⃣ Creating Default Roles...")
        roles_data = [
            RoleCreate(name="owner", description="Tenant Owner - Full access"),
            RoleCreate(name="admin", description="Administrator - Manage users and settings"),
            RoleCreate(name="member", description="Member - Standard user access"),
            RoleCreate(name="viewer", description="Viewer - Read-only access")
        ]
        
        for role_data in roles_data:
            try:
                role = AccessService.create_role(db, role_data)
                role.is_system = True  # Mark as system role
                db.commit()
                print(f"   ✅ Role created: {role.name}")
            except Exception as e:
                print(f"   ⚠️  Role {role_data.name} might already exist: {e}")
        
        print()
        
        # 7. Create Default Permissions
        print("7️⃣ Creating Default Permissions...")
        permissions_data = [
            PermissionCreate(name="access_dashboard", resource="dashboard", action="read", description="Access dashboard"),
            PermissionCreate(name="manage_users", resource="users", action="write", description="Manage users"),
            PermissionCreate(name="run_agent", resource="agent", action="execute", description="Run AI agent"),
            PermissionCreate(name="execute_workflow", resource="workflow", action="execute", description="Execute workflows"),
            PermissionCreate(name="view_logs", resource="logs", action="read", description="View logs"),
            PermissionCreate(name="modify_settings", resource="settings", action="write", description="Modify settings"),
            PermissionCreate(name="use_security_tools", resource="security", action="execute", description="Use security tools"),
            PermissionCreate(name="use_cicd", resource="cicd", action="execute", description="Use CI/CD features")
        ]
        
        for perm_data in permissions_data:
            try:
                perm = AccessService.create_permission(db, perm_data)
                print(f"   ✅ Permission created: {perm.name}")
            except Exception as e:
                print(f"   ⚠️  Permission {perm_data.name} might already exist: {e}")
        
        print()
        
        print("=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print(f"\n📧 Login Credentials:")
        print(f"   Email: {user_email}")
        print(f"   Password: [the password you entered]")
        print(f"\n🌐 Access URLs:")
        print(f"   Frontend: http://localhost:3000")
        print(f"   Backend API: http://localhost:8000")
        print(f"   API Docs: http://localhost:8000/docs")
        print(f"\n📋 Tenant ID: {tenant.id}")
        print(f"👤 User ID: {user.id}")
        print(f"📦 Subscription ID: {subscription.id}")
        print("\n✅ You can now login and start using the system!")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    setup_initial_data()

