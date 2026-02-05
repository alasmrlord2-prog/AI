# 🏗️ البنية الكاملة للمشروع - Complete Project Structure

## 📁 البنية العامة

```
ai-agent/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── core/               # Core functionality
│   │   ├── identity/           # IAM: Users, Tenants, Sessions
│   │   ├── access/             # RBAC: Roles, Permissions
│   │   ├── policy/             # Zanzibar Policy Engine
│   │   ├── subscription/       # Plans, Subscriptions, Usage
│   │   ├── audit/              # Audit Logs, Login Logs
│   │   ├── crm/                # CRM Service (Facade)
│   │   ├── api/                # API Routes
│   │   └── ... (AI Platform modules)
│   └── scripts/
│       └── setup_initial_data.py
│
└── frontend/                   # Next.js Frontend
    ├── app/
    │   ├── crm/                # CRM UI
    │   ├── iam/                # IAM UI
    │   └── ... (AI Platform UI)
    └── lib/
        └── api.ts              # API Wrappers
```

---

## 🔵 BACKEND - البنية الكاملة

### 📂 Core Modules

```
backend/app/core/
├── config.py                   # Configuration
├── settings.py                 # Settings management
├── database.py                 # SQLAlchemy setup
├── security.py                 # JWT, password hashing
├── exceptions.py               # Exception handlers
├── utils.py                    # Utilities
└── aaa_middleware.py          # ✅ AAA Middleware (Authentication, Authorization, Accounting)
```

**الوظيفة:**
- `aaa_middleware.py`: Middleware مركزي للـ AAA
  - Authentication: التحقق من JWT tokens
  - Authorization: التحقق من الصلاحيات
  - Accounting: تتبع الاستهلاك + Audit logs
  - Workflow Triggers: استدعاء Workflows عند الأحداث

---

### 📂 Identity Module (IAM)

```
backend/app/identity/
├── models.py                   # User, Tenant, TenantUser, Session, APIToken, Department, Project
├── schemas.py                  # Pydantic schemas
└── service.py                  # Business logic
```

**الوظيفة:**
- إدارة المستخدمين (Users)
- إدارة العملاء (Tenants)
- إدارة الجلسات (Sessions)
- إدارة API Tokens
- إدارة Departments و Projects

**API Routes:** `/api/identity/*`
- `POST /api/identity/login` - تسجيل الدخول
- `POST /api/identity/users` - إنشاء مستخدم
- `GET /api/identity/users/{id}` - جلب مستخدم
- `POST /api/identity/tenants` - إنشاء tenant
- `GET /api/identity/sessions` - جلب الجلسات
- `POST /api/identity/api-tokens` - إنشاء API token
- `GET /api/identity/api-tokens` - قائمة API tokens

---

### 📂 Access Module (RBAC)

```
backend/app/access/
├── models.py                   # Role, Permission, UserRole, UserPermission
├── schemas.py                  # Pydantic schemas
└── service.py                  # Business logic
```

**الوظيفة:**
- إدارة الأدوار (Roles)
- إدارة الصلاحيات (Permissions)
- ربط المستخدمين بالأدوار
- التحقق من الصلاحيات

**API Routes:** `/api/access/*`
- `GET /api/access/roles` - قائمة الأدوار
- `POST /api/access/roles` - إنشاء دور
- `GET /api/access/permissions` - قائمة الصلاحيات
- `POST /api/access/user-roles` - تعيين دور لمستخدم

---

### 📂 Policy Module (Zanzibar)

```
backend/app/policy/
├── models.py                   # RelationTuple, PolicyRule
├── schemas.py                  # Pydantic schemas
├── service.py                  # Business logic
└── engine.py                  # ✅ Graph-based evaluation engine
```

**الوظيفة:**
- Zanzibar-style Relation Tuples
- Policy Rules (ABAC)
- Graph-based access evaluation
- Path finding للعلاقات غير المباشرة

**API Routes:** `/api/policy/*`
- `POST /api/policy/relations` - إنشاء relation tuple
- `GET /api/policy/relations` - قائمة relations
- `POST /api/policy/check` - التحقق من relation
- `POST /api/policy/rules` - إنشاء policy rule
- `GET /api/policy/rules` - قائمة policy rules

---

### 📂 Subscription Module

