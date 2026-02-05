# 🗺️ خريطة الواجهات - Interfaces Map

## 📍 أين كل واجهة تعمل؟

---

## 🔵 BACKEND APIs

### 🔐 Identity API (`/api/identity/*`)

**الملف:** `backend/app/api/identity_api.py`

| Endpoint | Method | الوظيفة | أين يستخدم |
|----------|--------|---------|------------|
| `/api/identity/login` | POST | تسجيل الدخول | Frontend Login Page |
| `/api/identity/users` | GET | قائمة المستخدمين | - |
| `/api/identity/users` | POST | إنشاء مستخدم | CRM Users Page |
| `/api/identity/users/{id}` | GET | جلب مستخدم | - |
| `/api/identity/users/{id}` | PUT | تحديث مستخدم | - |
| `/api/identity/tenants` | GET | قائمة Tenants | - |
| `/api/identity/tenants` | POST | إنشاء Tenant | CRM Tenants Page |
| `/api/identity/tenants/{id}` | GET | جلب Tenant | CRM Dashboard |
| `/api/identity/tenants/{id}/users` | GET | مستخدمي Tenant | CRM Users Page |
| `/api/identity/tenants/{id}/users` | POST | إضافة مستخدم | CRM Users Page |
| `/api/identity/sessions` | GET | جلب الجلسات | CRM Users Page |
| `/api/identity/sessions/{id}` | DELETE | إلغاء جلسة | CRM Users Page |
| `/api/identity/api-tokens` | POST | إنشاء API Token | IAM API Tokens |
| `/api/identity/api-tokens` | GET | قائمة API Tokens | IAM API Tokens |
| `/api/identity/api-tokens/{id}` | DELETE | إلغاء Token | IAM API Tokens |

---

### 🔑 Access API (`/api/access/*`)

**الملف:** `backend/app/api/access_api.py`

| Endpoint | Method | الوظيفة | أين يستخدم |
|----------|--------|---------|------------|
| `/api/access/roles` | GET | قائمة الأدوار | IAM Roles Page |
| `/api/access/roles` | POST | إنشاء دور | IAM Roles Page |
| `/api/access/roles/{id}` | GET | جلب دور | - |
| `/api/access/permissions` | GET | قائمة الصلاحيات | IAM Permissions Page |
| `/api/access/user-roles` | GET | أدوار المستخدم | - |
| `/api/access/user-roles` | POST | تعيين دور | - |

---

### 🎯 Policy API (`/api/policy/*`)

**الملف:** `backend/app/api/policy_api.py`

| Endpoint | Method | الوظيفة | أين يستخدم |
|----------|--------|---------|------------|
| `/api/policy/relations` | GET | قائمة Relations | IAM Policies Page |
| `/api/policy/relations` | POST | إنشاء Relation | IAM Policies Page |
| `/api/policy/check` | POST | التحقق من Relation | IAM Access Control Page |
| `/api/policy/rules` | GET | قائمة Rules | IAM Policies Page |
| `/api/policy/rules` | POST | إنشاء Rule | IAM Policies Page |

---

### 💳 Subscription API (`/api/subscription/*`)

**الملف:** `backend/app/api/subscription_api.py`

| Endpoint | Method | الوظيفة | أين يستخدم |
|----------|--------|---------|------------|
| `/api/subscription/plans` | GET | قائمة الخطط | CRM Subscription Page |
| `/api/subscription/plans` | POST | إنشاء خطة | - |
| `/api/subscription/plans/{id}` | GET | جلب خطة | - |
| `/api/subscription/subscriptions` | POST | إنشاء اشتراك | - |
| `/api/subscription/tenants/{id}/subscription` | GET | حالة الاشتراك | CRM Dashboard, Subscription Page |
| `/api/subscription/subscriptions/{id}/usage` | GET | الاستهلاك | CRM Dashboard, Usage Tab |
| `/api/subscription/subscriptions/{id}/usage/increment` | POST | زيادة الاستهلاك | AAA Middleware |
| `/api/subscription/subscriptions/{id}/usage/check` | POST | التحقق من الحدود | AAA Middleware |

