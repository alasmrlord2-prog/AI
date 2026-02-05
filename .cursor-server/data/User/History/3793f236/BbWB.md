# 🚀 SHIFTWAVE AI Platform - ثلاث خدمات منفصلة

## 📋 نظرة عامة

نظام شامل يتكون من ثلاث خدمات منفصلة:
- **AI-Agent** - على `ai-agent.bankid-sy.com` (port 3000)
- **CRM** - على `crm.bankid-sy.com` (port 3001)
- **AAA** - على `aaa.bankid-sy.com` (port 3002)

جميع الخدمات متصلة بنفس Backend على port 8000.

---

## 🏗️ البنية

```
ai-agent/
├── backend/              # FastAPI Backend (port 8000)
│   ├── app/              # Application code
│   ├── start.sh          # ✅ تشغيل Backend
│   ├── stop.sh           # ✅ إيقاف Backend
│   └── restart.sh        # ✅ إعادة تشغيل Backend
│
├── frontend/             # Next.js Frontend
│   ├── app/              # Application code
│   ├── start-all.sh      # ✅ تشغيل جميع Frontends
│   ├── stop-all.sh       # ✅ إيقاف جميع Frontends
│   └── pm2-start.sh      # ✅ تشغيل باستخدام PM2
│
├── docker-compose.yml    # Docker configuration
├── ecosystem.config.js   # PM2 configuration
├── nginx-ai-agent-complete.conf  # NGINX config للـ AI-Agent
├── nginx-crm-complete.conf       # NGINX config للـ CRM
├── nginx-aaa-complete.conf       # NGINX config للـ AAA
└── setup-all-services.sh        # إعداد NGINX
```

---

## 🚀 البدء السريع

### الخطوة 1: إعداد NGINX

```bash
./setup-all-services.sh
```

هذا السكربت سيقوم بـ:
- نسخ ملفات NGINX إلى `/etc/nginx/sites-available/`
- تفعيل المواقع
- اختبار التكوين
- إعادة تحميل NGINX

---

### الخطوة 2: تشغيل Backend

```bash
cd backend
./start.sh
```

**التحقق:**
```bash
curl http://localhost:8000/health
```

---

### الخطوة 3: تشغيل Frontends

#### الطريقة 1: PM2 (موصى به)

```bash
cd frontend
./pm2-start.sh
```

#### الطريقة 2: start-all.sh

```bash
cd frontend
./start-all.sh
```

---

## 🎯 URLs النهائية

| الخدمة | Domain | Frontend Port | Backend Port |
|--------|--------|---------------|--------------|
| **AI-Agent** | http://ai-agent.bankid-sy.com | 3000 | 8000 |
| **CRM** | http://crm.bankid-sy.com | 3001 | 8000 |
| **AAA** | http://aaa.bankid-sy.com | 3002 | 8000 |

---

## 🔧 السكربتات الأساسية

### Backend Scripts

```bash
# تشغيل Backend
cd backend && ./start.sh

# إيقاف Backend
cd backend && ./stop.sh

# إعادة تشغيل Backend
cd backend && ./restart.sh
```

### Frontend Scripts

```bash
# تشغيل جميع Frontends (PM2)
cd frontend && ./pm2-start.sh

# تشغيل جميع Frontends (يدوياً)
cd frontend && ./start-all.sh

# إيقاف جميع Frontends
cd frontend && ./stop-all.sh
```

---

## 📡 API Endpoints

### Identity API (`/api/identity/*`)
- `POST /api/identity/login` - تسجيل الدخول
- `GET /api/identity/users` - قائمة المستخدمين
- `POST /api/identity/users` - إنشاء مستخدم
- `GET /api/identity/tenants` - قائمة Tenants

### CRM API (`/api/crm/*`)
- `GET /api/crm/tenants` - قائمة Tenants
- `GET /api/crm/tenants/{id}/dashboard` - Dashboard
- `GET /api/crm/tenants/{id}/users` - مستخدمي Tenant

### Subscription API (`/api/subscription/*`)
- `GET /api/subscription/plans` - قائمة الخطط
- `GET /api/subscription/tenants/{id}/subscription` - حالة الاشتراك

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

## 🛠️ Troubleshooting

### Backend لا يعمل؟

```bash
# تحقق من Logs
cd backend
docker-compose logs backend

# إعادة تشغيل
./restart.sh
```

### Frontend لا يعمل؟

```bash
# تحقق من Logs (PM2)
pm2 logs

# أو (start-all.sh)
tail -f /tmp/frontend-ai-agent.log
tail -f /tmp/frontend-crm.log
tail -f /tmp/frontend-aaa.log

# إعادة تشغيل
pm2 restart all
```

### NGINX لا يعمل؟

```bash
# اختبار التكوين
sudo nginx -t

# عرض الأخطاء
sudo tail -f /var/log/nginx/error.log

# إعادة تحميل
sudo systemctl reload nginx
```

### Port مستخدم؟

```bash
# معرفة ما يستخدم الـ port
lsof -i :8000
lsof -i :3000

# قتل العملية
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### مشاكل Docker؟

```bash
# تنظيف شامل
docker-compose down --remove-orphans
docker system prune -f

# إعادة البناء
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 مراقبة الخدمات

### PM2

```bash
# عرض الحالة
pm2 status

# عرض Logs
pm2 logs

# إيقاف
pm2 stop all

# إعادة تشغيل
pm2 restart all
```

### Docker

```bash
# عرض Containers
docker ps

# عرض Logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### NGINX

```bash
# عرض Logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔄 إعادة التشغيل الكامل

```bash
# 1. إيقاف Frontends
cd frontend && ./stop-all.sh
# أو
pm2 stop all

# 2. إيقاف Backend
cd backend && ./stop.sh

# 3. إعادة تشغيل Backend
cd backend && ./start.sh

# 4. إعادة تشغيل Frontends
cd frontend && ./pm2-start.sh
```

---

## ✅ Checklist النهائي

- [ ] NGINX configurations منسوخة ومفعّلة
- [ ] NGINX تم إعادة تحميله
- [ ] Backend يعمل على port 8000
- [ ] AI-Agent frontend يعمل على port 3000
- [ ] CRM frontend يعمل على port 3001
- [ ] AAA frontend يعمل على port 3002
- [ ] جميع health checks تعمل
- [ ] يمكن الوصول للخدمات عبر الـ domains

---

## 📝 ملاحظات مهمة

- جميع الصفحات تتطلب Authentication
- API Documentation متوفرة على `/docs`
- النظام يدعم Resource-based Usage Tracking
- AAA Middleware يعمل على كل Request
- جميع الخدمات تستخدم نفس Backend على port 8000

---

## 🎯 الخطوات التالية

1. **إنشاء Tenants جديدة** عبر `/crm/tenants`
2. **إضافة Users** عبر `/crm/tenants/{id}/users`
3. **إدارة Plans** عبر API أو Database
4. **إعداد Roles** عبر `/iam/roles`
5. **إعداد Permissions** عبر `/iam/permissions`

---

**آخر تحديث:** 2025-01-XX  
**الإصدار:** 1.0.0
