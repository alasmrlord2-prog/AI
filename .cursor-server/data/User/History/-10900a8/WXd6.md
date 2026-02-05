# 🔄 Workflow الكامل: Dashboard → CRM → AAA

## 📋 نظرة عامة

النظام يتكون من **3 تطبيقات منفصلة** تعمل على منافذ مختلفة:

1. **Dashboard (AI Agent)** - Port 3000
2. **CRM** - Port 3001  
3. **AAA** - Port 3002

جميعها تتصل بـ **Backend واحد** على Port 8000

---

## 🌐 البنية التحتية (Infrastructure)

### NGINX Reverse Proxy

NGINX يعمل كـ reverse proxy ويوجه الطلبات بناءً على domain name:

```
┌─────────────────────────────────────────────────────────┐
│                    NGINX (Port 80)                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ai-agent.bankid-sy.com  →  localhost:3000 (Dashboard) │
│  crm.bankid-sy.com       →  localhost:3001 (CRM)       │
│  aaa.bankid-sy.com       →  localhost:3002 (AAA)       │
│                                                           │
│  جميع /api/* → localhost:8000 (Backend)                 │
└─────────────────────────────────────────────────────────┘
```

### Next.js Middleware

Middleware يعيد التوجيه تلقائياً:
- `crm.bankid-sy.com/` → `/crm`
- `aaa.bankid-sy.com/` → `/aaa`
- `ai-agent.bankid-sy.com/` → `/` (Dashboard)

---

## 🔐 بيانات الدخول الافتراضية

### المستخدم الافتراضي (Admin):
- **Email:** `admin@example.com`
- **Password:** `admin123`
- **Role:** `admin`

هذا المستخدم يمكنه:
- ✅ الدخول إلى CRM
- ✅ الدخول إلى AAA
- ✅ الدخول إلى Dashboard
- ✅ إنشاء Tenants جديدة
- ✅ إنشاء Users لكل Tenant

---

## 📝 Workflow الكامل

### 1️⃣ الدخول إلى CRM

```
1. افتح: http://crm.bankid-sy.com
   ↓
2. Middleware يعيد التوجيه إلى: /crm
   ↓
3. إذا لم تكن مسجل دخول → /crm/login
   ↓
4. أدخل:
   Email: admin@example.com
   Password: admin123
   ↓
5. Frontend يرسل POST إلى: /api/identity/login
   ↓
6. NGINX يمرر الطلب إلى: localhost:8000/api/identity/login
   ↓
7. Backend يتحقق من البيانات ويعيد Token
   ↓
8. Frontend يحفظ Token في localStorage
   ↓
9. يتم التوجيه إلى: /crm (CRM Dashboard)
```

### 2️⃣ إنشاء Tenant جديد

```
1. من CRM Dashboard → اضغط "View All Tenants"
   ↓
2. اضغط "Create New Tenant"
   ↓
3. املأ البيانات:
   - Tenant Name
   - Contact Email
   - Subscription Plan
   - etc.
   ↓
4. Frontend يرسل POST إلى: /api/crm/tenants
   ↓
5. Backend ينشئ Tenant في Database
   ↓
6. يعود Tenant ID الجديد
```

### 3️⃣ إنشاء User لـ Tenant

```
1. من CRM → Tenants → اختر Tenant
   ↓
2. اضغط "Users" tab
   ↓
3. اضغط "Create User"
   ↓
4. املأ البيانات:
   - Email
   - Password
   - Name
   - Role
   ↓
5. Frontend يرسل POST إلى: /api/crm/tenants/{tenant_id}/users
   ↓
6. Backend ينشئ User ويربطه بـ Tenant
   ↓
7. User يمكنه الآن الدخول إلى Dashboard و AAA
```

### 4️⃣ الدخول إلى Dashboard (AI Agent)

```
1. افتح: http://ai-agent.bankid-sy.com
   ↓
2. إذا لم تكن مسجل دخول → /login
   ↓
3. أدخل بيانات User الذي أنشأته في CRM:
   Email: user@tenant.com
   Password: [password]
   ↓
4. Frontend يرسل POST إلى: /api/identity/login
   ↓
5. Backend يتحقق ويعيد Token
   ↓
6. يتم التوجيه إلى: / (Dashboard)
   ↓
7. User يمكنه استخدام جميع خدمات Dashboard
```

### 5️⃣ الدخول إلى AAA

```
1. افتح: http://aaa.bankid-sy.com
   ↓
2. Middleware يعيد التوجيه إلى: /aaa
   ↓
3. إذا لم تكن مسجل دخول → /aaa/login
   ↓
4. أدخل نفس بيانات User:
   Email: user@tenant.com
   Password: [password]
   ↓
5. Frontend يرسل POST إلى: /api/identity/login
   ↓
6. Backend يتحقق ويعيد Token
   ↓
7. يتم التوجيه إلى: /aaa (AAA Dashboard)
   ↓
8. User يمكنه:
   - إدارة Tokens
   - عرض Sessions
   - إدارة Users
   - Audit Logs
```

