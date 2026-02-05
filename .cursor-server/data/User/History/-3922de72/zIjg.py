#!/usr/bin/env python3
"""Quick script to create default admin user."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.identity.service import IdentityService
from app.identity.schemas import UserCreate, TenantCreate

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if users exist
    user_count = IdentityService.count_users(db)
    
    if user_count > 0:
        print(f"✅ Users already exist ({user_count} users)")
        users = IdentityService.list_users(db, limit=10)
        for user in users:
            print(f"   - {user.email} (status: {user.status})")
    else:
        print("📦 No users found. Creating default admin user...")
        
        # Create tenant
        tenant = IdentityService.create_tenant(
            db,
            TenantCreate(
                name="Default Organization",
                type="company",
                contact_email="admin@example.com",
                contact_phone="+1234567890"
            )
        )
        print(f"✅ Tenant created: {tenant.name}")
        
        # Create user with default password: admin123
        user = IdentityService.create_user(
            db,
            UserCreate(
                email="admin@example.com",
                password="admin123",
                full_name="Admin User",
                tenant_id=tenant.id
            )
        )
        user.status = "active"
        user.email_verified = True
        db.commit()
        print(f"✅ User created: {user.email}")
        
        # Add user as owner
        IdentityService.add_user_to_tenant(db, tenant.id, user.id, role="owner")
        print(f"✅ User added as tenant owner")
        
        print("\n" + "="*50)
        print("🎉 Default admin user created!")
        print("="*50)
        print(f"Email: admin@example.com")
        print(f"Password: admin123")
        print("="*50)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