```
backend/app/subscription/
├── models.py                   # Plan, Subscription, UsageCounter, UsageQuota
├── schemas.py                  # Pydantic schemas
└── service.py                  # Business logic
```

**الوظيفة:**
- إدارة الخطط (Plans)
- إدارة الاشتراكات (Subscriptions)
- تتبع الاستهلاك (Usage Counters) - Resource-based
- التحقق من الحدود (Usage Quotas)

**API Routes:** `/api/subscription/*`
- `GET /api/subscription/plans` - قائمة الخطط
- `POST /api/subscription/plans` - إنشاء خطة
- `GET /api/subscription/tenants/{id}/subscription` - حالة الاشتراك
- `GET /api/subscription/subscriptions/{id}/usage` - الاستهلاك
- `POST /api/subscription/subscriptions/{id}/usage/increment` - زيادة الاستهلاك
- `POST /api/subscription/subscriptions/{id}/usage/check` - التحقق من الحدود

---

### 📂 Audit Module

```
backend/app/audit/
├── models.py                   # AuditLog, LoginLog
├── schemas.py                  # Pydantic schemas
└── service.py                  # Business logic
```

**الوظيفة:**
- تسجيل جميع العمليات (Audit Logs)
- تسجيل محاولات الدخول (Login Logs)
- Accounting للعمليات

**API Routes:** `/api/audit/*`
- `GET /api/audit/logs` - قائمة audit logs
- `POST /api/audit/logs` - إنشاء audit log
- `GET /api/audit/login-logs` - قائمة login logs

---

### 📂 CRM Module (Facade)

```
backend/app/crm/
├── schemas.py                  # ✅ CRM Response schemas
└── service.py                  # ✅ CRM Service (Facade layer)
```

**الوظيفة:**
- واجهة موحدة لـ CRM
- تجميع بيانات من identity + subscription + audit
- Dashboard data للـ Tenants

**API Routes:** `/api/crm/*`
- `GET /api/crm/tenants` - قائمة tenants
- `GET /api/crm/tenants/{id}/dashboard` - Dashboard شامل
- `GET /api/crm/tenants/{id}/summary` - إحصائيات ملخصة
- `GET /api/crm/tenants/{id}/users` - قائمة المستخدمين
- `GET /api/crm/tenants/{id}/departments` - الأقسام
- `GET /api/crm/tenants/{id}/projects` - المشاريع
- `GET /api/crm/tenants/{id}/usage` - تحليلات الاستهلاك
- `GET /api/crm/tenants/{id}/incidents` - الحوادث
- `GET /api/crm/tenants/{id}/audit-logs` - سجل العمليات

---

### 📂 API Routes

```
backend/app/api/
├── identity_api.py             # ✅ Identity API routes
├── access_api.py               # ✅ Access API routes
├── policy_api.py               # ✅ Policy API routes
├── subscription_api.py         # ✅ Subscription API routes
├── audit_api.py                # ✅ Audit API routes
└── crm_api.py                  # ✅ CRM API routes
```

**جميع الـ Routes مسجلة في:** `app/main.py`

---

## 🟢 FRONTEND - البنية الكاملة

### 📂 CRM Pages

```
frontend/app/crm/
└── tenants/
    ├── page.tsx                # ✅ قائمة Tenants
    └── [tenantId]/
        ├── page.tsx            # ✅ Dashboard مع Tabs
        ├── users/
        │   └── page.tsx        # ✅ إدارة المستخدمين
        └── subscription/
            └── page.tsx         # ✅ إدارة الاشتراكات
```

**الصفحات:**

1. **`/crm/tenants`** - قائمة Tenants
   - عرض جميع Tenants
   - Search و Filter
   - Pagination
   - Navigation إلى Dashboard

2. **`/crm/tenants/[tenantId]`** - Tenant Dashboard
   - **Overview Tab**: نظرة عامة + Subscription Status + Users Summary + Recent Activity
   - **Users Tab**: رابط إلى صفحة Users
   - **Subscription Tab**: رابط إلى صفحة Subscription
   - **Usage Analytics Tab**: رسوم بيانية للاستهلاك
   - **Audit Logs Tab**: سجل العمليات
   - **Incidents Tab**: الحوادث

3. **`/crm/tenants/[tenantId]/users`** - إدارة المستخدمين
   - قائمة المستخدمين مع تفاصيل
   - عرض Sessions النشطة
   - عرض API Tokens
   - Last Login Info (IP + Location)
   - Revoke Sessions

