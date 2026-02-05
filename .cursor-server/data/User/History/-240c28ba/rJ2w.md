# 🚀 دليل البدء السريع - CRM + AAA

## 📋 المتطلبات

- Python 3.9+
- Node.js 18+
- PostgreSQL (أو أي قاعدة بيانات تدعم SQLAlchemy)
- Redis (اختياري - للـ sessions)

---

## 1️⃣ إعداد قاعدة البيانات

### إنشاء قاعدة البيانات

```bash
# PostgreSQL
createdb ai_agent_db

# أو MySQL
mysql -u root -p
CREATE DATABASE ai_agent_db;
```

### تشغيل Migrations

```bash
cd /home/ai/ai-agent/backend

# إذا كنت تستخدم Alembic
alembic upgrade head

# أو إذا كنت تستخدم SQLAlchemy مباشرة
python -c "from app.core.database import Base, engine; Base.metadata.create_all(engine)"
```

---

## 2️⃣ تشغيل Backend

### الطريقة 1: باستخدام start.sh

```bash
cd /home/ai/ai-agent/backend
./start.sh
```

### الطريقة 2: يدوياً

```bash
cd /home/ai/ai-agent/backend

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### التحقق من أن Backend يعمل

```bash
# تحقق من Health Check
curl http://localhost:8000/health

# تحقق من API Docs
# افتح المتصفح: http://localhost:8000/docs
```

---

## 3️⃣ تشغيل Frontend

### الطريقة 1: باستخدام start.sh

```bash
cd /home/ai/ai-agent/frontend
./start.sh
```

### الطريقة 2: يدوياً

```bash
cd /home/ai/ai-agent/frontend

# تثبيت المتطلبات
npm install

# تشغيل Next.js
npm run dev
```

### التحقق من أن Frontend يعمل

افتح المتصفح: http://localhost:3000

---

## 4️⃣ إعداد البيانات الأولية

### إنشاء Super Admin User

```bash
# استخدام Python shell
cd /home/ai/ai-agent/backend
python
```

```python
from app.core.database import SessionLocal
from app.identity.service import IdentityService
from app.identity.schemas import UserCreate, TenantCreate
from app.subscription.service import SubscriptionService
from app.subscription.schemas import PlanCreate, SubscriptionCreate
from datetime import datetime, timedelta
from uuid import uuid4

db = SessionLocal()

# 1. إنشاء Tenant
tenant_data = TenantCreate(
    name="Admin Organization",
    type="company",
    contact_email="admin@example.com",
    contact_phone="+1234567890"
)
tenant = IdentityService.create_tenant(db, tenant_data)
print(f"✅ Tenant created: {tenant.id}")

# 2. إنشاء User
user_data = UserCreate(
    email="admin@example.com",
    password="admin123456",  # غيّر هذا!
    full_name="Super Admin",
    tenant_id=tenant.id
)
user = IdentityService.create_user(db, user_data)
user.status = "active"
db.commit()
print(f"✅ User created: {user.id}")

# 3. إضافة User كـ Owner للـ Tenant
IdentityService.add_user_to_tenant(db, tenant.id, user.id, role="owner")
print(f"✅ User added as owner")

# 4. إنشاء Plan
plan_data = PlanCreate(
    name="Enterprise",
    description="Enterprise Plan",
    price_monthly=999.99,
    max_users=None,  # Unlimited
    max_requests=1000000,
    max_tokens=100000000,
    max_storage_gb=1000,
    features_json={
        "ai_debugger": True,
        "cicd": True,
        "security": True,
        "threat_detection": True
    }
)
plan = SubscriptionService.create_plan(db, plan_data)
print(f"✅ Plan created: {plan.id}")

# 5. إنشاء Subscription
subscription_data = SubscriptionCreate(
    tenant_id=tenant.id,
    plan_id=plan.id,
    start_at=datetime.utcnow(),
    end_at=datetime.utcnow() + timedelta(days=365),
    grace_end_at=datetime.utcnow() + timedelta(days=380),
    renewal_type="manual"
)
subscription = SubscriptionService.create_subscription(db, subscription_data)
print(f"✅ Subscription created: {subscription.id}")

