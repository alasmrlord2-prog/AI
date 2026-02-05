# استكشاف الأخطاء - AI Agent

## المشاكل الشائعة والحلول

### 1. ❌ مشكلة package-lock.json غير متزامن

**الخطأ:**
```
npm error `npm ci` can only install packages when your package.json and package-lock.json are in sync.
```

**الحل:**
تم تعديل Dockerfile لاستخدام `npm install` بدلاً من `npm ci`. الآن يجب أن يعمل البناء.

```bash
cd /home/ai/ai-agent
./start_frontend.sh
```

### 2. ❌ Backend يعيد التشغيل باستمرار (Restarting)

**الخطأ:**
```
ai-agent-backend-prod   Restarting (1) 12 seconds ago
```

**الحل:**
تحقق من سجلات backend:
```bash
docker logs ai-agent-backend-prod
```

الأسباب المحتملة:
- قاعدة البيانات غير متصلة
- متغيرات البيئة مفقودة
- خطأ في الكود

**الحل السريع:**
```bash
# تحقق من ملف .env
cat /home/ai/ai-agent/.env

# إعادة تشغيل backend
cd /home/ai/ai-agent
./restart_backend.sh

# أو إعادة بناء
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### 3. ❌ Nginx غير مشغّل

**الخطأ:**
```
Error response from daemon: No such container: ai-agent-nginx
```

**الحل:**
```bash
cd /home/ai/ai-agent
./start_nginx.sh
```

أو:
```bash
docker-compose -f docker-compose.prod.yml up -d nginx
```

### 4. ❌ Cloudflare Error 522

**السبب:** nginx غير مشغّل أو لا يستجيب

**الحل:**
1. تشغيل nginx:
```bash
./start_nginx.sh
```

2. التحقق من المنافذ:
```bash
sudo netstat -tlnp | grep -E ':(80|443)'
```

3. التحقق من Firewall:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

4. التحقق من DNS:
```bash
# تأكد من أن الدومين يشير إلى IP الصحيح
dig ai-agent.bankid-sy.com
```

### 5. ❌ مشكلة Dependencies (React 19 vs React 18)

**الخطأ:**
```
peer react@"^18.0.0" from @testing-library/react@14.3.1
```

**الحل:**
تم إصلاح Dockerfile لاستخدام `--legacy-peer-deps`. إذا استمرت المشكلة:

```bash
cd /home/ai/ai-agent/frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm run build
```

### 6. ❌ متغيرات البيئة مفقودة

**الخطأ:**
```
WARNING: The DATABASE_URL variable is not set. Defaulting to a blank string.
```

**الحل:**
```bash
cd /home/ai/ai-agent

# إنشاء ملف .env إذا لم يكن موجوداً
if [ ! -f .env ]; then
  cat > .env << 'EOF'
DATABASE_URL=postgresql://ai_agent:ai_agent_password@postgres:5432/ai_agent
SECRET_KEY=ai-agent-secret-key-change-in-production
JWT_SECRET_KEY=ai-agent-jwt-secret-change-in-production
POSTGRES_DB=ai_agent
POSTGRES_USER=ai_agent
POSTGRES_PASSWORD=ai_agent_password
GRAFANA_ADMIN_PASSWORD=admin123
GRAFANA_ROOT_URL=http://localhost:3001
NEXT_PUBLIC_AGENT_API_URL=https://ai-agent.bankid-sy.com/api
NEXT_PUBLIC_BACKEND_URL=https://ai-agent.bankid-sy.com/api
NEXT_PUBLIC_AGENT_WS_URL=wss://ai-agent.bankid-sy.com/ws/chat
EOF
fi
```

## الترتيب الصحيح للتشغيل

```bash
cd /home/ai/ai-agent

# 1. تأكد من وجود ملف .env
[ -f .env ] || echo "⚠️ ملف .env غير موجود!"

# 2. تشغيل Backend
./start_backend.sh

# 3. انتظر قليلاً ثم شغّل Frontend
sleep 10
./start_frontend.sh

# 4. بعد أن يعمل Frontend، شغّل Nginx
sleep 10
./start_nginx.sh
```

## أوامر مفيدة للتشخيص

```bash
# عرض حالة جميع الحاويات
docker ps -a

# عرض السجلات
docker logs ai-agent-backend-prod
docker logs ai-agent-frontend-prod
docker logs ai-agent-nginx

# إعادة بناء صورة
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# إزالة الحاويات القديمة
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# تنظيف Docker
docker system prune -a
```

## التحقق من الصحة

```bash
# Backend Health
curl http://localhost:8000/health

# Frontend (يجب أن يعمل بعد nginx)
curl -k https://ai-agent.bankid-sy.com/health

# Nginx Status
docker exec ai-agent-nginx nginx -t
```

