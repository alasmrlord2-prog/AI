# 🚀 SHIFTWAVE AI Platform

نظام شامل يتكون من **ثلاث واجهات منفصلة تماماً** متصلة بـ Backend موحد.

---

## 📋 الواجهات (Frontends)

### 1. Dashboard (AI Agent)
- **Domain:** `ai-agent.bankid-sy.com`
- **Port:** 3000
- **الوظيفة:** واجهة المستخدم العادي
- **المميزات:**
  - Chat مع AI Agent
  - إدارة Services
  - Monitoring & Analytics
  - Knowledge Base
  - Workflows

### 2. CRM (Customer Relationship Management)
- **Domain:** `crm.bankid-sy.com`
- **Port:** 3001
- **الوظيفة:** إدارة Tenants و Users و Subscriptions
- **المميزات:**
  - إنشاء وإدارة Tenants
  - إدارة Users لكل Tenant
  - إدارة Subscription Plans
  - Analytics & Reports
  - Audit Logs

### 3. AAA (Authentication, Authorization, Accounting)
- **Domain:** `aaa.bankid-sy.com`
- **Port:** 3002
- **الوظيفة:** إدارة Authentication و Authorization
- **المميزات:**
  - إدارة API Tokens
  - إدارة Sessions
  - إدارة Users
  - Audit Logs
  - Security Policies

---

## 🏗️ البنية التحتية

### Backend
- **Technology:** FastAPI (Python 3.11)
- **Port:** 8000
- **Database:** PostgreSQL (Docker)
- **AI:** Ollama (Docker)
- **Location:** `/home/ai/ai-agent/backend`

### Frontend
- **Technology:** Next.js 16 (React)
- **Ports:** 3000 (Dashboard), 3001 (CRM), 3002 (AAA)
- **Location:** `/home/ai/ai-agent/frontend`

### Reverse Proxy
- **Technology:** NGINX
- **Port:** 80
- **Configs:** `/etc/nginx/sites-available/`

---

## 🚀 التشغيل السريع

### 1. تشغيل Backend

```bash
cd /home/ai/ai-agent/backend
./start.sh
```

**ما يفعله:**
- يوقف أي process موجود على port 8000
- يتحقق من توفر Python 3.11
- يتحقق من الـ routers (identity, CRM)
- يبدأ Backend مباشرة بـ uvicorn
- ينتظر حتى Backend يكون جاهز

### 2. إيقاف Backend

```bash
cd /home/ai/ai-agent/backend
./stop.sh
```

### 3. إعادة تشغيل Backend

```bash
cd /home/ai/ai-agent/backend
./restart.sh
```

### 4. تشغيل Frontends

```bash
cd /home/ai/ai-agent/frontend
./start-all.sh
```

**ما يفعله:**
- يبدأ Dashboard على port 3000
- يبدأ CRM على port 3001
- يبدأ AAA على port 3002
- يحفظ PIDs في `/tmp/frontend-*.pid`

### 5. إيقاف Frontends

```bash
cd /home/ai/ai-agent/frontend
./stop-all.sh
```

### 6. تشغيل Frontends بـ PM2

```bash
cd /home/ai/ai-agent/frontend
./pm2-start.sh
```

---

## 📝 Scripts المتاحة

### Backend Scripts (`/backend/`)
1. **`start.sh`** - بدء Backend (Direct Mode - uvicorn)
2. **`stop.sh`** - إيقاف Backend
3. **`restart.sh`** - إعادة تشغيل Backend

### Frontend Scripts (`/frontend/`)
4. **`start-all.sh`** - بدء جميع Frontends
5. **`stop-all.sh`** - إيقاف جميع Frontends
6. **`pm2-start.sh`** - بدء Frontends بـ PM2

---

## 🔐 بيانات الدخول الافتراضية

### Admin User
- **Email:** `admin@example.com`
- **Password:** `admin123`
- **Role:** `admin`

**يمكن استخدامه في:**
- ✅ Dashboard (`ai-agent.bankid-sy.com`)
- ✅ CRM (`crm.bankid-sy.com`)
- ✅ AAA (`aaa.bankid-sy.com`)

---

## 🔄 Workflow الكامل

```
1. Admin Login إلى CRM
   └─> http://crm.bankid-sy.com
   └─> Email: admin@example.com
   └─> Password: admin123

2. إنشاء Tenant جديد
   └─> CRM Dashboard → Tenants → Create New Tenant

3. إنشاء User للـ Tenant
   └─> Tenants → اختر Tenant → Users → Create User

4. User يستخدم Dashboard
   └─> http://ai-agent.bankid-sy.com
   └─> Login بـ بيانات User الجديد

5. User يستخدم AAA
   └─> http://aaa.bankid-sy.com
   └─> Login بـ نفس بيانات User
```

