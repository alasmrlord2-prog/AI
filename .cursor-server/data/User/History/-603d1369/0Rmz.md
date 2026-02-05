# CRM + AAA Architecture Documentation

## نظرة عامة

هذا المستند يشرح البنية الكاملة لنظام CRM + AAA (Authentication, Authorization, Accounting) المدمج في SHIFTWAVE AI Platform.

---

## 🏗️ البنية المعمارية

### 1. الموديولات الأساسية

```
backend/app/
├── identity/          # IAM: Users, Tenants, Sessions, Departments, Projects
├── access/            # RBAC: Roles, Permissions, UserRoles
├── policy/            # Zanzibar-style Policy Engine (ABAC)
├── subscription/      # Plans, Subscriptions, Usage Counters, Quotas
├── audit/             # Audit Logs, Login Logs (Accounting)
├── crm/               # CRM Service (Facade layer)
└── core/
    └── aaa_middleware.py  # AAA Middleware (Authentication + Authorization + Accounting)
```

---

## 🔐 AAA (Authentication, Authorization, Accounting)

### Authentication (المصادقة)

**المسؤول:** `identity/` + `core/security.py`

**المكونات:**
- `User` model: حسابات المستخدمين
- `Session` model: جلسات الدخول
- `APIToken` model: API Tokens للوصول البرمجي
- JWT tokens
- MFA support (TOTP, Email, SMS)

**Endpoints:**
- `POST /api/identity/login` - تسجيل الدخول
- `GET /api/identity/sessions` - جلسات المستخدم
- `POST /api/identity/api-tokens` - إنشاء API Token
- `GET /api/identity/api-tokens` - قائمة API Tokens
- `DELETE /api/identity/api-tokens/{token_id}` - إلغاء Token

---

### Authorization (الصلاحيات)

**المسؤول:** `access/` + `policy/`

**المكونات:**

#### 1. RBAC (Role-Based Access Control)
- `Role` model: الأدوار (owner, admin, member, viewer)
- `Permission` model: الصلاحيات (resource + action)
- `UserRole` model: ربط المستخدمين بالأدوار
- `UserPermission` model: صلاحيات مباشرة للمستخدمين

#### 2. Policy Engine (Zanzibar-style)
- `RelationTuple` model: علاقات (user → relation → object)
- `PolicyRule` model: قواعد ABAC (Attribute-Based Access Control)

**Endpoints:**
- `GET /api/access/roles` - قائمة الأدوار
- `POST /api/access/roles` - إنشاء دور
- `GET /api/policy/relations` - قائمة العلاقات
- `POST /api/policy/relations` - إنشاء علاقة

---

### Accounting (المحاسبة)

**المسؤول:** `subscription/` + `audit/`

**المكونات:**

#### 1. Usage Tracking (Resource-based)
- `UsageCounter` model: تتبع الاستهلاك حسب نوع المورد
  - `resource_type`: "requests", "tokens", "storage_gb", "workflow_runs", "log_volume_gb", "agents"
  - `value`: القيمة الحالية
  - `period_start/period_end`: فترة الفوترة

#### 2. Usage Quotas
- `UsageQuota` model: حدود الاستهلاك لكل نوع مورد
  - `limit`: الحد الأقصى
  - `warning_threshold`: نسبة التحذير (مثلاً 80%)

#### 3. Audit Logs
- `AuditLog` model: سجل جميع العمليات
- `LoginLog` model: سجل محاولات الدخول

**Endpoints:**
- `GET /api/subscription/subscriptions/{id}/usage` - الاستهلاك الحالي
- `POST /api/subscription/subscriptions/{id}/usage/increment` - زيادة الاستهلاك
- `POST /api/subscription/subscriptions/{id}/usage/check` - التحقق من الحدود
- `GET /api/audit/logs` - سجل العمليات

---

## 🏢 CRM (Customer Relationship Management)

### المكونات

#### 1. Tenants (العملاء)
- `Tenant` model: يمثل عميل/شركة
- أنواع: company, individual, partner
- الحالات: active, suspended, trial, cancelled

#### 2. Departments (الأقسام)
- `Department` model: أقسام داخل Tenant
- دعم هيكل هرمي (parent_department_id)

#### 3. Projects (المشاريع)
- `Project` model: مشاريع داخل Tenant/Department

#### 4. Subscriptions (الاشتراكات)
- `Subscription` model: اشتراك Tenant في Plan
- `end_at`: تاريخ انتهاء الصلاحية
- `grace_end_at`: نهاية فترة السماح
- الحالات: active, expired, cancelled, trial, suspended

---

### CRM Service

**الملف:** `app/crm/service.py`

**الوظائف الرئيسية:**

1. `get_tenant_dashboard()` - لوحة تحكم شاملة للـ Tenant
2. `list_tenants()` - قائمة جميع Tenants
3. `get_tenant_users_detailed()` - قائمة المستخدمين مع Sessions و Devices
4. `get_tenant_departments()` - الأقسام
5. `get_tenant_projects()` - المشاريع
6. `get_tenant_usage_analytics()` - تحليلات الاستهلاك
7. `get_tenant_incidents()` - الحوادث
8. `get_tenant_audit_logs()` - سجل العمليات مع فلاتر
9. `get_tenant_summary_stats()` - إحصائيات ملخصة

---

### CRM API Endpoints

**الملف:** `app/api/crm_api.py`

#### Tenants
- `GET /api/crm/tenants` - قائمة Tenants
- `GET /api/crm/tenants/{id}/dashboard` - لوحة التحكم
- `GET /api/crm/tenants/{id}/summary` - إحصائيات ملخصة

#### Users
- `GET /api/crm/tenants/{id}/users` - قائمة المستخدمين مع تفاصيل

