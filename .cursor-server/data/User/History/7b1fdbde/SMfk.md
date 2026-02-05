# سكربتات التشغيل - AI Agent

## 📋 السكربتات المتوفرة

تم إنشاء 6 سكربتات فقط لتشغيل المشروع:

### 🔵 Backend (3 سكربتات)

1. **`start_backend.sh`** - تشغيل Backend
   - يبدأ: postgres, ollama, backend
   - يضمن تشغيل جميع الخدمات المطلوبة للـ backend

2. **`restart_backend.sh`** - إعادة تشغيل Backend
   - يعيد تشغيل: postgres, ollama, backend

3. **`stop_backend.sh`** - إيقاف Backend
   - يوقف: backend, ollama, postgres

### 🟢 Frontend (3 سكربتات)

1. **`start_frontend.sh`** - تشغيل Frontend
   - يبدأ: postgres, ollama, backend, frontend
   - يضمن تشغيل جميع الخدمات المطلوبة للـ frontend

2. **`restart_frontend.sh`** - إعادة تشغيل Frontend
   - يعيد تشغيل: postgres, ollama, backend, frontend

3. **`stop_frontend.sh`** - إيقاف Frontend
   - يوقف: frontend, backend, ollama, postgres

## 🚀 طريقة الاستخدام

### تشغيل Backend فقط:

```bash
cd /home/ai/ai-agent

# تشغيل
./start_backend.sh

# إعادة تشغيل
./restart_backend.sh

# إيقاف
./stop_backend.sh
```

### تشغيل Frontend (يشمل Backend):

```bash
cd /home/ai/ai-agent

# تشغيل (سيبدأ backend تلقائياً)
./start_frontend.sh

# إعادة تشغيل
./restart_frontend.sh

# إيقاف
./stop_frontend.sh
```

## 🌐 الوصول للموقع

بعد التشغيل، يمكنك الوصول للموقع على:
- **الموقع الرئيسي**: https://ai-agent.bankid-sy.com
- **API**: https://ai-agent.bankid-sy.com/api
- **API Docs**: https://ai-agent.bankid-sy.com/api/docs
- **Health Check**: https://ai-agent.bankid-sy.com/health

## 📝 الأوامر المفيدة

### عرض حالة الخدمات:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### عرض السجلات:
```bash
# جميع السجلات
docker-compose -f docker-compose.prod.yml logs -f

# سجلات خدمة محددة
docker logs -f ai-agent-backend-prod
docker logs -f ai-agent-frontend-prod
docker logs -f ai-agent-nginx
```

### إيقاف جميع الخدمات:
```bash
docker-compose -f docker-compose.prod.yml down
```

### إعادة تشغيل خدمة محددة:
```bash
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart frontend
```

## ⚙️ الإعدادات

- **الدومين**: ai-agent.bankid-sy.com
- **IP**: 3.76.209.35
- **Docker Compose File**: docker-compose.prod.yml

## 📊 الخدمات التي يتم تشغيلها تلقائياً

### عند تشغيل Backend:
- ✅ **postgres** - قاعدة البيانات
- ✅ **ollama** - خدمة AI
- ✅ **backend** - FastAPI Backend

### عند تشغيل Frontend:
- ✅ **postgres** - قاعدة البيانات
- ✅ **ollama** - خدمة AI
- ✅ **backend** - FastAPI Backend
- ✅ **frontend** - Next.js Frontend

## 🔧 استكشاف الأخطاء

### إذا فشل تشغيل Backend:
```bash
# تحقق من السجلات
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs postgres
docker-compose -f docker-compose.prod.yml logs ollama

# تحقق من حالة الحاويات
docker ps -a | grep ai-agent
```

### إذا فشل تشغيل Frontend:
```bash
# تحقق من السجلات
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs backend

# تأكد من أن backend يعمل
docker ps | grep backend
```

### إذا كانت الحاويات لا تبدأ:
```bash
# إعادة بناء الصور
docker-compose -f docker-compose.prod.yml build

# إزالة الحاويات القديمة وإعادة التشغيل
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 💡 ملاحظات مهمة

1. **Frontend يعتمد على Backend**: عند تشغيل `start_frontend.sh`، سيتم تشغيل backend تلقائياً
2. **الترتيب مهم**: الخدمات تبدأ بالترتيب الصحيح (postgres → ollama → backend → frontend)
3. **nginx منفصل**: إذا كنت تحتاج nginx، يجب تشغيله بشكل منفصل أو إضافته إلى docker-compose
