# AI Agent - نظام إدارة DevOps

## 📋 السكربتات المتوفرة

### 🔵 Backend (3 سكربتات)
- `start_backend.sh` - تشغيل Backend (يبدأ: postgres, ollama, backend)
- `restart_backend.sh` - إعادة تشغيل Backend
- `stop_backend.sh` - إيقاف Backend

### 🟢 Frontend (3 سكربتات)
- `start_frontend.sh` - تشغيل Frontend (يبدأ: postgres, ollama, backend, frontend)
- `restart_frontend.sh` - إعادة تشغيل Frontend
- `stop_frontend.sh` - إيقاف Frontend

## 🚀 طريقة الاستخدام

### 1. تشغيل Backend

```bash
./start_backend.sh
```

### 3. تشغيل Frontend

```bash
./start_frontend.sh
```

### 4. تشغيل Nginx

```bash
docker-compose -f docker-compose.prod.yml up -d nginx
```

## 🌐 الوصول للموقع

- **الموقع الرئيسي**: http://ai-agent.bankid-sy.com
- **API**: http://ai-agent.bankid-sy.com/api
- **API Docs**: http://ai-agent.bankid-sy.com/api/docs
- **Health Check**: http://ai-agent.bankid-sy.com/health

## ⚙️ الإعدادات

### ملف .env

يجب أن يحتوي على:
```bash
DATABASE_URL=postgresql://ai_agent:ai_agent_password@postgres:5432/ai_agent
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
POSTGRES_DB=ai_agent
POSTGRES_USER=ai_agent
POSTGRES_PASSWORD=ai_agent_password
GRAFANA_ADMIN_PASSWORD=admin123
GRAFANA_ROOT_URL=http://localhost:3001
NEXT_PUBLIC_AGENT_API_URL=http://ai-agent.bankid-sy.com/api
NEXT_PUBLIC_BACKEND_URL=http://ai-agent.bankid-sy.com/api
NEXT_PUBLIC_AGENT_WS_URL=ws://ai-agent.bankid-sy.com/ws/chat
```

### الدومين والـ IP

- **الدومين**: ai-agent.bankid-sy.com
- **IP**: 3.76.209.35


## 📝 الأوامر المفيدة

### عرض حالة الخدمات
```bash
docker-compose -f docker-compose.prod.yml ps
```

### عرض السجلات
```bash
# Backend
docker logs -f ai-agent-backend-prod

# Frontend
docker logs -f ai-agent-frontend-prod

# Nginx
docker logs -f ai-agent-nginx
```

### إيقاف جميع الخدمات
```bash
docker-compose -f docker-compose.prod.yml down
```

## 🔧 استكشاف الأخطاء

### إذا فشل تشغيل Backend
```bash
docker logs ai-agent-backend-prod
```

### إذا فشل تشغيل Frontend
```bash
docker logs ai-agent-frontend-prod
```

### إذا فشل SSL Certificate
```bash
# تحقق من الشهادات
ls -la nginx/ssl/live/ai-agent.bankid-sy.com/

# إذا لم تكن موجودة، استخدم self-signed مؤقتاً
cd nginx && ./generate-ssl.sh && cd ..
```

### Cloudflare Error 522

إذا ظهر Error 522:
1. تأكد من أن nginx يعمل: `docker ps | grep nginx`
2. في Cloudflare، أزل Proxy (DNS Only) أو غيّر SSL/TLS mode إلى "Full"
3. تحقق من المنافذ: `sudo netstat -tlnp | grep -E ':(80|443)'`

## 📊 الخدمات

المشروع يستخدم:
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React)
- **Database**: PostgreSQL
- **AI**: Ollama
- **Web Server**: Nginx
- **Monitoring**: Prometheus, Grafana, Loki

## 🔄 الترتيب الصحيح للتشغيل

```bash
# 1. Backend
./start_backend.sh

# 2. Frontend (بعد 10 ثواني)
sleep 10
./start_frontend.sh

# 3. Nginx (بعد 10 ثواني)
sleep 10
docker-compose -f docker-compose.prod.yml up -d nginx

# 4. SSL Certificate (اختياري - Let's Encrypt)
./install-ssl.sh
```

## 💡 ملاحظات مهمة

1. **Frontend يعتمد على Backend**: عند تشغيل `start_frontend.sh`، سيتم تشغيل backend تلقائياً
2. **SSL Certificates**: استخدم Let's Encrypt للإنتاج، أو self-signed للتطوير
3. **Cloudflare**: إذا كنت تستخدم Cloudflare، تأكد من إعدادات SSL/TLS mode
4. **Firewall**: تأكد من فتح المنافذ 80 و 443
