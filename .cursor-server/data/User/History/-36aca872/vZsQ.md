# 📖 الدليل الشامل - Complete Guide

## 🎯 نظرة عامة

هذا الدليل يوضح **كل شيء** عن نظام CRM + AAA:
- البنية الكاملة
- كيف تشغّله
- كيف تصل لكل واجهة
- Docker Setup
- API Endpoints
- Troubleshooting

---

## 🏗️ البنية الكاملة

### Backend Structure

```
backend/app/
├── core/
│   └── aaa_middleware.py      ✅ AAA Middleware
├── identity/                   ✅ Users, Tenants, Sessions
├── access/                     ✅ RBAC (Roles, Permissions)
├── policy/                     ✅ Zanzibar Policy Engine
├── subscription/               ✅ Plans, Subscriptions, Usage
├── audit/                      ✅ Audit Logs
├── crm/                        ✅ CRM Service
└── api/                        ✅ API Routes
```

### Frontend Structure

```
frontend/app/
├── crm/
│   └── tenants/
│       ├── page.tsx            ✅ قائمة Tenants
│       └── [tenantId]/
│           ├── page.tsx        ✅ Dashboard (6 Tabs)
│           ├── users/page.tsx  ✅ إدارة المستخدمين
│           └── subscription/   ✅ إدارة الاشتراكات
└── iam/
    ├── roles/page.tsx          ✅ إدارة الأدوار
    ├── permissions/page.tsx     ✅ Permission Matrix
    ├── policies/page.tsx        ✅ Zanzibar Policies
    └── access-control/page.tsx  ✅ Access Testing
```

---

## 🚀 التشغيل

### الطريقة 1: Docker (مُوصى بها)

```bash
# 1. تشغيل كل شيء
docker-compose up -d

# 2. إعداد البيانات
cd backend
python scripts/setup_initial_data.py

# 3. تسجيل الدخول
# http://localhost:3000/login
```

### الطريقة 2: السكربتات

```bash
# Backend
cd backend && ./start.sh

# Frontend
cd frontend && ./start.sh

# إعداد البيانات
cd backend && python scripts/setup_initial_data.py
```

---

## 📍 الوصول للواجهات

### 🔐 1. تسجيل الدخول

**URL:** http://localhost:3000/login

**الخطوات:**
1. افتح المتصفح
2. اذهب إلى `/login`
3. أدخل Email و Password
4. اضغط Login

---

### 🏢 2. CRM - قائمة Tenants

**URL:** http://localhost:3000/crm/tenants

**كيف تصل:**
- من القائمة الجانبية → CRM → Tenants
- أو مباشرة: `/crm/tenants`

**الوظيفة:**
- عرض جميع Tenants
- Search و Filter
- Pagination
- Navigation إلى Dashboard

---

### 🏢 3. CRM - Tenant Dashboard

**URL:** http://localhost:3000/crm/tenants/{tenant_id}

**كيف تصل:**
- من قائمة Tenants → اضغط على Tenant
- أو مباشرة: `/crm/tenants/{tenant_id}`

**التبويبات (6 Tabs):**

#### Overview Tab
- Subscription Status
- Users Summary (أول 5)
- Recent Activity

#### Users Tab
- قائمة المستخدمين (أول 10)
- زر "View All Users" → `/crm/tenants/{id}/users`

#### Subscription Tab
- Current Subscription Details
- زر "Manage Subscription" → `/crm/tenants/{id}/subscription`

#### Usage Analytics Tab
- رسوم بيانية للاستهلاك
- Progress Bars لكل Resource Type
- النسبة المئوية المستخدمة

#### Audit Logs Tab
- سجل العمليات الأخيرة
- عرض Activity مع Timestamps

#### Incidents Tab
- قائمة الحوادث
- Severity و Status

---

### 👥 4. CRM - إدارة المستخدمين

**URL:** http://localhost:3000/crm/tenants/{tenant_id}/users

**كيف تصل:**
- من Dashboard → Users Tab → "View All Users"
- أو مباشرة: `/crm/tenants/{tenant_id}/users`

**الوظيفة:**
- قائمة المستخدمين مع تفاصيل
- عرض Sessions النشطة
- عرض API Tokens
- Last Login Info (IP + Location)
- Revoke Sessions

---

### 💳 5. CRM - إدارة الاشتراكات

**URL:** http://localhost:3000/crm/tenants/{tenant_id}/subscription

