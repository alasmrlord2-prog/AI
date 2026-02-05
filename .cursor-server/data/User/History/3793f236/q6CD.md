# AI Agent System - نظام الوكيل الذكي

## 📋 نظرة عامة

نظام شامل لإدارة وتشغيل AI Agent مع نظام صلاحيات موحد يتحكم بكل الواجهات والميزات.

## 🏗️ البنية

```
ai-agent/
├── backend/              # FastAPI Backend
│   ├── app/             # Application Code
│   ├── start.sh         # بدء Backend
│   ├── stop.sh          # إيقاف Backend
│   ├── restart.sh       # إعادة تشغيل Backend
│   └── README.md        # دليل Backend
├── frontend/            # Next.js Frontend
│   ├── app/            # Next.js App
│   ├── start.sh        # بدء Frontend
│   ├── stop.sh         # إيقاف Frontend
│   ├── restart.sh      # إعادة تشغيل Frontend
│   └── README.md       # دليل Frontend
└── README.md           # هذا الملف
```

## 🚀 البدء السريع

### 1. تشغيل Backend

```bash
cd /home/ai/ai-agent/backend
./start.sh
```

الـ Backend سيعمل على: http://localhost:8000

### 2. تشغيل Frontend

```bash
cd /home/ai/ai-agent/frontend
./start.sh
```

الـ Frontend سيعمل على: http://localhost:3000

### 3. الوصول للنظام

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **API Docs**: http://localhost:8000/docs

## 📚 الوثائق

### Backend
- [Backend README](backend/README.md) - دليل شامل للـ Backend
- [Permission System](backend/PERMISSIONS_SYSTEM.md) - نظام الصلاحيات

### Frontend
- [Frontend README](frontend/README.md) - دليل شامل للـ Frontend

## 🔐 نظام الصلاحيات

النظام يحتوي على نظام صلاحيات موحد يتحكم بكل الواجهات:

### Agent Modes
- **Safe**: قراءة فقط، بدون run_shell
- **DevOps**: كل الصلاحيات مع approval للعمليات الخطيرة
- **Root**: كل الصلاحيات بدون قيود
- **Short**: جلسة واحدة بدون حفظ

### Memory Modes
- **Off**: لا حفظ
- **Short**: ذاكرة مؤقتة
- **Long**: حفظ طويل الأمد

### Features
- Security Center
- CI/CD
- AI Debugger
- Backup & Restore
- Workflows
- Monitoring

## 🛠️ السكربتات المتاحة

### Backend Scripts

```bash
cd /home/ai/ai-agent/backend

./start.sh      # بدء Backend
./stop.sh       # إيقاف Backend
./restart.sh    # إعادة تشغيل Backend
```

### Frontend Scripts

```bash
cd /home/ai/ai-agent/frontend

./start.sh      # بدء Frontend
./stop.sh       # إيقاف Frontend
./restart.sh    # إعادة تشغيل Frontend
```

## 📡 API Endpoints الرئيسية

### Permissions
- `GET /api/permissions/list` - قائمة الصلاحيات
- `GET /api/permissions/validate?action=...` - التحقق من الصلاحية
- `GET /api/permissions/actions` - Actions المسموحة

### Tools
- `POST /api/tools/read_file` - قراءة ملف
- `POST /api/tools/run_shell` - تنفيذ أمر shell
- `POST /api/tools/service` - فحص خدمة

### Security
- `POST /api/security/scan_repo` - فحص المستودع
- `POST /api/security/scan_infra` - فحص البنية التحتية
- `POST /api/security/scan_network` - فحص الشبكة

### CI/CD
- `POST /api/cicd/deploy/docker-compose` - نشر Docker Compose
- `POST /api/cicd/deploy/kubernetes` - نشر Kubernetes

## 🔧 الإعدادات

### Backend Settings

في `backend/memory/settings.json`:

```json
{
  "agent_mode": "devops",
  "memory_mode": "short",
  "allow_shell": false,
  "allow_read_file": true,
  "require_approval": ["run_shell", "write_file"]
}
```

### Frontend Settings

في `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## ✅ Approval System

النظام يحتوي على نظام موافقات تلقائي:

1. العمليات الخطيرة تحتاج موافقة
2. يتم إنشاء pending action تلقائياً
3. Admin/DevOps يوافقون من Dashboard
4. بعد الموافقة، يتم التنفيذ تلقائياً

## 🔍 Troubleshooting

### Backend لا يعمل

```bash
cd /home/ai/ai-agent/backend
./stop.sh
./start.sh
```

**ملاحظة**: السكربتات تتحقق تلقائياً من Docker containers وتتعامل معها.

### Frontend لا يعمل

```bash
cd /home/ai/ai-agent/frontend
./stop.sh
./start.sh
```

### مشاكل Dependencies

إذا واجهت أخطاء مثل `ModuleNotFoundError`:

```bash
cd /home/ai/ai-agent/backend
python3 -m pip install -r requirements.txt
```

السكربت `start.sh` يتحقق تلقائياً من Dependencies ويقوم بتثبيتها إذا لزم الأمر.

### Port مستخدم

```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Frontend (3000)
lsof -ti:3000 | xargs kill -9
```

### مشاكل الاتصال بين Frontend و Backend

1. تأكد من أن Backend يعمل: `curl http://localhost:8000/health`
2. تأكد من أن Frontend يعمل: `curl http://localhost:3000`
3. تحقق من CORS في Backend (يجب أن يكون `allow_origins=["*"]`)

## 📝 Logs

### Backend Logs
```bash
tail -f /home/ai/ai-agent/backend/backend.log
```

### Frontend Logs
```bash
tail -f /tmp/frontend.log
```

## 🔗 روابط مفيدة

- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health
- **Frontend**: http://localhost:3000

## 📄 الترخيص

هذا المشروع خاص.

## 👥 المساهمون

AI Agent Team

---

**ملاحظة**: تأكد من تشغيل Backend قبل Frontend للحصول على أفضل تجربة.
