# AI Agent Project - نظام إدارة DevOps متكامل

## 🚀 البدء السريع

### Backend
```bash
cd backend
./start_backend.sh    # تشغيل
./stop_backend.sh     # إيقاف
./restart_backend.sh  # إعادة تشغيل
```

### Frontend
```bash
cd frontend
./start_frontend.sh    # تشغيل
./stop_frontend.sh     # إيقاف
./restart_frontend.sh  # إعادة تشغيل
```

## 🌐 URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎯 الميزات الرئيسية

### 1. CI/CD Pipeline
- Git Integration (Clone/Pull)
- Pipeline Runner
- Deploy Engine (Docker, Kubernetes, RSync)

### 2. AI Debugger
- Log Watcher
- AI Error Analyzer
- Auto Patch

### 3. Monitoring & Auto Repair
- Health Checks
- Auto Repair Engine
- Alert Manager

### 4. Workflow Builder
- Node-based Workflows
- Flow Executor

### 5. Audit Trail
- Complete Activity Logging
- Export & Filtering

### 6. Backup Manager
- Database Backups (PostgreSQL, MySQL)
- Docker Volumes Backup

### 7. Incident Management
- Incident Tracking
- Root Cause Analysis

### 8. Visualization
- Network Map
- Architecture Graph
- Metrics Heatmap

## 📦 التبعيات

```bash
cd backend
pip install -r requirements.txt
```

## 🔧 الإعداد

1. إنشاء مجلدات البيانات:
```bash
sudo mkdir -p /data/repos /data/backups
sudo chown -R $USER:$USER /data/repos /data/backups
```

2. إعداد Telegram Bot (اختياري):
```bash
# في backend/.env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 📝 ملاحظات

- جميع الـ APIs تتطلب authentication (استثناء `/health`)
- CI/CD repositories: `/data/repos/`
- Backups: `/data/backups/`
- Audit logs: `audit.db`
- Incidents: `incidents.db`

## 🔧 الإصلاحات

راجع `FIXES.md` لحل المشاكل الشائعة
