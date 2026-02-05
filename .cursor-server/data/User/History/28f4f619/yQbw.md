# دليل الاختبار - Testing Guide

## ✅ جميع التحسينات مكتملة وجاهزة للاختبار!

## 🧪 خطوات الاختبار

### 1. التحقق من التثبيت

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend  
cd frontend
npm install
```

### 2. إعداد Environment Variables

```bash
# Backend
cd backend
cp env.example .env
# تعديل .env حسب احتياجاتك

# Frontend
cd frontend
cp env.example .env.local
# تعديل .env.local
```

### 3. اختبار Backend

#### أ. اختبار البنية الجديدة (main_new.py)

```bash
cd backend

# تشغيل السيرفر
uvicorn app.main_new:app --reload --host 0.0.0.0 --port 8000
```

#### ب. اختبار الـ Endpoints

افتح المتصفح واذهب إلى:
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/health` - Health check
- `http://localhost:8000/` - Root endpoint

#### ج. تشغيل Unit Tests

```bash
cd backend
pytest tests/ -v
```

### 4. اختبار Frontend

```bash
cd frontend
npm run dev
```

افتح المتصفح:
- `http://localhost:3000` - Frontend application

#### تشغيل Frontend Tests

```bash
cd frontend
npm test
```

### 5. اختبار Docker Compose (اختياري)

```bash
# من جذر المشروع
docker-compose up -d

# التحقق من الخدمات
docker-compose ps

# عرض الـ logs
docker-compose logs -f
```

## 🔍 التحقق من البنية

### Backend Structure

```
backend/app/
├── api/              ✅ جميع الـ endpoints
├── core/             ✅ Config & Database
├── models/           ✅ Pydantic models
├── services/         ✅ جاهز للاستخدام
├── utils/            ✅ Helper functions
├── exceptions/       ✅ Error handling
├── monitoring/       ✅ Logging & Metrics
└── main_new.py       ✅ Main app
```

### Frontend Structure

```
frontend/
├── __tests__/        ✅ Test files
├── app/              ✅ Next.js app
├── components/       ✅ React components
└── lib/              ✅ Utilities
```

## 📋 Checklist للاختبار

### Backend Tests
- [ ] Health check endpoint
- [ ] Authentication endpoints
- [ ] Chat endpoints
- [ ] Settings endpoints
- [ ] Tools endpoints
- [ ] Monitor endpoints
- [ ] Billing endpoints
- [ ] WebSocket connections
- [ ] Error handling
- [ ] Database connections

### Frontend Tests
- [ ] Component rendering
- [ ] API integration
- [ ] User interactions
- [ ] Error states
- [ ] Loading states

### Integration Tests
- [ ] Backend ↔ Frontend communication
- [ ] WebSocket real-time updates
- [ ] Authentication flow
- [ ] Database operations

## 🐛 Troubleshooting

### مشكلة: Import errors

**الحل:**
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### مشكلة: Database connection

**الحل:**
- تأكد من أن `DATABASE_URL` في `.env` صحيح
- إذا كنت تستخدم SQLite، تأكد من وجود permissions للكتابة

### مشكلة: Port already in use

**الحل:**
```bash
# Backend
lsof -ti:8000 | xargs kill -9

# Frontend
lsof -ti:3000 | xargs kill -9
```

### مشكلة: Module not found

**الحل:**
```bash
# تأكد من تثبيت جميع dependencies
pip install -r requirements.txt
npm install
```

## 📊 Coverage Reports

### Backend Coverage

```bash
cd backend
pytest tests/ --cov=app --cov-report=html
# افتح htmlcov/index.html
```

### Frontend Coverage

```bash
cd frontend
npm run test:coverage
# افتح coverage/index.html
```

## 🚀 Next Steps

بعد التأكد من أن كل شيء يعمل:

1. ✅ كتابة المزيد من tests
2. ✅ إضافة integration tests
3. ✅ تحسين error messages
4. ✅ إضافة logging
5. ✅ تحسين documentation

---

**جاهز للاختبار! 🎉**

