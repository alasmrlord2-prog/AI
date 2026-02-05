# سكربتات التشغيل - AI Agent

## 📋 السكربتات المتوفرة

تم إنشاء 3 سكربتات فقط لتشغيل المشروع:

### 1. `start_services.sh` - تشغيل الخدمات الأساسية
يبدأ جميع الخدمات الأساسية:
- **nginx** - خادم الويب العكسي (Reverse Proxy)
- **postgres** - قاعدة البيانات
- **ollama** - خدمة AI
- **prometheus** - مراقبة الأداء
- **grafana** - لوحة المعلومات
- **loki** - تجميع السجلات
- **promtail** - جمع السجلات

### 2. `start_backend.sh` - تشغيل Backend
يبدأ خدمة Backend (FastAPI)

### 3. `start_frontend.sh` - تشغيل Frontend
يبدأ خدمة Frontend (Next.js)

## 🚀 طريقة الاستخدام

### التشغيل الكامل للمشروع:

```bash
cd /home/ai/ai-agent

# 1. تشغيل الخدمات الأساسية أولاً
./start_services.sh

# 2. تشغيل Backend
./start_backend.sh

# 3. تشغيل Frontend
./start_frontend.sh
```

### أو تشغيل كل شيء دفعة واحدة:

```bash
cd /home/ai/ai-agent
./start_services.sh && ./start_backend.sh && ./start_frontend.sh
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
docker logs -f ai-agent-nginx
docker logs -f ai-agent-backend-prod
docker logs -f ai-agent-frontend-prod
```

### إيقاف الخدمات:
```bash
docker-compose -f docker-compose.prod.yml down
```

### إعادة تشغيل خدمة:
```bash
docker-compose -f docker-compose.prod.yml restart nginx
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart frontend
```

## ⚙️ الإعدادات

- **الدومين**: ai-agent.bankid-sy.com
- **IP**: 3.76.209.35
- **Docker Compose File**: docker-compose.prod.yml

## 🔧 استكشاف الأخطاء

### إذا فشل تشغيل nginx:
```bash
# تحقق من شهادات SSL
ls -la nginx/ssl/

# إذا لم تكن موجودة، قم بإنشائها:
cd nginx && ./generate-ssl.sh && cd ..
```

### إذا فشل تشغيل خدمة:
```bash
# تحقق من السجلات
docker-compose -f docker-compose.prod.yml logs [service_name]

# تحقق من حالة الحاوية
docker ps -a | grep ai-agent
```

