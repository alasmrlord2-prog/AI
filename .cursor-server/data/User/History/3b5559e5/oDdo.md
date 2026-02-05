# إصلاحات المشاكل - Dashboard Fixes

## المشاكل التي تم إصلاحها

### 1. إعدادات Docker Compose ✅
- **المشكلة**: Frontend containers كانت تستخدم `localhost:8000` فقط، ولم يكن لديها `BACKEND_URL` للـ server-side
- **الحل**: 
  - إضافة `BACKEND_URL=http://backend:8000` لجميع frontend containers (dashboard, CRM, AAA)
  - إضافة health checks لجميع containers
  - تحديث `depends_on` لاستخدام `service_healthy` condition
  - تغيير CORS_ORIGINS في backend إلى `["*"]` للسماح بجميع المصادر

### 2. تحسين getApiUrl() في lib/api.ts ✅
- **المشكلة**: الدالة لم تكن تتعامل بشكل صحيح مع IP addresses والـ Docker network
- **الحل**:
  - إضافة دعم للـ IP addresses (مثل 3.76.209.35)
  - تحسين المنطق للتعامل مع حالات مختلفة من الوصول (localhost, IP, domain)
  - Server-side يستخدم `BACKEND_URL` (Docker service name)
  - Client-side يستخدم `NEXT_PUBLIC_BACKEND_URL` أو يحسب من hostname

### 3. إصلاح Next.js Rewrites ✅
- **المشكلة**: Rewrites كانت تستخدم `NEXT_PUBLIC_BACKEND_URL` للـ server-side أيضاً
- **الحل**: تغيير rewrites لاستخدام `BACKEND_URL` (بدون NEXT_PUBLIC_) للـ server-side

### 4. إصلاح Health Checks ✅
- **المشكلة**: Frontend containers لم يكن لديها health checks صحيحة
- **الحل**:
  - إضافة health checks لجميع frontend containers (dashboard, CRM, AAA)
  - استخدام port الصحيح لكل container (3000, 3001, 3002)
  - إضافة wget إلى frontend Dockerfile
  - تحديث backend health check لاستخدام curl

### 5. إصلاح CORS ✅
- **المشكلة**: CORS قد يمنع الطلبات من مصادر مختلفة
- **الحل**: تغيير `CORS_ORIGINS` إلى `["*"]` للسماح بجميع المصادر في development

## الملفات المعدلة

1. `/home/ai/ai-agent/docker-compose.yml`
   - إضافة `BACKEND_URL` لجميع frontend containers
   - إضافة health checks
   - تحديث `depends_on` conditions
   - تغيير CORS_ORIGINS

2. `/home/ai/ai-agent/frontend/lib/api.ts`
   - تحسين `getApiUrl()` لدعم IP addresses
   - تحسين المنطق للـ Docker network

3. `/home/ai/ai-agent/frontend/next.config.ts`
   - إصلاح rewrites لاستخدام `BACKEND_URL` الصحيح

4. `/home/ai/ai-agent/frontend/Dockerfile`
   - إضافة wget للـ health checks

## الخطوات التالية

لتفعيل الإصلاحات، قم بتنفيذ:

```bash
cd /home/ai/ai-agent

# إعادة بناء frontend containers (لإضافة wget)
docker-compose build frontend-dashboard frontend-crm frontend-aaa

# إعادة تشغيل جميع الخدمات
docker-compose down
docker-compose up -d

# التحقق من حالة الخدمات
docker-compose ps

# مراقبة الـ logs
docker-compose logs -f frontend-dashboard
docker-compose logs -f backend
```

## التحقق من الإصلاحات

1. **التحقق من Health Checks**:
   ```bash
   docker ps  # يجب أن تكون جميع containers healthy
   ```

2. **اختبار الاتصال**:
   - افتح Dashboard على `http://localhost:3000`
   - افتح Developer Console (F12)
   - تحقق من عدم وجود أخطاء "Failed to fetch"
   - جرب إرسال رسالة للـ Agent

3. **اختبار API مباشرة**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/monitor
   ```

## ملاحظات مهمة

- **CORS**: تم تعيين CORS_ORIGINS إلى `["*"]` للـ development. في production، يجب تحديد المصادر المسموحة بشكل صريح
- **Health Checks**: قد تستغرق containers بعض الوقت للوصول إلى حالة healthy (خاصة frontend containers التي تحتاج 60 ثانية start_period)
- **Network**: جميع containers على نفس Docker network (`ai-agent-network`) ويمكنها التواصل باستخدام service names