---

## 🔄 تدفق البيانات (Data Flow)

### Frontend → Backend Communication

```
Browser (Frontend)
    ↓
    POST /api/identity/login
    ↓
NGINX (Reverse Proxy)
    ↓
    proxy_pass http://localhost:8000
    ↓
Backend (FastAPI on Port 8000)
    ↓
    Database (SQLite/PostgreSQL)
    ↓
    Response with Token
    ↓
NGINX
    ↓
Frontend
    ↓
localStorage.setItem("auth_token", token)
```

### Authentication Flow

```
1. User يدخل Email/Password
   ↓
2. Frontend يرسل إلى /api/identity/login
   ↓
3. Backend:
   - يتحقق من Email في Database
   - يتحقق من Password Hash
   - ينشئ JWT Token
   - يعيد Token + User Info
   ↓
4. Frontend:
   - يحفظ Token في localStorage
   - يضيف Token في Headers لجميع الطلبات التالية
   ↓
5. Backend يتحقق من Token في كل request
```

---

## 🗂️ هيكل المشروع

```
ai-agent/
├── frontend/              # Next.js Application
│   ├── app/
│   │   ├── page.tsx      # Dashboard Home
│   │   ├── crm/          # CRM Routes
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── login/
│   │   │   └── tenants/
│   │   └── aaa/          # AAA Routes
│   │       ├── layout.tsx
│   │       ├── page.tsx
│   │       ├── login/
│   │       └── users/
│   ├── middleware.ts     # Auto-redirect based on domain
│   └── components/
│       ├── layout/       # Dashboard Components
│       ├── crm/          # CRM Components
│       └── aaa/          # AAA Components
│
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── identity_api.py
│   │   │   └── crm_api.py
│   │   ├── auth.py
│   │   └── main.py
│   └── database/
│
└── /etc/nginx/sites-available/
    ├── ai-agent.bankid-sy.com
    ├── crm.bankid-sy.com
    └── aaa.bankid-sy.com
```

---

## ✅ Checklist: التحقق من كل شيء

### الخدمات (Services)
- [x] Dashboard يعمل على Port 3000
- [x] CRM يعمل على Port 3001
- [x] AAA يعمل على Port 3002
- [x] Backend يعمل على Port 8000

### NGINX
- [x] ai-agent.bankid-sy.com → localhost:3000
- [x] crm.bankid-sy.com → localhost:3001
- [x] aaa.bankid-sy.com → localhost:3002
- [x] جميع /api/* → localhost:8000

### Middleware
- [x] crm.bankid-sy.com/ → /crm
- [x] aaa.bankid-sy.com/ → /aaa
- [x] ai-agent.bankid-sy.com/ → /

### Authentication
- [x] Login يعمل في CRM
- [x] Login يعمل في AAA
- [x] Login يعمل في Dashboard
- [x] Token يتم حفظه في localStorage
- [x] API calls تستخدم Token

### Frontend → Backend
- [x] Frontend يستخدم نفس hostname (ليس localhost)
- [x] NGINX يمرر /api/* إلى Backend
- [x] CORS معطل (جميع origins مسموحة)

---

## 🚀 خطوات البدء السريع

### 1. التحقق من الخدمات:
```bash
# Dashboard
curl http://ai-agent.bankid-sy.com

# CRM
curl http://crm.bankid-sy.com

# AAA
curl http://aaa.bankid-sy.com

# Backend
curl http://localhost:8000/health
```

### 2. تسجيل الدخول:
1. افتح `http://crm.bankid-sy.com`
2. استخدم: `admin@example.com` / `admin123`
3. أنشئ Tenant جديد
4. أنشئ User للـ Tenant
5. استخدم بيانات User للدخول إلى Dashboard و AAA

---

## 📊 ملخص Workflow

```
┌─────────────┐
│   Admin     │
│  Login CRM  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Create      │
│ Tenant      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Create      │
│ User        │
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Dashboard│   │   CRM    │   │   AAA    │
│  Login   │   │  Login   │   │  Login   │
└──────────┘   └──────────┘   └──────────┘
```

---

## 🎯 النتيجة النهائية

✅ **3 تطبيقات منفصلة تماماً:**
- Dashboard: صفحة مستقلة بكل خدماتها
- CRM: صفحة مستقلة لإدارة Tenants و Users
- AAA: صفحة مستقلة لإدارة Authentication & Authorization

✅ **كل تطبيق له:**
- Layout خاص
- Sidebar خاص
- Header خاص
- Routes خاصة

✅ **جميعها تتصل بـ Backend واحد:**
- Authentication موحد
- Database موحد
- API موحد

✅ **Workflow كامل:**
- Admin → CRM → Create Tenant → Create User → User يستخدم Dashboard & AAA

