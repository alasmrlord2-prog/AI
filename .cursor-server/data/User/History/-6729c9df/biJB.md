# 📋 دليل استخدام الـ Scripts

## 🔧 Backend Scripts

### 1. `./backend/start.sh`
- **الاستخدام:** بدء Backend باستخدام Docker
- **الوصف:** يبدأ Backend, PostgreSQL, و Ollama في Docker containers
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./backend/start.sh
  ```

### 2. `./backend/stop.sh`
- **الاستخدام:** إيقاف Backend (Docker)
- **الوصف:** يوقف جميع Docker containers
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./backend/stop.sh
  ```

### 3. `./backend/restart.sh`
- **الاستخدام:** إعادة تشغيل Backend (Docker)
- **الوصف:** يوقف ثم يبدأ Backend في Docker
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./backend/restart.sh
  ```

### 4. `./backend/restart-direct.sh` ⭐ (جديد)
- **الاستخدام:** إعادة تشغيل Backend مباشرة (بدون Docker)
- **الوصف:** يوقف جميع uvicorn processes ويبدأ Backend مباشرة
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./backend/restart-direct.sh
  ```

### 5. `./restart-backend.sh` ⭐ (جديد - موصى به)
- **الاستخدام:** إعادة تشغيل Backend بشكل كامل مع التحقق
- **الوصف:** يوقف جميع processes، يتحقق من الـ routers، ويبدأ Backend
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./restart-backend.sh
  ```
- **ملاحظة:** يحتاج sudo

---

## 🎨 Frontend Scripts

### 6. `./frontend/start-all.sh`
- **الاستخدام:** بدء جميع Frontends (Dashboard, CRM, AAA)
- **الوصف:** يبدأ 3 Next.js processes على ports 3000, 3001, 3002
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./frontend/start-all.sh
  ```

### 7. `./frontend/stop-all.sh`
- **الاستخدام:** إيقاف جميع Frontends
- **الوصف:** يوقف جميع Next.js processes
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./frontend/stop-all.sh
  ```

### 8. `./frontend/pm2-start.sh`
- **الاستخدام:** بدء Frontends باستخدام PM2
- **الوصف:** يبدأ Frontends باستخدام PM2 process manager
- **الاستخدام:**
  ```bash
  cd /home/ai/ai-agent
  ./frontend/pm2-start.sh
  ```

---

## 🚀 سيناريوهات الاستخدام

### السيناريو 1: إعادة تشغيل Backend فقط
```bash
cd /home/ai/ai-agent
./restart-backend.sh
```

### السيناريو 2: إعادة تشغيل Frontend فقط
```bash
cd /home/ai/ai-agent
./frontend/stop-all.sh
./frontend/start-all.sh
```

### السيناريو 3: إعادة تشغيل كل شيء
```bash
cd /home/ai/ai-agent
# Backend
./restart-backend.sh

# Frontend
./frontend/stop-all.sh
./frontend/start-all.sh
```

### السيناريو 4: استخدام Docker
```bash
cd /home/ai/ai-agent
# Backend
./backend/restart.sh

# Frontend (لا يستخدم Docker)
./frontend/start-all.sh
```

---

## ✅ التحقق من الحالة

### Backend:
```bash
# Health check
curl http://localhost:8000/health

# Check routes
curl -s http://localhost:8000/openapi.json | python3 -c "import json, sys; data = json.load(sys.stdin); paths = [p for p in data['paths'].keys() if '/api/identity' in p or '/api/crm' in p]; print(f'Found {len(paths)} routes')"
```

### Frontend:
```bash
# Check ports
ss -tlnp | grep -E ':(3000|3001|3002)'

# Check processes
ps aux | grep -E "[n]ext dev"
```

---

## 📝 Logs

### Backend Logs:
- Direct mode: `tail -f /tmp/backend-direct.log`
- Restart script: `tail -f /tmp/backend-restart.log`
- Docker: `docker-compose logs -f backend`

### Frontend Logs:
- AI-Agent: `tail -f /tmp/frontend-ai-agent.log`
- CRM: `tail -f /tmp/frontend-crm.log`
- AAA: `tail -f /tmp/frontend-aaa.log`

---

## ⚠️ ملاحظات مهمة

1. **Backend الحالي:** يعمل مباشرة بـ uvicorn (ليس Docker)
2. **Port 8000:** يجب أن يكون متاحاً قبل بدء Backend
3. **Python 3.11:** مطلوب لتشغيل Backend
4. **email-validator:** يجب تثبيته في Python 3.11
5. **Sudo:** قد تحتاج sudo لإيقاف processes التي تعمل كـ root

---

## 🎯 الحل السريع للمشكلة الحالية

```bash
cd /home/ai/ai-agent
./restart-backend.sh
```

هذا سيقوم بـ:
1. إيقاف جميع Backend processes
2. التحقق من الـ routers
3. بدء Backend مع جميع الـ routes
4. التحقق من أن كل شيء يعمل

