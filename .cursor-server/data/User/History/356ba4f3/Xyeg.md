# 🔧 خدمات المشروع - الحالة والإصلاحات

## 📋 الخدمات المتوفرة

### 1. Backend Services (Docker)
- **PostgreSQL** - Database (port 5432)
- **Ollama** - AI Model Service (port 11434)
- **Backend API** - FastAPI (port 8000)

### 2. Frontend Services (PM2/Node)
- **AI-Agent Frontend** - port 3000
- **CRM Frontend** - port 3001
- **AAA Frontend** - port 3002

### 3. NGINX
- **ai-agent.bankid-sy.com** → port 3000
- **crm.bankid-sy.com** → port 3001
- **aaa.bankid-sy.com** → port 3002

---

## ✅ الإصلاحات التي تمت

### 1. إصلاح سكربتات Backend
- ✅ `backend/start.sh` - يستخدم الآن docker-compose.yml من المجلد الجذر
- ✅ `backend/stop.sh` - يستخدم الآن docker-compose.yml من المجلد الجذر
- ✅ `backend/restart.sh` - يستخدم الآن docker-compose.yml من المجلد الجذر
- ✅ إضافة انتظار أطول للـ health check

### 2. إصلاح FIX_PORT_8000.sh
- ✅ إيقاف Docker containers قبل قتل العمليات
- ✅ دعم fuser (يتطلب sudo)
- ✅ تحقق أفضل من حالة المنفذ

### 3. إصلاح Dockerfile
- ✅ إضافة curl للـ healthcheck

### 4. سكربتات جديدة
- ✅ `check-all-services.sh` - فحص شامل لجميع الخدمات
- ✅ `fix-and-start-all.sh` - إصلاح وتشغيل جميع الخدمات

---

## 🚀 كيفية التشغيل

### الطريقة السريعة (موصى بها)
```bash
cd /home/ai/ai-agent
./fix-and-start-all.sh
```

### الطريقة اليدوية

#### 1. إصلاح وإيقاف المنفذ 8000
```bash
cd /home/ai/ai-agent
./FIX_PORT_8000.sh
```

#### 2. تشغيل Backend
```bash
cd /home/ai/ai-agent/backend
./start.sh
```

#### 3. التحقق من Backend
```bash
curl http://localhost:8000/health
```

#### 4. تشغيل Frontends
```bash
cd /home/ai/ai-agent/frontend
./pm2-start.sh
```

---

## 🔍 فحص الخدمات

### فحص شامل
```bash
cd /home/ai/ai-agent
./check-all-services.sh
```

### فحص Docker containers
```bash
docker ps | grep ai-agent
```

### فحص Backend logs
```bash
docker-compose -f /home/ai/ai-agent/docker-compose.yml logs -f backend
```

### فحص PM2 processes
```bash
pm2 status
pm2 logs
```

---

## 🛠️ حل المشاكل

### Backend لا يستجيب
```bash
cd /home/ai/ai-agent/backend
./restart.sh
```

### Port 8000 محجوز
```bash
cd /home/ai/ai-agent
./FIX_PORT_8000.sh
```

### إعادة بناء Docker images
```bash
cd /home/ai/ai-agent
docker-compose -f docker-compose.yml build --no-cache
```

### إيقاف جميع الخدمات
```bash
# Backend
cd /home/ai/ai-agent/backend
./stop.sh

# Frontend
cd /home/ai/ai-agent/frontend
pm2 stop all
```

---

## 📝 ملاحظات مهمة

1. **Ollama Model**: بعد تشغيل Ollama لأول مرة، قد تحتاج لتحميل model:
   ```bash
   docker exec -it ai-agent-ollama ollama pull llama3.2:1b
   ```

2. **Docker Permissions**: إذا واجهت مشاكل في الصلاحيات:
   ```bash
   sudo usermod -aG docker $USER
   # ثم logout و login مرة أخرى
   ```

3. **Ports**: تأكد أن المنافذ التالية متاحة:
   - 3000, 3001, 3002 (Frontends)
   - 8000 (Backend)
   - 11434 (Ollama)
   - 5432 (PostgreSQL)

---

## ✅ Checklist

- [ ] إصلاح port 8000: `./FIX_PORT_8000.sh`
- [ ] تشغيل Backend: `cd backend && ./start.sh`
- [ ] التحقق من Backend: `curl http://localhost:8000/health`
- [ ] تحميل Ollama model (إذا لزم): `docker exec -it ai-agent-ollama ollama pull llama3.2:1b`
- [ ] تشغيل Frontends: `cd frontend && ./pm2-start.sh`
- [ ] فحص جميع الخدمات: `./check-all-services.sh`

---

## 🎯 URLs النهائية

- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- AI-Agent: http://localhost:3000
- CRM: http://localhost:3001
- AAA: http://localhost:3002

