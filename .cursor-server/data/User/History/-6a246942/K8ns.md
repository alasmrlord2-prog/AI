# إصلاح سريع - Quick Fix

## المشكلة:
```
network ai-network declared as external, but could not be found
Connection refused on port 8000
```

## الحل:

### 1. إصلاح الـ Network:
تم تحديث `backend-compose.yml` لإنشاء الـ network تلقائياً بدلاً من external.

### 2. إصلاح Dockerfile:
تم تصحيح command من `app.main:app` إلى `main:app`.

### 3. تشغيل Backend:

```bash
cd /home/ai/ai-agent/backend

# الطريقة السريعة:
bash FIX_AND_START.sh

# أو يدوياً:
docker compose -f backend-compose.yml down
docker compose -f backend-compose.yml up -d --build

# تحقق من الحالة:
docker compose -f backend-compose.yml ps

# اختبر:
curl http://localhost:8000/api/settings

# شوف الـ logs:
docker compose -f backend-compose.yml logs -f
```

### 4. إذا استمرت المشكلة:

```bash
# تحقق من الـ container:
docker ps | grep ai-backend

# شوف الـ logs بالتفصيل:
docker compose -f backend-compose.yml logs

# تحقق من الـ port:
netstat -tlnp | grep 8000
# أو
ss -tlnp | grep 8000
```

### 5. إعادة بناء كاملة:

```bash
cd /home/ai/ai-agent/backend
docker compose -f backend-compose.yml down -v
docker compose -f backend-compose.yml build --no-cache
docker compose -f backend-compose.yml up -d
```