---

## 🌐 NGINX Configuration

### Domains
- `ai-agent.bankid-sy.com` → `localhost:3000` (Dashboard)
- `crm.bankid-sy.com` → `localhost:3001` (CRM)
- `aaa.bankid-sy.com` → `localhost:3002` (AAA)

### API Proxy
جميع `/api/*` requests يتم توجيهها إلى `localhost:8000` (Backend)

### Config Files
- `/etc/nginx/sites-available/ai-agent.bankid-sy.com`
- `/etc/nginx/sites-available/crm.bankid-sy.com`
- `/etc/nginx/sites-available/aaa.bankid-sy.com`

---

## 📊 البنية

```
ai-agent/
├── backend/              # FastAPI Backend
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── identity/     # Identity service
│   │   ├── crm/          # CRM service
│   │   └── main.py       # FastAPI app
│   ├── start.sh          # Start script
│   ├── stop.sh           # Stop script
│   └── restart.sh        # Restart script
│
├── frontend/             # Next.js Frontend
│   ├── app/              # Next.js app directory
│   │   ├── page.tsx      # Dashboard home
│   │   ├── crm/          # CRM routes
│   │   └── aaa/          # AAA routes
│   ├── components/       # React components
│   ├── start-all.sh      # Start all frontends
│   ├── stop-all.sh       # Stop all frontends
│   └── pm2-start.sh      # PM2 start
│
├── README.md             # هذا الملف
├── PROJECT_STRUCTURE.md  # بنية المشروع التفصيلية
├── SERVICES_TOOLS.md     # جميع Services مع الأدوات والكود
└── docker-compose.yml    # Docker configuration
```

---

## 🔧 المتطلبات

### Backend
- Python 3.11
- uvicorn
- FastAPI
- PostgreSQL (Docker)
- Ollama (Docker)

### Frontend
- Node.js 18+
- npm
- Next.js 16

### System
- NGINX
- Docker & Docker Compose (اختياري)

---

## 📝 Logs

### Backend Logs
- `/tmp/backend.log` - Backend logs

### Frontend Logs
- `/tmp/frontend-ai-agent.log` - Dashboard logs
- `/tmp/frontend-crm.log` - CRM logs
- `/tmp/frontend-aaa.log` - AAA logs

### PM2 Logs
- `./frontend/logs/pm2-*.log`

---

## ✅ التحقق من الحالة

### Backend
```bash
curl http://localhost:8000/health
```

### Frontend
```bash
curl http://localhost:3000  # Dashboard
curl http://localhost:3001  # CRM
curl http://localhost:3002  # AAA
```

### Ports
```bash
ss -tlnp | grep -E ':(3000|3001|3002|8000)'
```

---

## 🐛 Troubleshooting

### Backend لا يبدأ
1. تحقق من Python 3.11: `which python3.11`
2. تحقق من email-validator: `python3.11 -m pip list | grep email-validator`
3. تحقق من Logs: `tail -f /tmp/backend.log`

### Frontend لا يبدأ
1. تحقق من Node.js: `node --version`
2. تحقق من Ports: `ss -tlnp | grep -E ':(3000|3001|3002)'`
3. تحقق من Logs: `tail -f /tmp/frontend-*.log`

### 502 Bad Gateway
1. تحقق من أن Frontend يعمل: `curl http://localhost:3001`
2. تحقق من NGINX config: `sudo nginx -t`
3. أعد تحميل NGINX: `sudo systemctl reload nginx`

---

## 📚 الوثائق

- **`PROJECT_STRUCTURE.md`** - بنية المشروع التفصيلية
- **`SERVICES_TOOLS.md`** - جميع Services مع الأدوات والكود المستخدم

---

## 🎯 الميزات الرئيسية

### Dashboard
- ✅ Chat مع AI Agent
- ✅ إدارة Services (Security, DevOps, AI)
- ✅ Monitoring & Analytics
- ✅ Knowledge Base
- ✅ Workflows Builder

### CRM
- ✅ إدارة Tenants
- ✅ إدارة Users
- ✅ إدارة Subscriptions
- ✅ Analytics & Reports
- ✅ Audit Logs

### AAA
- ✅ إدارة API Tokens
- ✅ إدارة Sessions
- ✅ إدارة Users
- ✅ Security Policies
- ✅ Audit Logs

---

## 📞 الدعم

للمساعدة أو الأسئلة، راجع:
- `PROJECT_STRUCTURE.md` - للبنية التفصيلية
- `SERVICES_TOOLS.md` - للأدوات والكود

---

**تم التطوير بواسطة:** Shiftwave Team  
**الإصدار:** 1.0.0
