# 🔧 دليل حل المشاكل الشائعة

## 📋 المشاكل الشائعة وحلولها

---

## ❌ مشكلة: `KeyError: 'ContainerConfig'`

### السبب:
هذه المشكلة تحدث عندما يكون Docker container تالف أو غير متوافق.

### الحل:

```bash
# 1. إيقاف وإزالة جميع containers
cd backend
docker-compose down --remove-orphans
docker rm -f ai-agent-postgres ai-agent-backend 2>/dev/null || true

# 2. تنظيف Docker
docker system prune -f

# 3. إزالة volumes التالفة (احذر: سيحذف البيانات!)
docker-compose down -v

# 4. إعادة البناء
docker-compose build --no-cache

# 5. البدء من جديد
docker-compose up -d
```

**أو استخدم السكربت المحسّن:**
```bash
cd backend
./start-fixed.sh
```

---

## ❌ مشكلة: `address already in use` (Port 8000 أو 3000)

### السبب:
المنفذ مستخدم بالفعل من قبل container أو process آخر.

### الحل:

#### الطريقة 1: استخدام السكربتات المحسّنة

```bash
# Backend
cd backend
./stop-fixed.sh
./start-fixed.sh

# Frontend
cd frontend
./stop-fixed.sh 3000
./start-fixed.sh 3000
```

#### الطريقة 2: يدوياً

```bash
# 1. معرفة ما يستخدم الـ port
lsof -i :8000
lsof -i :3000

# 2. إيقاف containers
docker-compose down
docker stop ai-agent-backend ai-agent-frontend 2>/dev/null || true

# 3. قتل العملية إذا لزم الأمر
kill -9 <PID>

# 4. إعادة التشغيل
docker-compose up -d
```

#### الطريقة 3: تنظيف شامل

```bash
# إيقاف كل شيء
docker-compose down --remove-orphans

# قتل جميع العمليات على المنافذ
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:3002 | xargs kill -9 2>/dev/null || true

# إعادة التشغيل
docker-compose up -d
```

---

## ❌ مشكلة: `Cannot restart container` - Port already in use

### السبب:
Container موجود لكن الـ port مستخدم من قبل process آخر.

### الحل:

```bash
# 1. إزالة Container القديم
docker rm -f ai-agent-backend-prod
docker rm -f ai-agent-frontend-prod

# 2. قتل العملية على الـ port
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# 3. إعادة التشغيل
docker-compose restart
```

---

## ❌ مشكلة: Docker containers لا تبدأ

### الحل:

```bash
# 1. التحقق من حالة Docker
sudo systemctl status docker

# 2. إعادة تشغيل Docker
sudo systemctl restart docker

# 3. تنظيف Docker
docker system prune -f
docker volume prune -f

# 4. إعادة البناء
docker-compose build --no-cache
docker-compose up -d
```

---

## ❌ مشكلة: PostgreSQL لا يبدأ

### الحل:

```bash
# 1. إزالة container و volume
docker-compose down -v
docker volume rm ai-agent_postgres_data 2>/dev/null || true

# 2. إعادة البناء
docker-compose up -d postgres

# 3. التحقق من الحالة
docker-compose ps postgres
docker-compose logs postgres
```

---

## ❌ مشكلة: Backend لا يستجيب

### الحل:

```bash
# 1. التحقق من logs
docker-compose logs backend

# 2. التحقق من الحالة
docker-compose ps

# 3. إعادة التشغيل
docker-compose restart backend

# 4. إذا لم يعمل، إعادة البناء
docker-compose build backend
docker-compose up -d backend
```

---

## ❌ مشكلة: Frontend لا يستجيب

### الحل:

```bash
# 1. التحقق من logs
docker-compose logs frontend

# 2. التحقق من الحالة
docker-compose ps frontend

# 3. إعادة البناء
docker-compose build frontend
docker-compose up -d frontend

# 4. التحقق من Node modules
cd frontend
rm -rf node_modules .next
npm install
```

---

## ❌ مشكلة: CORS Errors

### الحل:

1. **تحديث `backend/app/core/config.py`:**
```python
CORS_ORIGINS = ["*"]  # أو قائمة محددة
```

2. **إعادة تشغيل Backend:**
```bash
cd backend
docker-compose restart backend
```

---

## ❌ مشكلة: NGINX لا يعمل

### الحل:

```bash
# 1. اختبار التكوين
sudo nginx -t

# 2. عرض الأخطاء
sudo tail -f /var/log/nginx/error.log

# 3. إعادة تحميل
sudo systemctl reload nginx

# 4. إعادة تشغيل
sudo systemctl restart nginx
```

---

## 🔍 أدوات التشخيص

### التحقق من حالة Docker:

```bash
# حالة جميع containers
docker ps -a

# حالة services محددة
docker-compose ps

# استخدام الموارد
docker stats

# Logs
docker-compose logs -f
```

### التحقق من المنافذ:

```bash
# ما يستخدم port 8000
lsof -i :8000

# ما يستخدم port 3000
lsof -i :3000

# جميع المنافذ المستخدمة
netstat -tulpn | grep LISTEN
```

### تنظيف Docker:

```bash
# تنظيف شامل (احذر!)
docker system prune -a --volumes

# تنظيف containers المتوقفة
docker container prune

# تنظيف images غير المستخدمة
docker image prune -a

# تنظيف volumes
docker volume prune
```

---

## 🛠️ سكربتات الإصلاح السريع

### تنظيف شامل وإعادة البناء:

```bash
#!/bin/bash
# cleanup-and-restart.sh

echo "🧹 Cleaning up..."

# Stop everything
docker-compose down --remove-orphans
docker stop $(docker ps -aq) 2>/dev/null || true

# Kill processes on ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:3002 | xargs kill -9 2>/dev/null || true

# Clean Docker
docker system prune -f
docker volume prune -f

# Remove containers
docker rm -f $(docker ps -aq) 2>/dev/null || true

echo "✅ Cleanup done!"
echo "🚀 Now run: docker-compose up -d"
```

---

## 📝 Checklist عند مواجهة مشاكل

- [ ] تحقق من حالة Docker: `sudo systemctl status docker`
- [ ] تحقق من المنافذ: `lsof -i :8000` و `lsof -i :3000`
- [ ] تحقق من logs: `docker-compose logs`
- [ ] جرب السكربتات المحسّنة: `./start-fixed.sh`
- [ ] نظف Docker: `docker system prune -f`
- [ ] أعد البناء: `docker-compose build --no-cache`
- [ ] تحقق من NGINX: `sudo nginx -t`

---

## 🆘 إذا لم تحل المشكلة

1. **جمع المعلومات:**
```bash
# Docker info
docker info
docker version

# Container logs
docker-compose logs > logs.txt

# System info
uname -a
docker-compose version
```

2. **إعادة البناء من الصفر:**
```bash
# احذر: سيحذف كل البيانات!
docker-compose down -v
docker system prune -a --volumes
docker-compose build --no-cache
docker-compose up -d
```

---

**آخر تحديث:** 2025-01-XX