**كيف تصل:**
- من Dashboard → Subscription Tab → "Manage Subscription"
- أو مباشرة: `/crm/tenants/{tenant_id}/subscription`

**الوظيفة:**
- Current Subscription Details
- Usage & Limits (Progress Bars)
- Available Plans
- Upgrade/Downgrade (قريباً)

---

### 🔐 6. IAM - إدارة الأدوار

**URL:** http://localhost:3000/iam/roles

**كيف تصل:**
- من القائمة الجانبية → IAM → Roles
- أو مباشرة: `/iam/roles`

**الوظيفة:**
- قائمة الأدوار
- Search
- Create Role
- عرض Permissions

---

### 🔑 7. IAM - Permission Matrix

**URL:** http://localhost:3000/iam/permissions

**كيف تصل:**
- من القائمة الجانبية → IAM → Permissions
- أو مباشرة: `/iam/permissions`

**الوظيفة:**
- جدول الصلاحيات
- Filter by Resource
- Filter by Action
- Search

---

### 🎯 8. IAM - Zanzibar Policies

**URL:** http://localhost:3000/iam/policies

**كيف تصل:**
- من القائمة الجانبية → IAM → Policies
- أو مباشرة: `/iam/policies`

**التبويبات:**
- **Relation Tuples Tab**: عرض Relations
- **Policy Rules Tab**: عرض Rules

---

### 🧪 9. IAM - Access Control Testing

**URL:** http://localhost:3000/iam/access-control

**كيف تصل:**
- من القائمة الجانبية → IAM → Access Control
- أو مباشرة: `/iam/access-control`

**الوظيفة:**
- Relation Check: اختبار العلاقات
- Permission Check: اختبار الصلاحيات
- عرض النتائج مع التفاصيل

---

## 🔧 السكربتات (6 فقط)

### Backend Scripts

```bash
./backend/start.sh      # تشغيل Backend
./backend/stop.sh       # إيقاف Backend
./backend/restart.sh     # إعادة تشغيل Backend
```

### Frontend Scripts

```bash
./frontend/start.sh      # تشغيل Frontend
./frontend/stop.sh       # إيقاف Frontend
./frontend/restart.sh    # إعادة تشغيل Frontend
```

---

## 🐳 Docker

### التشغيل

```bash
docker-compose up -d
```

### الإيقاف

```bash
docker-compose down
```

### Logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**للمزيد:** راجع `DOCKER_SETUP.md`

---

## 📡 API Endpoints

### Identity
- `POST /api/identity/login` - تسجيل الدخول
- `GET /api/identity/users` - قائمة المستخدمين
- `GET /api/identity/tenants` - قائمة Tenants

### CRM
- `GET /api/crm/tenants` - قائمة Tenants
- `GET /api/crm/tenants/{id}/dashboard` - Dashboard
- `GET /api/crm/tenants/{id}/users` - المستخدمين
- `GET /api/crm/tenants/{id}/usage` - الاستهلاك

### Subscription
- `GET /api/subscription/plans` - الخطط
- `GET /api/subscription/tenants/{id}/subscription` - حالة الاشتراك

**API Docs:** http://localhost:8000/docs

---

## 🗄️ قاعدة البيانات

### PostgreSQL

**Connection:**
```
postgresql://aiagent:aiagent123@postgres:5432/ai_agent_db
```

**الجداول:**
- `users`, `tenants`, `subscriptions`, `plans`
- `roles`, `permissions`, `audit_logs`
- `usage_counters`, `relation_tuples`

---

## 🔐 AAA System

### Authentication
- JWT Tokens
- Sessions
- API Tokens

### Authorization
- RBAC (Roles, Permissions)
- Zanzibar Policy Engine

### Accounting
- Resource-based Usage Tracking
- Audit Logs
- Usage Quotas

---

## 🛠️ Troubleshooting

### Backend لا يعمل؟
```bash
docker-compose logs backend
docker-compose restart backend
```

### Frontend لا يعمل؟
```bash
docker-compose logs frontend
docker-compose restart frontend
```

### قاعدة البيانات؟
```bash
docker-compose ps postgres
docker-compose restart postgres
```

---

## 📚 الملفات المرجعية

- **README.md** - هذا الملف (دليل شامل)
- **HOW_TO_ACCESS.md** - كيف تصل لكل واجهة
- **DOCKER_SETUP.md** - دليل Docker
- **QUICK_REFERENCE.md** - مرجع سريع

---

**آخر تحديث:** 2025-01-XX

