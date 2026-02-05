# 🚀 SHIFTWAVE AI Platform - CRM + AAA System

## 📋 نظرة عامة

نظام شامل لإدارة العملاء (CRM) مع نظام AAA كامل (Authentication, Authorization, Accounting) مدمج في منصة AI Agent.

**✅ جاهز للاستخدام مع Docker**

---

## 🏗️ البنية

```
ai-agent/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── core/         # AAA Middleware, Database, Security
│   │   ├── identity/     # Users, Tenants, Sessions
│   │   ├── access/       # RBAC (Roles, Permissions)
│   │   ├── policy/       # Zanzibar Policy Engine
│   │   ├── subscription/ # Plans, Subscriptions, Usage
│   │   ├── audit/        # Audit Logs
│   │   ├── crm/          # CRM Service
│   │   └── api/          # API Routes
│   ├── start.sh          # ✅ Start script
│   ├── stop.sh           # ✅ Stop script
│   └── restart.sh        # ✅ Restart script
│
├── frontend/             # Next.js Frontend
│   ├── app/
│   │   ├── crm/          # CRM UI
│   │   └── iam/          # IAM UI
│   ├── start.sh          # ✅ Start script
│   ├── stop.sh           # ✅ Stop script
│   └── restart.sh        # ✅ Restart script
│
└── docker-compose.yml    # ✅ Docker Compose Configuration
```

---

## 🚀 البدء السريع

### 1. تشغيل النظام (Docker)

```bash
# تشغيل كل شيء
docker-compose up -d

# أو تشغيل Backend فقط
cd backend && ./start.sh

# أو تشغيل Frontend فقط
cd frontend && ./start.sh
```

### 2. إعداد البيانات الأولية

```bash
cd backend
python scripts/setup_initial_data.py
```

### 3. الوصول للنظام

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📍 الواجهات - كيف تصل لها؟

> **📖 دليل شامل:** راجع `HOW_TO_ACCESS.md` للتفاصيل الكاملة

### 🔐 تسجيل الدخول
**URL:** http://localhost:3000/login

### 🏢 CRM Pages

| الواجهة | URL | الوظيفة |
|---------|-----|---------|
| **Tenants List** | `http://localhost:3000/crm/tenants` | قائمة Tenants |
| **Tenant Dashboard** | `http://localhost:3000/crm/tenants/{id}` | Dashboard مع 6 Tabs |
| **Users Management** | `http://localhost:3000/crm/tenants/{id}/users` | إدارة المستخدمين |
| **Subscription** | `http://localhost:3000/crm/tenants/{id}/subscription` | إدارة الاشتراكات |

### 🔐 IAM Pages

| الواجهة | URL | الوظيفة |
|---------|-----|---------|
| **Roles** | `http://localhost:3000/iam/roles` | إدارة الأدوار |
| **Permissions** | `http://localhost:3000/iam/permissions` | Permission Matrix |
| **Policies** | `http://localhost:3000/iam/policies` | Zanzibar Policies |
| **Access Control** | `http://localhost:3000/iam/access-control` | Access Testing |

**📖 للمزيد من التفاصيل:** راجع `HOW_TO_ACCESS.md`

---

## 🔧 السكربتات

### Backend Scripts

```bash
# تشغيل Backend
./backend/start.sh

# إيقاف Backend
./backend/stop.sh

# إعادة تشغيل Backend
./backend/restart.sh
```

### Frontend Scripts

```bash
# تشغيل Frontend
./frontend/start.sh

# إيقاف Frontend
./frontend/stop.sh

# إعادة تشغيل Frontend
./frontend/restart.sh
```

---

## 🐳 Docker Commands

```bash
# تشغيل كل شيء
docker-compose up -d

# إيقاف كل شيء
docker-compose down

# إعادة تشغيل
docker-compose restart

# عرض Logs
docker-compose logs -f backend
docker-compose logs -f frontend

# إعادة بناء
docker-compose build --no-cache
```

---

## 📡 API Endpoints

### Identity API (`/api/identity/*`)
- `POST /api/identity/login` - تسجيل الدخول
- `GET /api/identity/users` - قائمة المستخدمين
- `POST /api/identity/users` - إنشاء مستخدم
- `GET /api/identity/tenants` - قائمة Tenants
- `POST /api/identity/tenants` - إنشاء Tenant
- `GET /api/identity/sessions` - الجلسات
- `POST /api/identity/api-tokens` - إنشاء API Token

