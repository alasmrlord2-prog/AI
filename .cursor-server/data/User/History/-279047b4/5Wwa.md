# 🔧 Troubleshooting Guide

## المشاكل الحالية والحلول

### 1. ❌ CRM و Identity Endpoints تعطي 404

**السبب:**
- الـ routers غير مسجلة في الـ container بسبب فشل الاستيراد
- `pydantic[email]` غير مثبت في الـ container

**الحل:**
```bash
cd /home/ai/ai-agent
./fix-backend.sh
```

أو يدوياً:
```bash
docker compose build backend
docker compose restart backend
```

### 2. ❌ Access Endpoint يعطي 500 (Database Error)

**السبب:**
- مشكلة في الاتصال بقاعدة البيانات
- `password authentication failed for user "aiagent"`

**الحل:**
```bash
# إعادة تشغيل PostgreSQL
docker compose restart postgres

# أو إعادة تشغيل جميع الخدمات
./backend-restart.sh
```

### 3. ✅ السكربتات تعمل الآن

تم إصلاح `check-endpoints.sh` ليعمل بدون `jq`:
```bash
./check-endpoints.sh
```

## 📋 الخطوات الكاملة للإصلاح

### الخطوة 1: إعادة بناء Backend
```bash
cd /home/ai/ai-agent
docker compose build backend
```

### الخطوة 2: إعادة تشغيل Backend
```bash
docker compose restart backend
```

### الخطوة 3: التحقق من الـ Endpoints
```bash
./check-endpoints.sh
```

### الخطوة 4: إذا استمرت المشاكل
```bash
# إعادة تشغيل جميع الخدمات
./backend-restart.sh

# انتظر 30 ثانية
sleep 30

# تحقق مرة أخرى
./check-endpoints.sh
```

## 🔍 التحقق من الحالة

### Backend Health
```bash
curl http://localhost:8000/health
```

### CRM Endpoint
```bash
curl http://localhost:8000/api/crm/tenants
# يجب أن يعطي 200 أو 401 (ليس 404)
```

### Identity Endpoint
```bash
curl http://localhost:8000/api/identity/users
# يجب أن يعطي 200 أو 401 (ليس 404)
```

### Access Endpoint
```bash
curl http://localhost:8000/api/access/roles
# يجب أن يعطي 200 أو 401 (ليس 500)
```

## 📝 ملاحظات

1. **404 يعني الـ router غير مسجل** - يحتاج rebuild
2. **500 يعني مشكلة في قاعدة البيانات** - يحتاج restart
3. **401/403 يعني الـ endpoint موجود لكن يحتاج authentication** - هذا طبيعي ✅

## 🎯 الحل السريع

```bash
cd /home/ai/ai-agent
./fix-backend.sh
sleep 30
./check-endpoints.sh
```

---

**آخر تحديث:** $(date)

