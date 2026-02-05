# الملفات المهمة - Essential Files

## 📁 البنية الأساسية

### Backend
```
backend/
├── app/
│   ├── main_new.py          ⭐ Main app (البنية الجديدة)
│   ├── core/                 ⭐ Configuration & Database
│   ├── api/                  ⭐ API endpoints
│   ├── models/               ⭐ Pydantic models
│   ├── exceptions/           ⭐ Error handling
│   └── monitoring/           ⭐ Logging & Metrics
├── start_backend.sh          ⭐ تشغيل الباك إند
├── stop_backend.sh           ⭐ إيقاف الباك إند
├── restart_backend.sh        ⭐ إعادة تشغيل الباك إند
├── requirements.txt          ⭐ Dependencies
└── env.example               ⭐ Environment variables template
```

### Frontend
```
frontend/
├── start_frontend.sh         ⭐ تشغيل الفرونت إند
├── stop_frontend.sh          ⭐ إيقاف الفرونت إند
├── restart_frontend.sh       ⭐ إعادة تشغيل الفرونت إند
├── package.json              ⭐ Dependencies
└── env.example               ⭐ Environment variables template
```

## 🚀 السكربتات

### Backend Scripts
- `backend/start_backend.sh` - تشغيل الباك إند
- `backend/stop_backend.sh` - إيقاف الباك إند
- `backend/restart_backend.sh` - إعادة تشغيل الباك إند

### Frontend Scripts
- `frontend/start_frontend.sh` - تشغيل الفرونت إند
- `frontend/stop_frontend.sh` - إيقاف الفرونت إند
- `frontend/restart_frontend.sh` - إعادة تشغيل الفرونت إند

## 📚 الملفات المرجعية

### التوثيق الأساسي
- `README.md` - الدليل الرئيسي
- `QUICK_START.md` - البدء السريع
- `SCRIPTS_GUIDE.md` - دليل السكربتات
- `ESSENTIAL_FILES.md` - هذا الملف

### التوثيق التفصيلي
- `docs/api/` - API documentation
- `docs/development/` - Development guide
- `docs/deployment/` - Deployment guide

## ⚙️ Configuration Files

### Backend
- `backend/env.example` - Environment variables template
- `backend/requirements.txt` - Python dependencies
- `backend/alembic.ini` - Database migrations config

### Frontend
- `frontend/env.example` - Environment variables template
- `frontend/package.json` - Node.js dependencies
- `frontend/jest.config.js` - Test configuration

## 🐳 Docker (اختياري)

- `docker-compose.yml` - Development setup
- `docker-compose.prod.yml` - Production setup

---

**للبدء السريع:**
1. راجع `SCRIPTS_GUIDE.md` لاستخدام السكربتات
2. راجع `README.md` للدليل الكامل
3. استخدم السكربتات للبدء السريع

