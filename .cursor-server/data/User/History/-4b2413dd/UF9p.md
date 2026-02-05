# إصلاح سريع للمشاكل

## المشاكل الحالية والحلول

### 1. ✅ تم إصلاح: TypeScript Error في Frontend
- **المشكلة**: `Type 'Dispatch<SetStateAction<"en" | "ar">>' is not assignable`
- **الحل**: تم إضافة wrapper function في `app/page.tsx`

### 2. ✅ تم إصلاح: Backend لا يستطيع استيراد main
- **المشكلة**: `Could not import module "main"`
- **الحل**: تم تعديل Dockerfile لاستخدام `app.main:app` ونسخ جميع الملفات

### 3. ⚠️ مشكلة Docker Compose مع الحاويات القديمة
- **المشكلة**: `KeyError: 'ContainerConfig'`
- **الحل**: إزالة الحاويات القديمة وإعادة البناء

## خطوات الإصلاح السريع

### الطريقة 1: استخدام سكربت الإصلاح

```bash
cd /home/ai/ai-agent
./fix_issues.sh
```

### الطريقة 2: يدوياً

```bash
cd /home/ai/ai-agent

# 1. إيقاف وإزالة جميع الحاويات
docker-compose -f docker-compose.prod.yml down --remove-orphans

# 2. إزالة الحاويات القديمة يدوياً
docker ps -a | grep -E "agent-core|alertmanager|3d28ce0e23e1" | awk '{print $1}' | xargs docker rm -f

# 3. إعادة بناء الصور
docker-compose -f docker-compose.prod.yml build --no-cache backend frontend

# 4. تشغيل الخدمات
./start_backend.sh
sleep 10
./start_frontend.sh
sleep 10
./start_nginx.sh
```

## التحقق من الإصلاح

### Frontend:
```bash
# يجب أن يبني بدون أخطاء TypeScript
docker-compose -f docker-compose.prod.yml build frontend
```

### Backend:
```bash
# يجب أن يبدأ بدون أخطاء
docker logs ai-agent-backend-prod
# يجب أن ترى: "Application startup complete" بدلاً من "Could not import module"
```

## ملاحظات

1. **Backend Dockerfile**: تم تعديله لنسخ جميع الملفات واستخدام `app.main:app`
2. **Frontend TypeScript**: تم إصلاح مشكلة `setLocale` type
3. **Docker Compose**: قد تحتاج لإزالة الحاويات القديمة يدوياً

## إذا استمرت المشاكل

```bash
# تنظيف شامل
docker system prune -a --volumes

# إعادة بناء كامل
cd /home/ai/ai-agent
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