4. **`/crm/tenants/[tenantId]/subscription`** - إدارة الاشتراكات
   - Current Subscription Details
   - Usage & Limits (مع Progress Bars)
   - Available Plans
   - Upgrade/Downgrade

---

### 📂 IAM Pages

```
frontend/app/iam/
├── roles/
│   └── page.tsx                # ✅ إدارة الأدوار
├── permissions/
│   └── page.tsx                # ✅ Permission Matrix
├── policies/
│   └── page.tsx                # ✅ Zanzibar Policies
└── access-control/
    └── page.tsx                # ✅ Access Testing Tool
```

**الصفحات:**

1. **`/iam/roles`** - إدارة الأدوار
   - قائمة الأدوار
   - Search
   - Create Role Modal
   - عرض Permissions لكل Role

2. **`/iam/permissions`** - Permission Matrix
   - جدول الصلاحيات
   - Filter by Resource
   - Filter by Action
   - Search

3. **`/iam/policies`** - Zanzibar Policies
   - **Relation Tuples Tab**: عرض جميع العلاقات
   - **Policy Rules Tab**: عرض القواعد
   - Create Relation Tuple
   - Create Policy Rule

4. **`/iam/access-control`** - Access Testing Tool
   - Relation Check: اختبار العلاقات
   - Permission Check: اختبار الصلاحيات
   - عرض النتائج مع التفاصيل
   - عرض Matched Tuples و Paths

---

### 📂 API Wrappers

```
frontend/lib/api.ts
```

**الوظيفة:**
- API wrappers لجميع الـ endpoints
- Authentication headers
- Error handling
- Timeout handling

**المتوفرة:**
- `crmApi` - جميع وظائف CRM
- `identityApi` - إدارة المستخدمين والـ Tenants
- `subscriptionApi` - إدارة الاشتراكات
- `accessApi` - إدارة الأدوار والصلاحيات
- `policyApi` - Zanzibar Policy Engine

---

## 🔄 Flow العمل

### 1. User Login Flow

```
User → POST /api/identity/login
  ↓
IdentityService.authenticate_user()
  ↓
Create JWT Token
  ↓
Create Session
  ↓
Return Token + User + Tenant
```

---

### 2. API Request Flow (مع AAA Middleware)

```
Request → AAA Middleware
  ↓
1. authenticate_request() → Verify JWT Token
  ↓
2. check_subscription() → Check Subscription Status
  ↓
3. authorize_request() → Check Permissions (RBAC + Policy)
  ↓
4. check_usage_limit() → Check Usage Limits
  ↓
5. account_request() → Log Audit + Increment Usage
  ↓
Process Request
  ↓
Return Response
```

---

### 3. CRM Dashboard Flow

```
Frontend → GET /api/crm/tenants/{id}/dashboard
  ↓
CRMService.get_tenant_dashboard()
  ↓
Aggregate Data:
  - IdentityService.get_tenant_by_id()
  - SubscriptionService.check_subscription_status()
  - IdentityService.get_tenant_users()
  - SubscriptionService.get_usage()
  - AuditService.query_audit_logs()
  ↓
Return Complete Dashboard Data
```

---

## 🌐 URLs و Endpoints

### Backend API

**Base URL:** `http://localhost:8000`

#### Identity API
- `POST /api/identity/login`
- `GET /api/identity/users`
- `POST /api/identity/users`
- `GET /api/identity/tenants`
- `POST /api/identity/tenants`
- `GET /api/identity/sessions`
- `POST /api/identity/api-tokens`
- `GET /api/identity/api-tokens`

#### Access API
- `GET /api/access/roles`
- `POST /api/access/roles`
- `GET /api/access/permissions`
- `POST /api/access/user-roles`

#### Policy API
- `GET /api/policy/relations`
- `POST /api/policy/relations`
- `POST /api/policy/check`
- `GET /api/policy/rules`
- `POST /api/policy/rules`

#### Subscription API
- `GET /api/subscription/plans`
- `POST /api/subscription/plans`
- `GET /api/subscription/tenants/{id}/subscription`
- `GET /api/subscription/subscriptions/{id}/usage`
- `POST /api/subscription/subscriptions/{id}/usage/increment`

#### Audit API
- `GET /api/audit/logs`
- `GET /api/audit/login-logs`

