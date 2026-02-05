# 🗺️ دليل الوصول للواجهات - Access Guide

## 📍 كيف تصل لكل واجهة؟

---

## 🔐 1. تسجيل الدخول

**URL:** http://localhost:3000/login

**الخطوات:**
1. افتح المتصفح
2. اذهب إلى: `http://localhost:3000/login`
3. أدخل:
   - **Email**: (اللي أنشأته في setup_initial_data.py)
   - **Password**: (اللي أدخلته)
4. اضغط Login

**بعد تسجيل الدخول:**
- رح يتم حفظ Token في localStorage
- رح يتم Redirect إلى Dashboard

---

## 🏢 2. CRM - قائمة Tenants

**URL:** http://localhost:3000/crm/tenants

**كيف تصل:**
- من القائمة الجانبية → CRM → Tenants
- أو مباشرة: `http://localhost:3000/crm/tenants`

**الوظيفة:**
- عرض جميع Tenants
- Search و Filter
- Pagination
- Navigation إلى Dashboard

**API:** `GET /api/crm/tenants`

---

## 🏢 3. CRM - Tenant Dashboard

**URL:** http://localhost:3000/crm/tenants/{tenant_id}

**كيف تصل:**
1. من قائمة Tenants → اضغط على أي Tenant
2. أو مباشرة: `http://localhost:3000/crm/tenants/{tenant_id}`

**التبويبات:**

### Overview Tab
- Subscription Status
- Users Summary (أول 5)
- Recent Activity

### Users Tab
- قائمة المستخدمين (أول 10)
- زر "View All Users" → يوديك لصفحة Users الكاملة

### Subscription Tab
- Current Subscription Details
- زر "Manage Subscription" → يوديك لصفحة Subscription

### Usage Analytics Tab
- رسوم بيانية للاستهلاك
- Progress Bars لكل Resource Type
- النسبة المئوية المستخدمة

### Audit Logs Tab
- سجل العمليات الأخيرة
- زر "View All Audit Logs" → (قريباً)

### Incidents Tab
- قائمة الحوادث
- Severity و Status

**API:** `GET /api/crm/tenants/{id}/dashboard`

---

## 👥 4. CRM - إدارة المستخدمين

**URL:** http://localhost:3000/crm/tenants/{tenant_id}/users

**كيف تصل:**
1. من Dashboard → Users Tab → "View All Users"
2. أو مباشرة: `http://localhost:3000/crm/tenants/{tenant_id}/users`

**الوظيفة:**
- قائمة المستخدمين مع تفاصيل كاملة
- عرض Sessions النشطة
- عرض API Tokens
- Last Login Info (IP + Location)
- Revoke Sessions

**API:** `GET /api/crm/tenants/{id}/users`

---

## 💳 5. CRM - إدارة الاشتراكات

**URL:** http://localhost:3000/crm/tenants/{tenant_id}/subscription

**كيف تصل:**
1. من Dashboard → Subscription Tab → "Manage Subscription"
2. أو مباشرة: `http://localhost:3000/crm/tenants/{tenant_id}/subscription`

**الوظيفة:**
- Current Subscription Details
- Usage & Limits (Progress Bars)
- Available Plans
- Upgrade/Downgrade (قريباً)

**API:** 
- `GET /api/subscription/tenants/{id}/subscription`
- `GET /api/subscription/plans`

---

## 🔐 6. IAM - إدارة الأدوار

**URL:** http://localhost:3000/iam/roles

**كيف تصل:**
1. من القائمة الجانبية → IAM → Roles
2. أو مباشرة: `http://localhost:3000/iam/roles`

**الوظيفة:**
- قائمة الأدوار
- Search
- Create Role (Modal)
- عرض Permissions لكل Role

**API:** 
- `GET /api/access/roles`
- `POST /api/access/roles`

---

## 🔑 7. IAM - Permission Matrix

**URL:** http://localhost:3000/iam/permissions

**كيف تصل:**
1. من القائمة الجانبية → IAM → Permissions
2. أو مباشرة: `http://localhost:3000/iam/permissions`

**الوظيفة:**
- جدول الصلاحيات
- Filter by Resource
- Filter by Action
- Search

**API:** `GET /api/access/permissions`

---

## 🎯 8. IAM - Zanzibar Policies

**URL:** http://localhost:3000/iam/policies

**كيف تصل:**
1. من القائمة الجانبية → IAM → Policies
2. أو مباشرة: `http://localhost:3000/iam/policies`

**التبويبات:**

### Relation Tuples Tab
- عرض جميع Relations
- Create Relation Tuple

### Policy Rules Tab
- عرض Policy Rules
- Create Policy Rule

**API:**
- `GET /api/policy/relations`
- `POST /api/policy/relations`
- `GET /api/policy/rules`
- `POST /api/policy/rules`

---

## 🧪 9. IAM - Access Control Testing

**URL:** http://localhost:3000/iam/access-control

**كيف تصل:**
1. من القائمة الجانبية → IAM → Access Control
2. أو مباشرة: `http://localhost:3000/iam/access-control`

**الوظيفة:**
- **Relation Check**: اختبار العلاقات (Zanzibar-style)
- **Permission Check**: اختبار الصلاحيات
- عرض النتائج مع التفاصيل
- عرض Matched Tuples و Paths

**API:**
- `POST /api/policy/check`

---

## 🔗 Quick Links

### بعد تسجيل الدخول:

```
Dashboard → http://localhost:3000
CRM Tenants → http://localhost:3000/crm/tenants
IAM Roles → http://localhost:3000/iam/roles
IAM Permissions → http://localhost:3000/iam/permissions
IAM Policies → http://localhost:3000/iam/policies
IAM Access Control → http://localhost:3000/iam/access-control
```

### API Documentation:

```
Swagger UI → http://localhost:8000/docs
ReDoc → http://localhost:8000/redoc
Health Check → http://localhost:8000/health
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

4. **عرض Dashboard**
   - Overview Tab: نظرة عامة
   - Users Tab: عرض المستخدمين
   - Subscription Tab: حالة الاشتراك
   - Usage Tab: الاستهلاك

5. **إدارة المستخدمين**
   - من Dashboard → Users Tab → "View All Users"
   - أو: `http://localhost:3000/crm/tenants/{tenant_id}/users`

6. **إدارة الاشتراك**
   - من Dashboard → Subscription Tab → "Manage Subscription"
   - أو: `http://localhost:3000/crm/tenants/{tenant_id}/subscription`

---

## 🔧 Troubleshooting

### لا أستطيع الوصول للصفحة؟

1. **تحقق من أن Frontend يعمل:**
   ```bash
   docker-compose ps frontend
   ```

2. **تحقق من أن Backend يعمل:**
   ```bash
   docker-compose ps backend
   ```

3. **تحقق من Authentication:**
   - تأكد من أنك مسجل دخول
   - تحقق من Token في localStorage

### الصفحة فارغة؟

1. **تحقق من Console:**
   - افتح Developer Tools (F12)
   - شوف Console للأخطاء

2. **تحقق من Network:**
   - شوف Network Tab
   - تحقق من API Calls

---

**آخر تحديث:** 2025-01-XX

