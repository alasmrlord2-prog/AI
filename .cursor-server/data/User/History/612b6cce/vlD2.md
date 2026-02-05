# 🔧 حل سريع لمشكلة Backend

## المشكلة
Backend container يعمل لكن لا يستجيب على port 8000 (Empty reply from server)

## الحلول السريعة

### 1. فحص الـ Logs
```bash
cd /home/ai/ai-agent
./debug-backend.sh
```

أو مباشرة:
```bash
sudo docker logs ai-agent-backend --tail=100
```

### 2. إعادة تشغيل Backend
```bash
cd /home/ai/ai-agent/backend
./restart.sh
```

### 3. إعادة بناء Container
```bash
cd /home/ai/ai-agent
docker-compose -f docker-compose.yml build --no-cache backend
docker-compose -f docker-compose.yml up -d backend
```

### 4. فحص Database Connection
```bash
sudo docker logs ai-agent-postgres --tail=20
sudo docker exec ai-agent-backend python -c "from app.core.database import engine; print('DB OK')"
```

### 5. فحص Imports
```bash
sudo docker exec ai-agent-backend python -c "from app.main import app; print('OK')"
```

### 6. تشغيل Backend يدوياً داخل Container
```bash
sudo docker exec -it ai-agent-backend bash
# ثم داخل الـ container:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## الأسباب المحتملة

1. **خطأ في Import** - أحد الـ routers لا يمكن استيراده
2. **Database Connection Failed** - لا يمكن الاتصال بـ PostgreSQL
3. **Missing Dependencies** - مكتبة مفقودة في requirements.txt
4. **Port Binding Issue** - مشكلة في ربط المنفذ
5. **App Crash on Startup** - التطبيق يتعطل عند البدء

## خطوات التشخيص

1. ✅ Container يعمل: `sudo docker ps | grep backend`
2. ✅ Port يستمع: `sudo netstat -tlnp | grep 8000`
3. ❌ App لا يستجيب: `curl http://localhost:8000/health` → Empty reply
4. 🔍 فحص الـ logs للعثور على الخطأ

## الحل النهائي

إذا لم يعمل أي شيء أعلاه، جرب:

```bash
cd /home/ai/ai-agent

# إيقاف كل شيء
cd backend && ./stop.sh

# إعادة بناء من الصفر
docker-compose -f docker-compose.yml build --no-cache

# تشغيل
cd backend && ./start.sh

# انتظر 30 ثانية ثم اختبر
sleep 30
curl http://localhost:8000/health
```

