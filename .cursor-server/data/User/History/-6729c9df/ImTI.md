# دليل السكربتات - Scripts Guide

## 🚀 سكربتات الباك إند (Backend)

### 1. تشغيل الباك إند
```bash
cd backend
./start_backend.sh
```

**ما يفعله:**
- ✅ يتحقق من Python و dependencies
- ✅ يتحقق من أن البورت 8000 متاح
- ✅ يشغل السيرفر على `app.main_new:app` (البنية الجديدة)
- ✅ يعرض حالة التشغيل والـ URLs

### 2. إيقاف الباك إند
```bash
cd backend
./stop_backend.sh
```

**ما يفعله:**
- ✅ يوقف جميع عمليات uvicorn
- ✅ يحرر البورت 8000
- ✅ يتحقق من أن كل شيء توقف

### 3. إعادة تشغيل الباك إند
```bash
cd backend
./restart_backend.sh
```

**ما يفعله:**
- ✅ يوقف الباك إند
- ✅ ينتظر 3 ثواني
- ✅ يشغل الباك إند من جديد

---

## 🎨 سكربتات الفرونت إند (Frontend)

### 1. تشغيل الفرونت إند
```bash
cd frontend
./start_frontend.sh
```

**ما يفعله:**
- ✅ يتحقق من Node.js و npm
- ✅ يثبت dependencies إن لم تكن موجودة
- ✅ ينشئ `.env.local` من `env.example` إن لم يكن موجود
- ✅ يشغل Next.js development server على البورت 3000

### 2. إيقاف الفرونت إند
```bash
cd frontend
./stop_frontend.sh
```

**ما يفعله:**
- ✅ يوقف جميع عمليات Next.js
- ✅ يحرر البورت 3000
- ✅ يتحقق من أن كل شيء توقف

### 3. إعادة تشغيل الفرونت إند
```bash
cd frontend
./restart_frontend.sh
```

**ما يفعله:**
- ✅ يوقف الفرونت إند
- ✅ ينتظر 3 ثواني
- ✅ يشغل الفرونت إند من جديد

---

## 📋 استخدام سريع

### تشغيل كل شيء
```bash
# Terminal 1 - Backend
cd /home/ai/ai-agent/backend
./start_backend.sh

# Terminal 2 - Frontend
cd /home/ai/ai-agent/frontend
./start_frontend.sh
```

### إيقاف كل شيء
```bash
# Terminal 1
cd /home/ai/ai-agent/backend
./stop_backend.sh

# Terminal 2
cd /home/ai/ai-agent/frontend
./stop_frontend.sh
```

### إعادة تشغيل كل شيء
```bash
# Backend
cd /home/ai/ai-agent/backend
./restart_backend.sh

# Frontend
cd /home/ai/ai-agent/frontend
./restart_frontend.sh
```

---

## 🌐 URLs بعد التشغيل

### Backend
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Frontend
- Application: http://localhost:3000

---

## 📝 ملاحظات

1. **الباك إند** يستخدم `app.main_new:app` (البنية الجديدة المحسّنة)
2. **الـ logs** تُحفظ في:
   - Backend: `backend/backend.log`
   - Frontend: `frontend/frontend.log`
3. **التحقق من الحالة:**
   ```bash
   # Backend
   tail -f backend/backend.log
   
   # Frontend
   tail -f frontend/frontend.log
   ```

---

## 🔧 Troubleshooting

### البورت مستخدم
```bash
# Backend
lsof -ti:8000 | xargs kill -9

# Frontend
lsof -ti:3000 | xargs kill -9
```

### السكربت لا يعمل
```bash
chmod +x start_backend.sh
chmod +x stop_backend.sh
chmod +x restart_backend.sh
```

---

**جاهز للاستخدام! 🎉**

