# 🗺️ جميع الواجهات - All Interfaces

## 📍 كيف تصل لكل واجهة؟

---

## 🔐 1. تسجيل الدخول

**URL:** `http://localhost:3000/login`

**الخطوات:**
1. افتح المتصفح
2. اذهب إلى `/login`
3. أدخل Email و Password
4. اضغط Login

**بعد تسجيل الدخول:**
- Token رح يتم حفظه تلقائياً
- رح يتم Redirect للـ Dashboard

---

## 🏢 CRM Pages

### 2. قائمة Tenants

**URL:** `http://localhost:3000/crm/tenants`

**كيف تصل:**
- من القائمة الجانبية → CRM → Tenants
- أو مباشرة: `/crm/tenants`

**الوظيفة:**
- عرض جميع Tenants
- Search و Filter
- Pagination
- Navigation إلى Dashboard

**API:** `GET /api/crm/tenants`

---

### 3. Tenant Dashboard

**URL:** `http://localhost:3000/crm/tenants/{tenant_id}`

**كيف تصل:**
1. من قائمة Tenants → اضغط على Tenant
2. أو مباشرة: `/crm/tenants/{tenant_id}`

**التبويبات (6 Tabs):**

#### Tab 1: Overview
- Subscription Status
- Users Summary (أول 5)
- Recent Activity

#### Tab 2: Users
- قائمة المستخدمين (أول 10)
- زر "View All Users" → `/crm/tenants/{id}/users`

#### Tab 3: Subscription
- Current Subscription Details
- زر "Manage Subscription" → `/crm/tenants/{id}/subscription`

#### Tab 4: Usage Analytics
- رسوم بيانية للاستهلاك
- Progress Bars لكل Resource Type
- النسبة المئوية المستخدمة

#### Tab 5: Audit Logs
- سجل العمليات الأخيرة
- عرض Activity مع Timestamps

#### Tab 6: Incidents
- قائمة الحوادث
- Severity و Status

**API:** `GET /api/crm/tenants/{id}/dashboard`

---

### 4. إدارة المستخدمين

**URL:** `http://localhost:3000/crm/tenants/{tenant_id}/users`

**كيف تصل:**
1. من Dashboard → Users Tab → "View All Users"
2. أو مباشرة: `/crm/tenants/{tenant_id}/users`

**الوظيفة:**
- قائمة المستخدمين مع تفاصيل
- عرض Sessions النشطة
- عرض API Tokens
- Last Login Info (IP + Location)
- Revoke Sessions

**API:** `GET /api/crm/tenants/{id}/users`

---

### 5. إدارة الاشتراكات

**URL:** `http://localhost:3000/crm/tenants/{tenant_id}/subscription`

**كيف تصل:**
1. من Dashboard → Subscription Tab → "Manage Subscription"
2. أو مباشرة: `/crm/tenants/{tenant_id}/subscription`

**الوظيفة:**
- Current Subscription Details
- Usage & Limits (Progress Bars)
- Available Plans
- Upgrade/Downgrade

**API:**
- `GET /api/subscription/tenants/{id}/subscription`
- `GET /api/subscription/plans`

---

## 🔐 IAM Pages

### 6. إدارة الأدوار

**URL:** `http://localhost:3000/iam/roles`

**كيف تصل:**
1. من القائمة الجانبية → IAM → Roles
2. أو مباشرة: `/iam/roles`

**الوظيفة:**
- قائمة الأدوار
- Search
- Create Role (Modal)
- عرض Permissions

**API:**
- `GET /api/access/roles`
- `POST /api/access/roles`

---

### 7. Permission Matrix

**URL:** `http://localhost:3000/iam/permissions`

**كيف تصل:**
1. من القائمة الجانبية → IAM → Permissions
2. أو مباشرة: `/iam/permissions`

**الوظيفة:**
- جدول الصلاحيات
- Filter by Resource
- Filter by Action
- Search

**API:** `GET /api/access/permissions`

---

### 8. Zanzibar Policies

**URL:** `http://localhost:3000/iam/policies`

**كيف تصل:**
1. من القائمة الجانبية → IAM → Policies
2. أو مباشرة: `/iam/policies`

**التبويبات:**

#### Relation Tuples Tab
- عرض جميع Relations
- Create Relation Tuple

#### Policy Rules Tab
- عرض Policy Rules
- Create Policy Rule

**API:**
- `GET /api/policy/relations`
- `POST /api/policy/relations`
- `GET /api/policy/rules`
- `POST /api/policy/rules`

---

### 9. Access Control Testing

**URL:** `http://localhost:3000/iam/access-control`

**كيف تصل:**
1. من القائمة الجانبية → IAM → Access Control
2. أو مباشرة: `/iam/access-control`

**الوظيفة:**
- **Relation Check**: اختبار العلاقات (Zanzibar-style)
- **Permission Check**: اختبار الصلاحيات
- عرض النتائج مع التفاصيل
- عرض Matched Tuples و Paths

**API:** `POST /api/policy/check`

---

## 🔗 Quick Links

### بعد تسجيل الدخول:

```
CRM Tenants → /crm/tenants
Tenant Dashboard → /crm/tenants/{id}
Users → /crm/tenants/{id}/users
Subscription → /crm/tenants/{id}/subscription

IAM Roles → /iam/roles
IAM Permissions → /iam/permissions
IAM Policies → /iam/policies
IAM Access Control → /iam/access-control
```

---

## 📱 Navigation Flow

### من Login:
```
Login → Dashboard → CRM/IAM
```

### من CRM:
```
Tenants List → Tenant Dashboard → Users/Subscription
```

### من IAM:
```
Roles → Permissions → Policies → Access Control
```

---

## 🎯 مثال عملي

### السيناريو: إدارة Tenant جديد

1. **تسجيل الدخول**
   - `http://localhost:3000/login`

2. **الذهاب لـ CRM**
   - `http://localhost:3000/crm/tenants`

3. **اختيار Tenant**
   - اضغط على Tenant من القائمة
   - أو: `http://localhost:3000/crm/tenants/{tenant_id}`

4. **استكشاف Dashboard**
   - Overview Tab: نظرة عامة
   - Users Tab: عرض المستخدمين
   - Subscription Tab: حالة الاشتراك
   - Usage Tab: الاستهلاك
   - Audit Tab: سجل العمليات
   - Incidents Tab: الحوادث

5. **إدارة المستخدمين**
   - من Dashboard → Users Tab → "View All Users"
   - أو: `http://localhost:3000/crm/tenants/{tenant_id}/users`

6. **إدارة الاشتراك**
   - من Dashboard → Subscription Tab → "Manage Subscription"
   - أو: `http://localhost:3000/crm/tenants/{tenant_id}/subscription`

---

**آخر تحديث:** 2025-01-XX