db.close()
print("\n🎉 Setup complete! You can now login with:")
print(f"   Email: admin@example.com")
print(f"   Password: admin123456")
```

---

## 5️⃣ الوصول للنظام

### تسجيل الدخول

1. افتح: http://localhost:3000/login
2. استخدم:
   - Email: `admin@example.com`
   - Password: `admin123456`

### الوصول للصفحات

#### CRM Pages:
- **قائمة Tenants**: http://localhost:3000/crm/tenants
- **Tenant Dashboard**: http://localhost:3000/crm/tenants/{tenant_id}
- **Users Management**: http://localhost:3000/crm/tenants/{tenant_id}/users
- **Subscription**: http://localhost:3000/crm/tenants/{tenant_id}/subscription

#### IAM Pages:
- **Roles**: http://localhost:3000/iam/roles
- **Permissions**: http://localhost:3000/iam/permissions
- **Policies**: http://localhost:3000/iam/policies
- **Access Control**: http://localhost:3000/iam/access-control

---

## 6️⃣ API Endpoints

### CRM API

```bash
# قائمة Tenants
GET http://localhost:8000/api/crm/tenants

# Tenant Dashboard
GET http://localhost:8000/api/crm/tenants/{tenant_id}/dashboard

# Users
GET http://localhost:8000/api/crm/tenants/{tenant_id}/users

# Usage Analytics
GET http://localhost:8000/api/crm/tenants/{tenant_id}/usage?days=30
```

### Identity API

```bash
# Login
POST http://localhost:8000/api/identity/login
{
  "email": "admin@example.com",
  "password": "admin123456"
}

# Create User
POST http://localhost:8000/api/identity/users
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "tenant_id": "tenant-uuid"
}
```

### Subscription API

```bash
# Get Plans
GET http://localhost:8000/api/subscription/plans

# Get Subscription Status
GET http://localhost:8000/api/subscription/tenants/{tenant_id}/subscription

# Check Usage
GET http://localhost:8000/api/subscription/subscriptions/{subscription_id}/usage
```

---

## 7️⃣ اختبار النظام

### اختبار Login

```bash
curl -X POST http://localhost:8000/api/identity/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123456"
  }'
```

### اختبار CRM API (مع Token)

```bash
# احصل على Token من Login
TOKEN="your-jwt-token-here"

# قائمة Tenants
curl http://localhost:8000/api/crm/tenants \
  -H "Authorization: Bearer $TOKEN"
```

---

## 8️⃣ Troubleshooting

### Backend لا يعمل

```bash
# تحقق من الـ Port
lsof -i :8000

# تحقق من الـ Logs
cd /home/ai/ai-agent/backend
tail -f logs/app.log
```

### Frontend لا يعمل

```bash
# تحقق من الـ Port
lsof -i :3000

# تحقق من الـ Logs
cd /home/ai/ai-agent/frontend
npm run dev
```

### مشاكل قاعدة البيانات

```bash
# تحقق من الاتصال
psql -U postgres -d ai_agent_db -c "SELECT 1;"

# تحقق من الـ Tables
psql -U postgres -d ai_agent_db -c "\dt"
```

### مشاكل CORS

تأكد من أن `CORS_ORIGINS` في `backend/app/core/config.py` يحتوي على:
```python
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
```

---

## 9️⃣ استخدام Docker (اختياري)

### تشغيل مع Docker Compose

```bash
cd /home/ai/ai-agent

# تشغيل كل شيء
docker-compose up -d

# إيقاف
docker-compose down

# Logs
docker-compose logs -f
```

---

## 🔟 الخطوات التالية

بعد أن يعمل النظام:

1. **إنشاء Tenants جديدة** عبر `/crm/tenants`
2. **إضافة Users** عبر `/crm/tenants/{id}/users`
3. **إدارة Plans** عبر `/api/subscription/plans`
4. **إعداد Roles** عبر `/iam/roles`
5. **إعداد Permissions** عبر `/iam/permissions`
6. **اختبار Access Control** عبر `/iam/access-control`

---

## 📚 الوثائق

- [Architecture Documentation](./backend/CRM_AAA_ARCHITECTURE.md)
- [Quick Start Guide](./backend/CRM_AAA_QUICK_START.md)
- [Frontend Documentation](./frontend/CRM_IAM_FRONTEND.md)
- [API Documentation](http://localhost:8000/docs)

---

**آخر تحديث:** 2025-01-XX