#### Departments & Projects
- `GET /api/crm/tenants/{id}/departments` - الأقسام
- `GET /api/crm/tenants/{id}/projects` - المشاريع

#### Usage & Analytics
- `GET /api/crm/tenants/{id}/usage?days=30` - تحليلات الاستهلاك

#### Incidents
- `GET /api/crm/tenants/{id}/incidents` - الحوادث

#### Audit Logs
- `GET /api/crm/tenants/{id}/audit-logs` - سجل العمليات مع فلاتر

---

## 🔄 AAA Middleware

**الملف:** `app/core/aaa_middleware.py`

### الوظائف

#### 1. Authentication
```python
await AAAMiddleware.authenticate_request(request)
```
- يتحقق من JWT token
- يجلب User و Tenant
- يرجع user context

#### 2. Authorization
```python
await AAAMiddleware.authorize_request(request, user_context, resource, action)
```
- يتحقق من الصلاحيات (RBAC + Policy)
- يرجع True/False

#### 3. Accounting
```python
await AAAMiddleware.account_request(request, user_context, action, resource_type)
```
- يسجل في Audit Logs
- يزيد Usage Counters
- يتحقق من الحدود

#### 4. Subscription Check
```python
await AAAMiddleware.check_subscription(request, user_context)
```
- يتحقق من حالة الاشتراك
- يتحقق من تاريخ الانتهاء
- يتحقق من Grace Period

#### 5. Usage Limit Check
```python
await AAAMiddleware.check_usage_limit(request, user_context, resource_type, amount)
```
- يتحقق من الحدود
- يرجع allowed/not allowed مع التفاصيل

---

## 🎯 Workflow Triggers

### الأحداث المدعومة

الـ AAA Middleware يدعم استدعاء Workflows عند الأحداث التالية:

1. **subscription.expired** - عند انتهاء الاشتراك
2. **user.added** - عند إضافة مستخدم
3. **user.disabled** - عند تعطيل مستخدم
4. **usage.limit_exceeded** - عند تجاوز الحدود

### الاستخدام

```python
# في Subscription Service
await AAAMiddleware.handle_subscription_expired(db, tenant_id)

# في Identity Service
await AAAMiddleware.handle_user_added(db, tenant_id, user_id)
await AAAMiddleware.handle_user_disabled(db, tenant_id, user_id)

# في Usage Check
await AAAMiddleware.handle_usage_limit_exceeded(
    db, tenant_id, resource_type, current_usage, limit
)
```

---

## 📊 Data Flow

### 1. User Login Flow

```
1. User → POST /api/identity/login
2. IdentityService.authenticate_user() → يتحقق من الباسورد
3. إنشاء JWT token
4. إنشاء Session
5. Return token + user + tenant
```

### 2. API Request Flow

```
1. Request → AAA Middleware
2. authenticate_request() → يتحقق من Token
3. check_subscription() → يتحقق من الاشتراك
4. authorize_request() → يتحقق من الصلاحيات
5. check_usage_limit() → يتحقق من الحدود
6. account_request() → يسجل + يزيد الاستهلاك
7. Process request
8. Return response
```

### 3. Subscription Expiry Flow

```
1. check_subscription() → يكتشف انتهاء الاشتراك
2. handle_subscription_expired() → يستدعي Workflow
3. Workflow → يرسل إشعار / يعلق الحساب / إلخ
```

---

## 🔑 Resource Types (Usage Counters)

النظام يدعم تتبع الاستهلاك حسب نوع المورد:

- `requests` - عدد الطلبات
- `tokens` - AI tokens المستهلكة
- `storage_gb` - التخزين بالـ GB
- `workflow_runs` - عدد تنفيذات Workflows
- `log_volume_gb` - حجم الـ Logs بالـ GB
- `agents` - عدد الـ Agents النشطة

---

## 📝 Best Practices

### 1. استخدام AAA Middleware

```python
from app.core.aaa_middleware import get_current_user_context, require_active_subscription

@router.get("/protected")
async def protected_endpoint(
    request: Request,
    user_context: Dict = Depends(get_current_user_context),
    subscription: Dict = Depends(require_active_subscription)
):
    # User is authenticated and has active subscription
    pass
```

### 2. تتبع الاستهلاك

```python
from app.core.aaa_middleware import AAAMiddleware

# في endpoint
usage_check = await AAAMiddleware.check_usage_limit(
    request, user_context, "requests", 1
)
if not usage_check["allowed"]:
    raise HTTPException(402, "Usage limit exceeded")

# بعد نجاح العملية
await AAAMiddleware.account_request(
    request, user_context, "api_call", "requests"
)
```

### 3. Workflow Triggers

```python
# عند إضافة مستخدم
await AAAMiddleware.handle_user_added(db, tenant_id, user_id)

# عند انتهاء الاشتراك
await AAAMiddleware.handle_subscription_expired(db, tenant_id)
```

---

## 🚀 التوسعات المستقبلية

1. **Billing Integration** - ربط مع أنظمة الدفع
2. **Invoice Generation** - إنشاء فواتير تلقائية
3. **Multi-currency** - دعم عملات متعددة
4. **Usage Forecasting** - توقع الاستهلاك
5. **Auto-scaling** - زيادة/تقليل الخطة تلقائياً
6. **Advanced Analytics** - تحليلات متقدمة

---

## 📚 المراجع

- [Identity API](./app/api/identity_api.py)
- [CRM API](./app/api/crm_api.py)
- [Subscription API](./app/api/subscription_api.py)
- [AAA Middleware](./app/core/aaa_middleware.py)
- [CRM Service](./app/crm/service.py)

---

**آخر تحديث:** 2025-01-XX
**الإصدار:** 1.0.0