---

### 📋 Audit API (`/api/audit/*`)

**الملف:** `backend/app/api/audit_api.py`

| Endpoint | Method | الوظيفة | أين يستخدم |
|----------|--------|---------|------------|
| `/api/audit/logs` | GET | قائمة Audit Logs | CRM Audit Logs Tab |
| `/api/audit/logs` | POST | إنشاء Audit Log | AAA Middleware |
| `/api/audit/login-logs` | GET | قائمة Login Logs | - |

---

### 🏢 CRM API (`/api/crm/*`)

**الملف:** `backend/app/api/crm_api.py`

| Endpoint | Method | الوظيفة | أين يستخدم |
|----------|--------|---------|------------|
| `/api/crm/tenants` | GET | قائمة Tenants | CRM Tenants List Page |
| `/api/crm/tenants/{id}/dashboard` | GET | Dashboard شامل | CRM Dashboard Page |
| `/api/crm/tenants/{id}/summary` | GET | إحصائيات ملخصة | CRM Dashboard |
| `/api/crm/tenants/{id}/users` | GET | مستخدمي Tenant | CRM Users Page |
| `/api/crm/tenants/{id}/departments` | GET | أقسام Tenant | - |
| `/api/crm/tenants/{id}/projects` | GET | مشاريع Tenant | - |
| `/api/crm/tenants/{id}/usage` | GET | تحليلات الاستهلاك | CRM Usage Tab |
| `/api/crm/tenants/{id}/incidents` | GET | حوادث Tenant | CRM Incidents Tab |
| `/api/crm/tenants/{id}/audit-logs` | GET | سجل العمليات | CRM Audit Logs Tab |

---

## 🟢 FRONTEND Pages

### 🏢 CRM Pages

#### 1. `/crm/tenants` - قائمة Tenants
**الملف:** `frontend/app/crm/tenants/page.tsx`

**الوظيفة:**
- عرض قائمة جميع Tenants
- Search و Filter
- Pagination
- Navigation إلى Dashboard

**API Calls:**
- `crmApi.listTenants()`

---

#### 2. `/crm/tenants/[tenantId]` - Tenant Dashboard
**الملف:** `frontend/app/crm/tenants/[tenantId]/page.tsx`

**الوظيفة:**
- Dashboard شامل مع Tabs:
  - **Overview**: Subscription Status + Users Summary + Recent Activity
  - **Users**: رابط إلى Users Page
  - **Subscription**: رابط إلى Subscription Page
  - **Usage Analytics**: رسوم بيانية
  - **Audit Logs**: سجل العمليات
  - **Incidents**: الحوادث

**API Calls:**
- `crmApi.getTenantDashboard()`

---

#### 3. `/crm/tenants/[tenantId]/users` - إدارة المستخدمين
**الملف:** `frontend/app/crm/tenants/[tenantId]/users/page.tsx`

**الوظيفة:**
- قائمة المستخدمين مع تفاصيل
- عرض Sessions النشطة
- عرض API Tokens
- Last Login Info
- Revoke Sessions

**API Calls:**
- `crmApi.getTenantUsers()`
- `identityApi.revokeSession()`

---

#### 4. `/crm/tenants/[tenantId]/subscription` - إدارة الاشتراكات
**الملف:** `frontend/app/crm/tenants/[tenantId]/subscription/page.tsx`

**الوظيفة:**
- Current Subscription Details
- Usage & Limits (Progress Bars)
- Available Plans
- Upgrade/Downgrade

**API Calls:**
- `subscriptionApi.getSubscriptionStatus()`
- `subscriptionApi.getPlans()`

---

### 🔐 IAM Pages

#### 1. `/iam/roles` - إدارة الأدوار
**الملف:** `frontend/app/iam/roles/page.tsx`

