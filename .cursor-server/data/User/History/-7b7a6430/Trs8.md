# CRM + AAA Quick Start Guide

## 🚀 البدء السريع

### 1. إنشاء Tenant جديد

```bash
POST /api/identity/tenants
{
  "name": "شركة ABC",
  "type": "company",
  "contact_email": "contact@abc.com",
  "contact_phone": "+1234567890"
}
```

### 2. إنشاء Plan

```bash
POST /api/subscription/plans
{
  "name": "Pro",
  "description": "Professional Plan",
  "price_monthly": 99.99,
  "max_users": 10,
  "max_requests": 10000,
  "max_tokens": 1000000,
  "features_json": {
    "ai_debugger": true,
    "cicd": true,
    "security": true
  }
}
```

### 3. إنشاء Subscription

```bash
POST /api/subscription/subscriptions
{
  "tenant_id": "uuid-here",
  "plan_id": "uuid-here",
  "start_at": "2025-01-01T00:00:00Z",
  "end_at": "2025-12-31T23:59:59Z",
  "grace_end_at": "2026-01-15T23:59:59Z",
  "renewal_type": "manual"
}
```

### 4. إنشاء User

```bash
POST /api/identity/users
{
  "email": "user@abc.com",
  "password": "secure_password",
  "full_name": "John Doe",
  "tenant_id": "uuid-here"
}
```

### 5. تسجيل الدخول

```bash
POST /api/identity/login
{
  "email": "user@abc.com",
  "password": "secure_password"
}

# Response:
{
  "access_token": "jwt-token-here",
  "token_type": "bearer",
  "user": {...},
  "tenant": {...}
}
```

### 6. استخدام API مع Authentication

```bash
GET /api/crm/tenants/{tenant_id}/dashboard
Headers:
  Authorization: Bearer jwt-token-here
```

---

## 📊 CRM Dashboard

### الحصول على لوحة التحكم الكاملة

```bash
GET /api/crm/tenants/{tenant_id}/dashboard
```

**Response يتضمن:**
- معلومات Tenant
- حالة الاشتراك
- قائمة المستخدمين
- الاستهلاك الحالي
- الحدود
- آخر النشاطات

### قائمة Tenants

```bash
GET /api/crm/tenants?limit=100&offset=0
```

### إحصائيات Tenant

```bash
GET /api/crm/tenants/{tenant_id}/summary
```

---

## 👥 إدارة المستخدمين

### قائمة المستخدمين مع التفاصيل

```bash
GET /api/crm/tenants/{tenant_id}/users
```

**Response يتضمن:**
- معلومات المستخدم
- الدور
- الجلسات النشطة
- API Tokens
- آخر دخول + IP + Location

### إضافة مستخدم لـ Tenant

```bash
POST /api/identity/tenants/{tenant_id}/users?user_id={user_id}&role=admin
```

---

## 📈 Usage & Analytics

### الاستهلاك الحالي

```bash
GET /api/subscription/subscriptions/{subscription_id}/usage
```

### تحليلات الاستهلاك (آخر 30 يوم)

```bash
GET /api/crm/tenants/{tenant_id}/usage?days=30
```

### التحقق من الحدود

```bash
POST /api/subscription/subscriptions/{subscription_id}/usage/check
{
  "resource_type": "requests",
  "requested_amount": 1
}
```

### زيادة الاستهلاك

```bash
POST /api/subscription/subscriptions/{subscription_id}/usage/increment
{
  "resource_type": "requests",
  "amount": 1
}
```

---

## 🔑 API Tokens Management

### إنشاء API Token

```bash
POST /api/identity/api-tokens
{
  "name": "Production API Key",
  "tenant_id": "uuid-here",
  "scopes": ["read", "write"],
  "expires_at": "2025-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "token": {...},
  "plain_token": "token-shown-once-only",
  "message": "Store the plain_token securely - it won't be shown again."
}
```

### قائمة API Tokens

```bash
GET /api/identity/api-tokens?user_id={user_id}&tenant_id={tenant_id}
```

