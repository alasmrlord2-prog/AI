# 🔧 حل مشاكل Docker - دليل شامل

## 📋 المشاكل التي تم حلها

### 1. ❌ `KeyError: 'ContainerConfig'`

**السبب:** Container تالف أو غير متوافق مع Docker Compose.

**الحل:**
```bash
# استخدم السكربت الشامل
./fix-docker-issues.sh

# أو يدوياً
cd backend
docker-compose down --remove-orphans
docker rm -f ai-agent-postgres
docker system prune -f
./start-fixed.sh
```

---

### 2. ❌ `address already in use` (Port 8000 أو 3000)

**السبب:** المنفذ مستخدم من قبل container أو process آخر.

**الحل:**
```bash
# استخدم السكربتات المحسّنة
cd backend
./stop-fixed.sh
./start-fixed.sh

cd ../frontend
./stop-fixed.sh 3000
./start-fixed.sh 3000
```

---

### 3. ❌ `Cannot restart container` - Port already in use

**السبب:** Container موجود لكن الـ port مستخدم.

**الحل:**
```bash
# إزالة Container القديم
docker rm -f ai-agent-backend-prod ai-agent-frontend-prod

# قتل العملية
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# إعادة التشغيل
cd backend && ./restart-fixed.sh
cd ../frontend && ./restart-fixed.sh
```

---

## 🚀 الحل السريع (3 خطوات)

### الخطوة 1: تنظيف شامل

```bash
./fix-docker-issues.sh
```

هذا السكربت سيقوم بـ:
- إيقاف جميع containers
- قتل العمليات على المنافذ
- تنظيف Docker
- (اختياري) إزالة volumes
- (اختياري) إعادة بناء containers

---

### الخطوة 2: تشغيل Backend

```bash
cd backend
./start-fixed.sh
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

## 📝 السكربتات الجديدة

### Backend Scripts:

| السكربت | الوظيفة |
|---------|---------|
| `start-fixed.sh` | تشغيل مع معالجة الأخطاء |
| `stop-fixed.sh` | إيقاف شامل |
| `restart-fixed.sh` | إعادة تشغيل محسّنة |

### Frontend Scripts:

| السكربت | الوظيفة |
|---------|---------|
| `start-fixed.sh [port]` | تشغيل على port محدد |
| `stop-fixed.sh [port]` | إيقاف port محدد |
| `restart-fixed.sh [port]` | إعادة تشغيل port محدد |

### Utility Scripts:

| السكربت | الوظيفة |
|---------|---------|
| `fix-docker-issues.sh` | تنظيف شامل وإصلاح |

---

## 🔍 التحقق من الحالة

### التحقق من Docker:

```bash
# جميع containers
docker ps -a

# Services محددة
cd backend && docker-compose ps
cd ../frontend && docker-compose ps

# Logs
docker-compose logs -f
```

### التحقق من المنافذ:

```bash
# ما يستخدم port 8000
lsof -i :8000

# ما يستخدم port 3000
lsof -i :3000

# جميع المنافذ
netstat -tulpn | grep LISTEN
```

---

## 🛠️ حلول إضافية

### إذا استمرت المشاكل:

#### 1. إعادة تشغيل Docker:

```bash
sudo systemctl restart docker
```

#### 2. تنظيف شامل (احذر: سيحذف كل شيء):

```bash
docker-compose down -v
docker system prune -a --volumes
docker-compose build --no-cache
docker-compose up -d
```

#### 3. إزالة containers يدوياً:

```bash
# إزالة جميع containers
docker rm -f $(docker ps -aq)

# إزالة containers محددة
docker rm -f ai-agent-backend ai-agent-backend-prod
docker rm -f ai-agent-frontend ai-agent-frontend-prod
docker rm -f ai-agent-postgres
```

---

## 📚 الملفات المرجعية

- **TROUBLESHOOTING.md** - دليل شامل لحل المشاكل
- **COMPLETE_SETUP_GUIDE.md** - دليل الإعداد الكامل
- **QUICK_START.md** - البدء السريع

---

## ✅ Checklist

بعد تطبيق الحلول:

- [ ] Docker يعمل: `sudo systemctl status docker`
- [ ] Ports متاحة: `lsof -i :8000` و `lsof -i :3000`
- [ ] Backend يعمل: `curl http://localhost:8000/health`
- [ ] Frontends تعمل: `curl http://localhost:3000`
- [ ] لا توجد أخطاء في logs: `docker-compose logs`

---

## 🆘 إذا لم تحل المشكلة

1. **جمع المعلومات:**
```bash
docker info > docker-info.txt
docker-compose logs > logs.txt
docker ps -a > containers.txt
```

2. **إعادة البناء من الصفر:**
```bash
./fix-docker-issues.sh
# اختر "y" لجميع الخيارات
```

3. **التحقق من النظام:**
```bash
# Docker version
docker --version
docker-compose --version

# System resources
df -h
free -h
```

---

**آخر تحديث:** 2025-01-XX