#### CRM API
- `GET /api/crm/tenants`
- `GET /api/crm/tenants/{id}/dashboard`
- `GET /api/crm/tenants/{id}/summary`
- `GET /api/crm/tenants/{id}/users`
- `GET /api/crm/tenants/{id}/departments`
- `GET /api/crm/tenants/{id}/projects`
- `GET /api/crm/tenants/{id}/usage`
- `GET /api/crm/tenants/{id}/incidents`
- `GET /api/crm/tenants/{id}/audit-logs`

---

### Frontend Pages

**Base URL:** `http://localhost:3000`

#### CRM Pages
- `http://localhost:3000/crm/tenants` - قائمة Tenants
- `http://localhost:3000/crm/tenants/{tenantId}` - Dashboard
- `http://localhost:3000/crm/tenants/{tenantId}/users` - Users
- `http://localhost:3000/crm/tenants/{tenantId}/subscription` - Subscription

#### IAM Pages
- `http://localhost:3000/iam/roles` - Roles
- `http://localhost:3000/iam/permissions` - Permissions
- `http://localhost:3000/iam/policies` - Policies
- `http://localhost:3000/iam/access-control` - Access Control

---

## 📊 Database Schema

### الجداول الرئيسية

#### Identity Tables
- `users` - المستخدمين
- `tenants` - العملاء
- `tenant_users` - ربط المستخدمين بالعملاء
- `sessions` - الجلسات
- `api_tokens` - API Tokens
- `departments` - الأقسام
- `projects` - المشاريع

#### Access Tables
- `roles` - الأدوار
- `permissions` - الصلاحيات
- `role_permissions` - ربط الصلاحيات بالأدوار
- `user_roles` - ربط المستخدمين بالأدوار
- `user_permissions` - صلاحيات مباشرة للمستخدمين

#### Policy Tables
- `relation_tuples` - Relation Tuples (Zanzibar)
- `policy_rules` - Policy Rules (ABAC)

#### Subscription Tables
- `plans` - الخطط
- `subscriptions` - الاشتراكات
- `usage_counters` - تتبع الاستهلاك (Resource-based)
- `usage_quotas` - حدود الاستهلاك

#### Audit Tables
- `audit_logs` - سجل العمليات
- `login_logs` - سجل محاولات الدخول

---

## 🔐 AAA Middleware

**الملف:** `backend/app/core/aaa_middleware.py`

### الوظائف الرئيسية:

1. **`authenticate_request()`** - التحقق من JWT Token
2. **`authorize_request()`** - التحقق من الصلاحيات
3. **`account_request()`** - تسجيل Audit + زيادة الاستهلاك
4. **`check_subscription()`** - التحقق من حالة الاشتراك
5. **`check_usage_limit()`** - التحقق من الحدود
6. **`trigger_workflow_event()`** - استدعاء Workflows
7. **`handle_subscription_expired()`** - معالجة انتهاء الاشتراك
8. **`handle_user_added()`** - معالجة إضافة مستخدم
9. **`handle_user_disabled()`** - معالجة تعطيل مستخدم
10. **`handle_usage_limit_exceeded()`** - معالجة تجاوز الحدود

---

## 🎯 Resource Types (Usage Counters)

النظام يدعم تتبع الاستهلاك حسب نوع المورد:

- `requests` - عدد الطلبات
- `tokens` - AI tokens المستهلكة
- `storage_gb` - التخزين بالـ GB
- `workflow_runs` - عدد تنفيذات Workflows
- `log_volume_gb` - حجم الـ Logs بالـ GB
- `agents` - عدد الـ Agents النشطة

---

## 📝 ملخص

### Backend:
- ✅ **6 Modules رئيسية**: identity, access, policy, subscription, audit, crm
- ✅ **6 API Routers**: identity_api, access_api, policy_api, subscription_api, audit_api, crm_api
- ✅ **AAA Middleware**: Authentication + Authorization + Accounting
- ✅ **Resource-based Usage Tracking**

### Frontend:
- ✅ **4 CRM Pages**: Tenants List, Dashboard, Users, Subscription
- ✅ **4 IAM Pages**: Roles, Permissions, Policies, Access Control
- ✅ **API Wrappers**: crmApi, identityApi, subscriptionApi, accessApi, policyApi

---

**آخر تحديث:** 2025-01-XX