### CRM API (`/api/crm/*`)
- `GET /api/crm/tenants` - قائمة Tenants
- `GET /api/crm/tenants/{id}/dashboard` - Dashboard
- `GET /api/crm/tenants/{id}/users` - مستخدمي Tenant
- `GET /api/crm/tenants/{id}/usage` - تحليلات الاستهلاك
- `GET /api/crm/tenants/{id}/audit-logs` - سجل العمليات

### Subscription API (`/api/subscription/*`)
- `GET /api/subscription/plans` - قائمة الخطط
- `GET /api/subscription/tenants/{id}/subscription` - حالة الاشتراك
- `GET /api/subscription/subscriptions/{id}/usage` - الاستهلاك

### Access API (`/api/access/*`)
- `GET /api/access/roles` - قائمة الأدوار
- `GET /api/access/permissions` - قائمة الصلاحيات

### Policy API (`/api/policy/*`)
- `GET /api/policy/relations` - قائمة Relations
- `POST /api/policy/check` - التحقق من Relation

**API Documentation:** http://localhost:8000/docs

---

## 🗄️ قاعدة البيانات

### PostgreSQL

**Connection String:**
```
postgresql://aiagent:aiagent123@localhost:5432/ai_agent_db
```

**الجداول الرئيسية:**
- `users` - المستخدمين
- `tenants` - العملاء
- `subscriptions` - الاشتراكات
- `plans` - الخطط
- `roles` - الأدوار
- `permissions` - الصلاحيات
- `audit_logs` - سجل العمليات
- `usage_counters` - تتبع الاستهلاك

---

## 🔐 AAA System

### Authentication
- JWT Tokens
- Sessions Management
- MFA Support
- API Tokens

### Authorization
- RBAC (Role-Based Access Control)
- Zanzibar Policy Engine
- Permission Matrix

### Accounting
- Resource-based Usage Tracking
- Audit Logs
- Login Logs
- Usage Quotas

---

## 📊 Resource Types (Usage Tracking)

النظام يتتبع الاستهلاك حسب نوع المورد:
- `requests` - عدد الطلبات
- `tokens` - AI tokens
- `storage_gb` - التخزين
- `workflow_runs` - تنفيذات Workflows
- `log_volume_gb` - حجم Logs
- `agents` - عدد Agents

---

## 🛠️ Troubleshooting

### Backend لا يعمل؟
```bash
# تحقق من Logs
docker-compose logs backend

# إعادة بناء
docker-compose build backend
docker-compose up -d backend
```

### Frontend لا يعمل؟
```bash
# تحقق من Logs
docker-compose logs frontend

# إعادة بناء
docker-compose build frontend
docker-compose up -d frontend
```

### قاعدة البيانات؟
```bash
# تحقق من PostgreSQL
docker-compose ps postgres

# إعادة تشغيل
docker-compose restart postgres
```

### مشاكل CORS؟
تأكد من أن `CORS_ORIGINS` في `backend/app/core/config.py` يحتوي على:
```python
CORS_ORIGINS = ["http://localhost:3000"]
```

---

## 📚 الوثائق

- **API Docs**: http://localhost:8000/docs
- **Architecture**: `backend/CRM_AAA_ARCHITECTURE.md`
- **Quick Start**: `backend/CRM_AAA_QUICK_START.md`
- **Frontend Docs**: `frontend/CRM_IAM_FRONTEND.md`

---

## 🎯 الخطوات التالية

1. **إنشاء Tenants جديدة** عبر `/crm/tenants`
2. **إضافة Users** عبر `/crm/tenants/{id}/users`
3. **إدارة Plans** عبر API أو Database
4. **إعداد Roles** عبر `/iam/roles`
5. **إعداد Permissions** عبر `/iam/permissions`
6. **اختبار Access Control** عبر `/iam/access-control`

---

## 📝 ملاحظات

- جميع الصفحات تتطلب Authentication
- API Documentation متوفرة على `/docs`
- النظام يدعم Resource-based Usage Tracking
- AAA Middleware يعمل على كل Request

---

**آخر تحديث:** 2025-01-XX
**الإصدار:** 1.0.0
