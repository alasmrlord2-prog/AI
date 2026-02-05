# 🔧 إصلاح المشاكل - Fix Instructions

## المشكلة 1: Backend لا يعمل - ModuleNotFoundError

### الحل:
```bash
cd /home/ai/ai-agent/backend

# تثبيت Dependencies
./install_dependencies.sh

# أو يدوياً:
pip install -r requirements.txt
```

### ثم تشغيل الباك إند:
```bash
./start_backend.sh
```

---

## المشكلة 2: Frontend Warning عن CORS

### تم الإصلاح! ✅
تم تحديث `next.config.ts` لدعم cross-origin requests.

### إذا استمر التحذير:
```bash
cd /home/ai/ai-agent/frontend
# إعادة تشغيل
./restart_frontend.sh
```

---

## خطوات التشغيل الكاملة

### 1. تثبيت Dependencies
```bash
# Backend
cd /home/ai/ai-agent/backend
./install_dependencies.sh

# Frontend (إذا لم تكن مثبتة)
cd /home/ai/ai-agent/frontend
npm install
```

### 2. تشغيل الخدمات
```bash
# Terminal 1 - Backend
cd /home/ai/ai-agent/backend
./start_backend.sh

# Terminal 2 - Frontend
cd /home/ai/ai-agent/frontend
./start_frontend.sh
```

### 3. التحقق من الحالة
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## Troubleshooting

### إذا فشل تثبيت dependencies:
```bash
# Backend
cd backend
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### إذا البورت مستخدم:
```bash
# Backend
./stop_backend.sh

# Frontend
./stop_frontend.sh
```

---

**بعد الإصلاح، كل شيء يجب أن يعمل! ✅**

