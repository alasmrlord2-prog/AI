# ⚡ Quick Start Guide - SHIFTWAVE AI Platform

## 🎯 البنية النهائية (بدون لف ودوران)

### الواجهات الثلاث المنفصلة:

```
┌─────────────────────────────────────────────────────────┐
│  Dashboard (port 3000)                                  │
│  ai-agent.bankid-sy.com                                 │
│  └─> واجهة المستخدم العادي                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CRM (port 3001)                                         │
│  crm.bankid-sy.com                                      │
│  └─> واجهة إدارة Tenants/Users/Subscriptions           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  AAA (port 3002)                                         │
│  aaa.bankid-sy.com                                      │
│  └─> واجهة إدارة Authentication/Authorization/Accounting│
└─────────────────────────────────────────────────────────┘

                    ↓ جميعهم ↓

┌─────────────────────────────────────────────────────────┐
│  Backend API (port 8000)                                 │
│  http://localhost:8000                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 خطوات التشغيل (3 خطوات فقط)

### 1️⃣ إعداد NGINX

```bash
sudo ./setup-all-services.sh
```

**ما يحدث:**
- نسخ ملفات NGINX الثلاثة
- تفعيل المواقع
- اختبار وإعادة تحميل NGINX

### 2️⃣ تشغيل Backend

```bash
cd backend
./start.sh
```

**ما يحدث:**
- تشغيل PostgreSQL
- تشغيل Ollama
- تشغيل Backend API

### 3️⃣ تشغيل Frontends

```bash
cd frontend
./pm2-start.sh
```

**ما يحدث:**
- Dashboard على port 3000
- CRM على port 3001
- AAA على port 3002

---

## ✅ التحقق من الحالة

### فحص البورتات:

```bash
netstat -tlnp | grep -E '3000|3001|3002|8000'
```

### فحص NGINX:

```bash
sudo nginx -t
sudo systemctl status nginx
```

### فحص PM2:

```bash
pm2 status
pm2 logs
```

---

## 🔗 URLs النهائية

| الخدمة | URL | Port | الوظيفة |
|--------|-----|------|---------|
| **Dashboard** | http://ai-agent.bankid-sy.com | 3000 | واجهة المستخدم العادي |
| **CRM** | http://crm.bankid-sy.com | 3001 | إدارة Tenants/Users/Subscriptions |
| **AAA** | http://aaa.bankid-sy.com | 3002 | إدارة Authentication/Authorization |
| **Backend** | http://localhost:8000 | 8000 | API Backend |

---

## 🛑 إيقاف الخدمات

### إيقاف Frontends:

```bash
cd frontend
./stop-all.sh
```

أو:

```bash
pm2 stop all
```

### إيقاف Backend:

```bash
cd backend
./stop.sh
```

---

## 📝 ملاحظات مهمة

1. **كل واجهة منفصلة تماماً:**
   - Dashboard لا يحتوي على CRM أو AAA
   - CRM واجهة إدارة منفصلة
   - AAA واجهة إدارة منفصلة

2. **جميع الواجهات تتصل بنفس Backend:**
   - Backend على port 8000
   - جميع الواجهات تستخدم `/api/` للوصول إلى Backend

3. **الملفات المهمة:**
   - `nginx-dashboard.conf` - إعدادات Dashboard
   - `nginx-crm.conf` - إعدادات CRM
   - `nginx-aaa.conf` - إعدادات AAA
   - `setup-all-services.sh` - سكربت الإعداد

---

## 🐛 استكشاف الأخطاء السريع

### مشكلة: 502 Bad Gateway

```bash
# تأكد أن Frontend يعمل
curl http://localhost:3000
curl http://localhost:3001
curl http://localhost:3002

# تأكد أن Backend يعمل
curl http://localhost:8000/health
```

### مشكلة: Port مستخدم

```bash
# إيقاف العملية على البورت
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
lsof -ti:3002 | xargs kill -9
```

### مشكلة: NGINX لا يعمل

```bash
# إعادة تحميل NGINX
sudo systemctl reload nginx

# فحص الأخطاء
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

---

**🎉 النظام جاهز!**