### إلغاء API Token

```bash
DELETE /api/identity/api-tokens/{token_id}
```

---

## 📋 Audit Logs

### سجل العمليات

```bash
GET /api/crm/tenants/{tenant_id}/audit-logs?limit=100&offset=0
```

### مع فلاتر

```bash
GET /api/crm/tenants/{tenant_id}/audit-logs?
  action=login&
  user_id={user_id}&
  start_date=2025-01-01T00:00:00Z&
  end_date=2025-01-31T23:59:59Z
```

---

## 🏢 Departments & Projects

### إنشاء Department

```bash
POST /api/identity/tenants/{tenant_id}/departments
{
  "name": "Engineering",
  "description": "Engineering Department",
  "parent_department_id": null
}
```

### قائمة Departments

```bash
GET /api/crm/tenants/{tenant_id}/departments
```

### إنشاء Project

```bash
POST /api/identity/tenants/{tenant_id}/projects
{
  "name": "Project Alpha",
  "description": "Main project",
  "department_id": "uuid-here"
}
```

### قائمة Projects

```bash
GET /api/crm/tenants/{tenant_id}/projects?department_id={dept_id}
```

---

## ⚠️ Incidents

### قائمة الحوادث

```bash
GET /api/crm/tenants/{tenant_id}/incidents?limit=50&offset=0
```

---

## 🔐 استخدام AAA Middleware في Endpoints

### مثال: Protected Endpoint

```python
from fastapi import APIRouter, Depends, Request
from app.core.aaa_middleware import get_current_user_context, require_active_subscription

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(
    request: Request,
    user_context: Dict = Depends(get_current_user_context),
    subscription: Dict = Depends(require_active_subscription)
):
    # User is authenticated and has active subscription
    return {
        "user_id": user_context["user_id"],
        "tenant_id": user_context["tenant_id"],
        "message": "Access granted"
    }
```

### مثال: تتبع الاستهلاك

```python
from app.core.aaa_middleware import AAAMiddleware

@router.post("/api-call")
async def api_call(
    request: Request,
    user_context: Dict = Depends(get_current_user_context)
):
    # Check usage limit
    usage_check = await AAAMiddleware.check_usage_limit(
        request, user_context, "requests", 1
    )
    
    if not usage_check["allowed"]:
        raise HTTPException(402, "Usage limit exceeded")
    
    # Process request
    result = do_something()
    
    # Account for usage
    await AAAMiddleware.account_request(
        request, user_context, "api_call", "requests"
    )
    
    return result
```

---

## 🎯 Workflow Triggers

### استدعاء Workflow عند الأحداث

```python
from app.core.aaa_middleware import AAAMiddleware

# عند انتهاء الاشتراك
await AAAMiddleware.handle_subscription_expired(db, tenant_id)

# عند إضافة مستخدم
await AAAMiddleware.handle_user_added(db, tenant_id, user_id)

# عند تعطيل مستخدم
await AAAMiddleware.handle_user_disabled(db, tenant_id, user_id)

# عند تجاوز الحدود
await AAAMiddleware.handle_usage_limit_exceeded(
    db, tenant_id, "requests", current_usage, limit
)
```

---

## 📝 ملاحظات مهمة

1. **JWT Tokens**: صلاحية افتراضية 24 ساعة
2. **Grace Period**: فترة سماح بعد انتهاء الاشتراك (افتراضي 15 يوم)
3. **Usage Counters**: يتم إعادة تعيينها شهرياً
4. **API Tokens**: يتم عرض `plain_token` مرة واحدة فقط - احفظه بأمان
5. **Audit Logs**: يتم الاحتفاظ بها لمدة غير محدودة (يمكن إضافة retention policy)

---

## 🔗 روابط مفيدة

- [Architecture Documentation](./CRM_AAA_ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Identity API](./app/api/identity_api.py)
- [CRM API](./app/api/crm_api.py)
- [Subscription API](./app/api/subscription_api.py)

---

**آخر تحديث:** 2025-01-XX

