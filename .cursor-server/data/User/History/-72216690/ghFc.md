# 🔧 حل مشكلة 502 Bad Gateway

## 📋 المشكلة

عند محاولة الوصول إلى `/api/chat` أو أي endpoint آخر، تحصل على:
```
HTTP 502: خطأ في السيرفر (Endpoint: /api/chat)
```

## 🔍 السبب

502 Bad Gateway يعني أن:
- ✅ Frontend يعمل (لأن الخطأ يظهر في المتصفح)
- ❌ Backend لا يستجيب أو لا يعمل
- ❌ NGINX لا يستطيع الوصول إلى Backend

---

## 🚀 الحل السريع

### الخطوة 1: التحقق من حالة Backend

```bash
cd backend
./check-backend.sh
```

هذا السكربت سيعرض:
- حالة Docker containers
- إذا كان Backend يستجيب
- Logs الأخيرة

---

### الخطوة 2: إصلاح Backend

#### إذا كان Backend container لا يعمل:

```bash
cd backend
./start-fixed.sh
```

#### إذا كان Backend container يعمل لكن لا يستجيب:

```bash
cd backend
./restart-fixed.sh
```

#### إذا استمرت المشكلة:

```bash
cd backend

# إيقاف وإزالة
docker-compose down

# إعادة البناء
docker-compose build --no-cache backend

# البدء
docker-compose up -d backend postgres

# التحقق
sleep 5
curl http://localhost:8000/health
```

---

### الخطوة 3: التحقق من NGINX

```bash
# اختبار التكوين
sudo nginx -t

# عرض logs
sudo tail -f /var/log/nginx/error.log

# إعادة تحميل
sudo systemctl reload nginx
```

---

## 🔍 التشخيص التفصيلي

### 1. التحقق من Backend محلياً

```bash
# التحقق من health endpoint
curl http://localhost:8000/health

# التحقق من API docs
curl http://localhost:8000/docs

# التحقق من chat endpoint
curl http://localhost:8000/api/chat
```

**إذا لم يستجب:**
- Backend container لا يعمل
- Backend container يعمل لكن التطبيق فشل في البدء
- Port 8000 مستخدم من قبل process آخر

---

### 2. التحقق من Docker Containers

```bash
# جميع containers
docker ps -a

# Backend container فقط
docker ps -a | grep ai-agent-backend

# Logs
docker logs ai-agent-backend --tail=50
```

---

### 3. التحقق من NGINX Configuration

تأكد من أن NGINX يشير إلى Backend الصحيح:

```bash
# عرض تكوين ai-agent
sudo cat /etc/nginx/sites-available/ai-agent.bankid-sy.com | grep -A 5 "location /api"
```

يجب أن يكون:
```nginx
location /api {
    proxy_pass http://ai_backend;  # أو http://127.0.0.1:8000
    ...
}
```

---

### 4. التحقق من CORS

تأكد من أن Backend يدعم CORS:

```bash
# في backend/app/core/config.py
CORS_ORIGINS = ["*"]  # أو قائمة محددة بالـ domains
```

---

## 🛠️ حلول إضافية

### الحل 1: إعادة تشغيل Backend

```bash
cd backend
./restart-fixed.sh
```

### الحل 2: إعادة بناء Backend

```bash
cd backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

### الحل 3: تشغيل Backend بدون Docker

إذا كان Docker يسبب مشاكل، يمكن تشغيل Backend مباشرة:

```bash
cd backend

# تثبيت dependencies
pip install -r requirements.txt

# تشغيل
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**ملاحظة:** تأكد من أن PostgreSQL يعمل إذا كنت تحتاجه.

---

### الحل 4: تحديث NGINX Configuration

إذا كان NGINX لا يشير إلى Backend الصحيح:

```bash
# تحرير التكوين
sudo nano /etc/nginx/sites-available/ai-agent.bankid-sy.com

# تأكد من:
upstream ai_backend {
    server 127.0.0.1:8000;  # أو localhost:8000
    keepalive 32;
}

# إعادة تحميل
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📝 Checklist

- [ ] Backend container يعمل: `docker ps | grep ai-agent-backend`
- [ ] Backend يستجيب محلياً: `curl http://localhost:8000/health`
- [ ] NGINX configuration صحيح: `sudo nginx -t`
- [ ] NGINX يشير إلى Backend الصحيح
- [ ] CORS settings صحيحة في Backend
- [ ] لا توجد أخطاء في logs: `docker logs ai-agent-backend`

---

## 🆘 إذا استمرت المشكلة

### جمع المعلومات:

```bash
# Backend logs
docker logs ai-agent-backend > backend-logs.txt

# NGINX logs
sudo tail -100 /var/log/nginx/error.log > nginx-errors.txt

# System info
docker ps -a > containers.txt
lsof -i :8000 > port-8000.txt
```

### إعادة البناء من الصفر:

```bash
cd backend

# إيقاف كل شيء
docker-compose down -v

# تنظيف
docker system prune -f

# إعادة البناء
docker-compose build --no-cache

# البدء
docker-compose up -d

# التحقق
sleep 10
curl http://localhost:8000/health
```

---

## ✅ التحقق النهائي

بعد تطبيق الحلول:

```bash
# 1. Backend يستجيب محلياً
curl http://localhost:8000/health

# 2. Backend يستجيب عبر NGINX
curl http://ai-agent.bankid-sy.com/api/health

# 3. Frontend يمكنه الوصول
# افتح المتصفح وجرب /api/chat
```

---

**آخر تحديث:** 2025-01-XX

