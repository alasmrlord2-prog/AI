# إعداد المشروع - AI Agent

## المشاكل التي تم حلها

### 1. ✅ إنشاء Dockerfile للـ Frontend
تم إنشاء `frontend/Dockerfile` لبناء وتشغيل Next.js في Docker.

### 2. ✅ إنشاء ملف .env
تم إنشاء ملف `.env` في المجلد الرئيسي مع جميع المتغيرات المطلوبة.

### 3. ⚠️ تشغيل nginx
nginx يحتاج إلى تشغيل يدوي. استخدم الأمر التالي:

```bash
cd /home/ai/ai-agent
sudo docker-compose -f docker-compose.prod.yml up -d nginx
```

## خطوات التشغيل

### 1. إنشاء ملف .env (إذا لم يكن موجوداً)

```bash
cd /home/ai/ai-agent
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://ai_agent:ai_agent_password@postgres:5432/ai_agent

# Security Keys
SECRET_KEY=ai-agent-secret-key-change-in-production
JWT_SECRET_KEY=ai-agent-jwt-secret-change-in-production

# PostgreSQL Configuration
POSTGRES_DB=ai_agent
POSTGRES_USER=ai_agent
POSTGRES_PASSWORD=ai_agent_password

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=admin123
GRAFANA_ROOT_URL=http://localhost:3001

# Frontend Environment Variables
NEXT_PUBLIC_AGENT_API_URL=https://ai-agent.bankid-sy.com/api
NEXT_PUBLIC_BACKEND_URL=https://ai-agent.bankid-sy.com/api
NEXT_PUBLIC_AGENT_WS_URL=wss://ai-agent.bankid-sy.com/ws/chat
EOF
```

### 2. تشغيل Backend

```bash
cd /home/ai/ai-agent
./start_backend.sh
```

### 3. تشغيل Frontend

```bash
cd /home/ai/ai-agent
./start_frontend.sh
```

### 4. تشغيل nginx (مهم لحل مشكلة Cloudflare)

```bash
cd /home/ai/ai-agent
sudo docker-compose -f docker-compose.prod.yml up -d nginx
```

### 5. التحقق من حالة الخدمات

```bash
docker-compose -f docker-compose.prod.yml ps
```

## حل مشكلة Cloudflare Error 522

مشكلة Error 522 تعني أن Cloudflare لا يستطيع الاتصال بالخادم. الحل:

1. **تأكد من تشغيل nginx:**
```bash
sudo docker-compose -f docker-compose.prod.yml up -d nginx
```

2. **تحقق من أن nginx يعمل:**
```bash
docker ps | grep nginx
```

3. **تحقق من السجلات:**
```bash
docker logs ai-agent-nginx
```

4. **تحقق من أن المنافذ 80 و 443 مفتوحة:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

5. **تحقق من إعدادات DNS:**
تأكد من أن الدومين `ai-agent.bankid-sy.com` يشير إلى IP `3.76.209.35`

## ملاحظات مهمة

- **ملف .env**: تأكد من تغيير `SECRET_KEY` و `JWT_SECRET_KEY` في الإنتاج
- **nginx**: يجب تشغيله دائماً ليعمل الموقع عبر الدومين
- **SSL Certificates**: تم إنشاء شهادات SSL مؤقتة. للاستخدام في الإنتاج، استخدم Let's Encrypt

## استكشاف الأخطاء

### إذا فشل بناء Frontend:
```bash
cd /home/ai/ai-agent/frontend
npm install
npm run build
```

### إذا فشل تشغيل nginx:
```bash
# تحقق من شهادات SSL
ls -la nginx/ssl/

# إذا لم تكن موجودة:
cd nginx && ./generate-ssl.sh && cd ..
```

### إذا كانت الحاويات لا تبدأ:
```bash
# إعادة بناء الصور
docker-compose -f docker-compose.prod.yml build

# إزالة الحاويات القديمة
docker-compose -f docker-compose.prod.yml down
```

