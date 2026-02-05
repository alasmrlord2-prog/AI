# 🚀 دليل الإعداد الكامل - ثلاث خدمات منفصلة

## 📋 نظرة عامة

هذا الدليل يشرح كيفية إعداد وتشغيل ثلاث خدمات منفصلة:
1. **AI-Agent** - على `ai-agent.bankid-sy.com` (port 3000)
2. **CRM** - على `crm.bankid-sy.com` (port 3001)
3. **AAA** - على `aaa.bankid-sy.com` (port 3002)

جميع الخدمات تستخدم نفس Backend على port 8000.

---

## 📁 البنية

```
ai-agent/
├── backend/              # FastAPI Backend (port 8000)
├── frontend/             # Next.js Frontend (يمكن تشغيله على 3000/3001/3002)
├── nginx-ai-agent-complete.conf
├── nginx-aaa-complete.conf
└── nginx-crm-complete.conf
```

---

## 🔧 خطوات الإعداد

### 1️⃣ إعداد NGINX

#### نسخ ملفات التكوين إلى NGINX:

```bash
# نسخ ملفات التكوين
sudo cp nginx-ai-agent-complete.conf /etc/nginx/sites-available/ai-agent.bankid-sy.com
sudo cp nginx-aaa-complete.conf /etc/nginx/sites-available/aaa.bankid-sy.com
sudo cp nginx-crm-complete.conf /etc/nginx/sites-available/crm.bankid-sy.com

# تفعيل المواقع
sudo ln -sf /etc/nginx/sites-available/ai-agent.bankid-sy.com /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/aaa.bankid-sy.com /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/crm.bankid-sy.com /etc/nginx/sites-enabled/

# اختبار التكوين
sudo nginx -t

# إعادة تحميل NGINX
sudo systemctl reload nginx
```

---

### 2️⃣ تشغيل Backend

```bash
cd backend
./start.sh

# أو يدوياً:
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**التحقق:**
```bash
curl http://localhost:8000/health
```

---

### 3️⃣ تشغيل Frontends

#### الطريقة الأولى: تشغيل كل frontend منفصل

```bash
# Terminal 1 - AI-Agent (port 3000)
cd frontend
./start-ai-agent.sh

# Terminal 2 - CRM (port 3001)
cd frontend
./start-crm.sh

# Terminal 3 - AAA (port 3002)
cd frontend
./start-aaa.sh
```

#### الطريقة الثانية: تشغيل كل شيء مرة واحدة

```bash
cd frontend
./start-all.sh
```

**لإيقاف كل شيء:**
```bash
cd frontend
./stop-all.sh
```

---

### 4️⃣ التحقق من الخدمات

#### التحقق من Frontends:

```bash
# AI-Agent
curl http://localhost:3000/health

# CRM
curl http://localhost:3001/health

# AAA
curl http://localhost:3002/health
```

#### التحقق من NGINX:

```bash
# AI-Agent
curl http://ai-agent.bankid-sy.com/health

# CRM
curl http://crm.bankid-sy.com/health

# AAA
curl http://aaa.bankid-sy.com/health
```

---

## 🎯 URLs النهائية

| الخدمة | URL | Frontend Port | Backend Port |
|--------|-----|---------------|--------------|
| **AI-Agent** | http://ai-agent.bankid-sy.com | 3000 | 8000 |
| **CRM** | http://crm.bankid-sy.com | 3001 | 8000 |
| **AAA** | http://aaa.bankid-sy.com | 3002 | 8000 |

---

## 🔍 Troubleshooting

### مشكلة: Frontend لا يعمل على port معين

```bash
# تحقق من أن الـ port غير مستخدم
lsof -i :3000
lsof -i :3001
lsof -i :3002

# قتل أي عملية تستخدم الـ port
kill -9 $(lsof -ti:3000)
```

### مشكلة: NGINX لا يعمل

```bash
# تحقق من logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# اختبار التكوين
sudo nginx -t

# إعادة تشغيل NGINX
sudo systemctl restart nginx
```

### مشكلة: Backend لا يستجيب

```bash
# تحقق من Backend logs
cd backend
tail -f backend.log

# أو إذا كان في Docker
docker-compose logs -f backend
```

### مشكلة: CORS Errors

تأكد من أن `CORS_ORIGINS` في `backend/app/core/config.py` يحتوي على:
```python
CORS_ORIGINS = ["*"]  # أو قائمة محددة بالـ domains
```

---

## 📝 استخدام PM2 لإدارة الخدمات (اختياري)

### تثبيت PM2:

```bash
npm install -g pm2
```

### إنشاء ملفات PM2:

#### `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [
    {
      name: 'ai-agent-frontend',
      script: 'npm',
      args: 'run dev -- -p 3000',
      cwd: '/home/ai/ai-agent/frontend',
      env: {
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      }
    },
    {
      name: 'crm-frontend',
      script: 'npm',
      args: 'run dev -- -p 3001',
      cwd: '/home/ai/ai-agent/frontend',
      env: {
        PORT: 3001,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      }
    },
    {
      name: 'aaa-frontend',
      script: 'npm',
      args: 'run dev -- -p 3002',
      cwd: '/home/ai/ai-agent/frontend',
      env: {
        PORT: 3002,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      }
    }
  ]
};
```

### استخدام PM2:

```bash
# تشغيل كل شيء
pm2 start ecosystem.config.js

# عرض الحالة
pm2 status

# عرض logs
pm2 logs

# إيقاف كل شيء
pm2 stop all

# إعادة تشغيل
pm2 restart all

# حذف كل شيء
pm2 delete all
```

---

## 🐳 استخدام Docker (اختياري)

إذا كنت تريد استخدام Docker، يمكنك تعديل `docker-compose.yml` لإضافة services منفصلة:

```yaml
services:
  backend:
    # ... existing config

  frontend-ai-agent:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      - NEXT_PUBLIC_API_URL=http://backend:8000

  frontend-crm:
    build: ./frontend
    ports:
      - "3001:3001"
    environment:
      - PORT=3001
      - NEXT_PUBLIC_API_URL=http://backend:8000

  frontend-aaa:
    build: ./frontend
    ports:
      - "3002:3002"
    environment:
      - PORT=3002
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

---

## ✅ Checklist النهائي

- [ ] Backend يعمل على port 8000
- [ ] AI-Agent frontend يعمل على port 3000
- [ ] CRM frontend يعمل على port 3001
- [ ] AAA frontend يعمل على port 3002
- [ ] NGINX configurations منسوخة ومفعّلة
- [ ] NGINX تم إعادة تحميله
- [ ] جميع الـ health checks تعمل
- [ ] يمكن الوصول للخدمات عبر الـ domains

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. تحقق من logs (Backend, Frontend, NGINX)
2. تأكد من أن جميع الـ ports مفتوحة
3. تحقق من firewall settings
4. تأكد من أن الـ DNS records صحيحة

---

**آخر تحديث:** 2025-01-XX

