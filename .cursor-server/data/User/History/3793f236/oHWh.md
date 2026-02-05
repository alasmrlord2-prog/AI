# 🚀 SHIFTWAVE AI Platform

نظام شامل يتكون من ثلاث خدمات منفصلة:
- **AI-Agent** - على `ai-agent.bankid-sy.com` (port 3000)
- **CRM** - على `crm.bankid-sy.com` (port 3001)
- **AAA** - على `aaa.bankid-sy.com` (port 3002)

جميع الخدمات متصلة بنفس Backend على port 8000.

---

## 🏗️ البنية

```
ai-agent/
├── backend/              # FastAPI Backend (port 8000)
│   ├── app/              # Application code
│   ├── start.sh          # ✅ تشغيل Backend + Ollama + Postgres
│   ├── stop.sh           # ✅ إيقاف Backend + Ollama + Postgres
│   └── restart.sh        # ✅ إعادة تشغيل Backend + Ollama + Postgres
│
├── frontend/             # Next.js Frontend
│   ├── app/              # Application code
│   ├── start-all.sh      # ✅ تشغيل جميع Frontends (3000, 3001, 3002)
│   ├── stop-all.sh       # ✅ إيقاف جميع Frontends
│   └── pm2-start.sh      # ✅ تشغيل باستخدام PM2
│
├── docker-compose.yml    # Docker configuration (Backend, Ollama, Postgres, Frontend)
├── ecosystem.config.js   # PM2 configuration
├── nginx-ai-agent-complete.conf  # NGINX config للـ AI-Agent
├── nginx-crm-complete.conf       # NGINX config للـ CRM
├── nginx-aaa-complete.conf       # NGINX config للـ AAA
└── setup-all-services.sh         # إعداد NGINX
```

---

## 🚀 البدء السريع

### الخطوة 1: إعداد NGINX

```bash
sudo ./setup-all-services.sh
```

هذا السكربت سيقوم بـ:
- نسخ ملفات NGINX إلى `/etc/nginx/sites-available/`
- تفعيل المواقع
- اختبار التكوين
- إعادة تحميل NGINX

---

### الخطوة 2: تشغيل Backend (مع Ollama و Postgres)

```bash
cd backend
./start.sh
```

**التحقق:**
```bash
curl http://localhost:8000/health
```

**ملاحظة:** بعد تشغيل Ollama لأول مرة، تحتاج تحميل model:
```bash
docker exec -it ai-agent-ollama ollama pull llama3.2:1b
```

---

### الخطوة 3: تشغيل Frontends

#### الطريقة 1: PM2 (موصى به)

```bash
cd frontend
./pm2-start.sh
```

#### الطريقة 2: start-all.sh

```bash
cd frontend
./start-all.sh
```

---

## 🎯 URLs النهائية

| الخدمة | Domain | Frontend Port | Backend Port |
|--------|--------|---------------|--------------|
| **AI-Agent** | http://ai-agent.bankid-sy.com | 3000 | 8000 |
| **CRM** | http://crm.bankid-sy.com | 3001 | 8000 |
| **AAA** | http://aaa.bankid-sy.com | 3002 | 8000 |

---

## 🔧 السكربتات الأساسية

### Backend Scripts

#### `backend/start.sh`
تشغيل Backend + Ollama + Postgres:
```bash
cd backend
./start.sh
```

#### `backend/stop.sh`
إيقاف Backend + Ollama + Postgres:
```bash
cd backend
./stop.sh
```

#### `backend/restart.sh`
إعادة تشغيل Backend + Ollama + Postgres:
```bash
cd backend
./restart.sh
```

### Frontend Scripts

#### `frontend/start-all.sh`
تشغيل جميع Frontends (AI-Agent, CRM, AAA):
```bash
cd frontend
./start-all.sh
```

#### `frontend/stop-all.sh`
إيقاف جميع Frontends:
```bash
cd frontend
./stop-all.sh
```

#### `frontend/pm2-start.sh`
تشغيل جميع Frontends باستخدام PM2:
```bash
cd frontend
./pm2-start.sh
```

---

## 🐳 Docker Services

### الخدمات المتوفرة:

1. **ollama** - AI Model Service (port 11434)
2. **postgres** - Database (port 5432)
3. **backend** - FastAPI Backend (port 8000)
4. **frontend** - Next.js Frontend (port 3000)

### أوامر Docker مفيدة:

```bash
# تشغيل جميع الخدمات
docker-compose up -d

# إيقاف جميع الخدمات
docker-compose down

# عرض السجلات
docker-compose logs -f backend
docker-compose logs -f ollama

# إعادة تشغيل service معين
docker-compose restart backend

# عرض حالة الخدمات
docker-compose ps
```

---

## 🔧 الإعدادات

### Backend Environment Variables

في `docker-compose.yml`:
- `DATABASE_URL` - PostgreSQL connection string
- `OLLAMA_URL` - Ollama service URL (http://ollama:11434)
- `DEBUG` - Debug mode
- `LOG_LEVEL` - Logging level
- `SECRET_KEY` - Secret key for encryption

### Frontend Environment Variables

- `NEXT_PUBLIC_AGENT_API_URL` - Backend API URL
- `NEXT_PUBLIC_BACKEND_URL` - Backend URL
- `NEXT_PUBLIC_AGENT_WS_URL` - WebSocket URL

---

## 📝 ملاحظات مهمة

### Ollama Models

بعد تشغيل Ollama لأول مرة، تحتاج تحميل model:
```bash
docker exec -it ai-agent-ollama ollama pull llama3.2:1b
```

أو models أخرى:
```bash
docker exec -it ai-agent-ollama ollama pull mistral
docker exec -it ai-agent-ollama ollama pull llama2
```

### Ports المستخدمة

- **3000** - AI-Agent Frontend
- **3001** - CRM Frontend
- **3002** - AAA Frontend
- **8000** - Backend API
- **11434** - Ollama
- **5432** - PostgreSQL

### Troubleshooting

#### Backend لا يستجيب:
```bash
cd backend
./restart.sh
docker-compose logs -f backend
```

#### Ollama لا يعمل:
```bash
docker-compose logs -f ollama
docker-compose restart ollama
```

#### Frontend لا يعمل:
```bash
cd frontend
./stop-all.sh
./start-all.sh
```

---

## 📚 الوثائق الإضافية

- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Ollama API: http://localhost:11434/api/tags

---

## ✅ Checklist للتشغيل

- [ ] إعداد NGINX: `sudo ./setup-all-services.sh`
- [ ] تشغيل Backend: `cd backend && ./start.sh`
- [ ] تحميل Ollama model: `docker exec -it ai-agent-ollama ollama pull llama3.2:1b`
- [ ] تشغيل Frontends: `cd frontend && ./pm2-start.sh`
- [ ] التحقق من Health: `curl http://localhost:8000/health`

---

## 🎉 جاهز!

بعد إكمال الخطوات أعلاه، جميع الخدمات ستعمل بشكل طبيعي.