**الوظيفة:**
- قائمة الأدوار
- Search
- Create Role Modal
- عرض Permissions

**API Calls:**
- `accessApi.getRoles()`
- `accessApi.createRole()`

---

#### 2. `/iam/permissions` - Permission Matrix
**الملف:** `frontend/app/iam/permissions/page.tsx`

**الوظيفة:**
- جدول الصلاحيات
- Filter by Resource
- Filter by Action
- Search

**API Calls:**
- `accessApi.getPermissions()`

---

#### 3. `/iam/policies` - Zanzibar Policies
**الملف:** `frontend/app/iam/policies/page.tsx`

**الوظيفة:**
- **Relation Tuples Tab**: عرض Relations
- **Policy Rules Tab**: عرض Rules
- Create Relation Tuple
- Create Policy Rule

**API Calls:**
- `policyApi.getRelations()`
- `policyApi.createRelationTuple()`
- `policyApi.getPolicyRules()`
- `policyApi.createPolicyRule()`

---

#### 4. `/iam/access-control` - Access Testing Tool
**الملف:** `frontend/app/iam/access-control/page.tsx`

**الوظيفة:**
- Relation Check: اختبار العلاقات
- Permission Check: اختبار الصلاحيات
- عرض النتائج مع التفاصيل

**API Calls:**
- `policyApi.checkRelation()`
- `accessApi.getUserRoles()` (للمستقبل)

---

## 🔄 Flow العمل

### Login Flow
```
Frontend: /login
  ↓
POST /api/identity/login
  ↓
Backend: IdentityService.authenticate_user()
  ↓
Return JWT Token
  ↓
Frontend: Save Token → Redirect to Dashboard
```

---

### CRM Dashboard Flow
```
Frontend: /crm/tenants/{id}
  ↓
GET /api/crm/tenants/{id}/dashboard
  ↓
Backend: CRMService.get_tenant_dashboard()
  ↓
Aggregate Data:
  - IdentityService.get_tenant_by_id()
  - SubscriptionService.check_subscription_status()
  - IdentityService.get_tenant_users()
  - SubscriptionService.get_usage()
  - AuditService.query_audit_logs()
  ↓
Return Complete Dashboard
  ↓
Frontend: Display Dashboard with Tabs
```

---

### API Request Flow (مع AAA)
```
Frontend: API Request
  ↓
AAA Middleware:
  1. authenticate_request() → Verify JWT
  2. check_subscription() → Check Subscription
  3. authorize_request() → Check Permissions
  4. check_usage_limit() → Check Limits
  5. account_request() → Log + Increment Usage
  ↓
Process Request
  ↓
Return Response
```

---

## 📊 Database Tables

### Identity
- `users` → IdentityService
- `tenants` → IdentityService
- `tenant_users` → IdentityService
- `sessions` → IdentityService
- `api_tokens` → IdentityService
- `departments` → IdentityService
- `projects` → IdentityService

### Access
- `roles` → AccessService
- `permissions` → AccessService
- `user_roles` → AccessService
- `user_permissions` → AccessService

### Policy
- `relation_tuples` → PolicyService
- `policy_rules` → PolicyService

### Subscription
- `plans` → SubscriptionService
- `subscriptions` → SubscriptionService
- `usage_counters` → SubscriptionService
- `usage_quotas` → SubscriptionService

### Audit
- `audit_logs` → AuditService
- `login_logs` → AuditService

---

## 🎯 الخلاصة

### Backend:
- **6 Modules**: identity, access, policy, subscription, audit, crm
- **6 API Routers**: جميعها مسجلة في `main.py`
- **AAA Middleware**: يعمل على كل request

### Frontend:
- **4 CRM Pages**: Tenants List, Dashboard, Users, Subscription
- **4 IAM Pages**: Roles, Permissions, Policies, Access Control
- **API Wrappers**: في `lib/api.ts`

---

**آخر تحديث:** 2025-01-XX

