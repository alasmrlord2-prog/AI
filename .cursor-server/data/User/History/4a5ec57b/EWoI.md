# AI Agent Backend - دليل شامل

## 📋 نظرة عامة

Backend للنظام مبني على **FastAPI** مع نظام صلاحيات موحد يتحكم بكل الواجهات والميزات.

## 🏗️ البنية

```
backend/
├── app/
│   ├── core/
│   │   ├── permissions.py          # Permission Engine المركزي
│   │   ├── permission_helpers.py   # Helper functions للصلاحيات
│   │   └── config.py               # إعدادات التطبيق
│   ├── api/
│   │   ├── permissions.py           # API endpoints للصلاحيات
│   │   ├── tools.py                 # Tools API
│   │   ├── security.py             # Security API
│   │   ├── cicd.py                 # CI/CD API
│   │   ├── debugger.py             # AI Debugger API
│   │   ├── backup.py               # Backup API
│   │   └── workflows.py            # Workflows API
│   ├── models/
│   │   └── settings.py             # Settings Model
│   ├── tools/                      # Agent Tools
│   └── main.py                     # FastAPI App
├── start.sh                        # سكربت بدء التشغيل
├── stop.sh                         # سكربت إيقاف التشغيل
└── restart.sh                      # سكربت إعادة التشغيل
```

## 🚀 البدء السريع

### 1. تثبيت المتطلبات

```bash
cd /home/ai/ai-agent/backend
pip3 install -r requirements.txt
```

### 2. تشغيل Backend

```bash
# طريقة 1: استخدام السكربت
./start.sh

# طريقة 2: يدوياً
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. إيقاف Backend

```bash
./stop.sh
```

### 4. إعادة تشغيل Backend

```bash
./restart.sh
```

## 🔐 نظام الصلاحيات (Permission System)

### Agent Modes

#### 1. Safe Mode (آمن)
- **يسمح**: `read_file`, `doc_search`, `read_logs`
- **يمنع**: `run_shell`, `write_file`, `restart_service`
- **الاستخدام**: للبيئات الآمنة، قراءة فقط

#### 2. DevOps Mode (افتراضي)
- **يسمح**: كل الأدوات
- **يتطلب Approval**: `run_shell`, `write_file`, `restart_service`, `backup.restore`, `cicd.deploy`
- **الاستخدام**: للبيئات التطويرية والإنتاجية

#### 3. Root Mode (خطير)
- **يسمح**: كل الأدوات بدون أي قيود
- **بدون Approval**: كل العمليات تنفذ مباشرة
- **الاستخدام**: للمسؤولين فقط

#### 4. Short Mode (جلسة واحدة)
- **الذاكرة**: لا يتم حفظ أي شيء بعد انتهاء الجلسة
- **الاستخدام**: للاختبارات والجلسات المؤقتة

### Memory Modes

#### Off
- لا يتم حفظ أي شيء في الذاكرة
- `memory.json` و `long_memory.json` معطلان

#### Short
- البيانات في الذاكرة المؤقتة فقط
- لا يتم حفظ على القرص
- يتم إعادة التعيين عند كل refresh

#### Long
- تفعيل `memory.json`
- استخدام DB للذاكرة طويلة الأمد
- استرجاع السياق القديم تلقائياً

### Tool Permissions

```python
# في Settings
allow_shell: bool = False          # يتحكم بـ run_shell
allow_read_file: bool = True        # يتحكم بـ read_file
allow_doc_search: bool = True       # يتحكم بـ doc_search
allow_logs: bool = True            # يتحكم بـ read_logs
```

## 📡 API Endpoints

### Permissions API

#### GET `/api/permissions/list`
قائمة بكل الصلاحيات وحالتها

```bash
curl http://localhost:8000/api/permissions/list
```

#### GET `/api/permissions/validate?action=security.scan`
التحقق من صلاحية action معينة

```bash
curl "http://localhost:8000/api/permissions/validate?action=security.scan"
```

#### GET `/api/permissions/actions`
قائمة بكل Actions المسموحة

```bash
curl http://localhost:8000/api/permissions/actions
```

#### GET `/api/permissions/actions/requiring-approval`
قائمة بكل Actions التي تحتاج موافقة

```bash
curl http://localhost:8000/api/permissions/actions/requiring-approval
```

### Tools API

#### POST `/api/tools/read_file`
قراءة ملف

```bash
curl -X POST http://localhost:8000/api/tools/read_file \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"path": "/path/to/file"}'
```

#### POST `/api/tools/run_shell`
تنفيذ أمر shell (يتطلب approval في DevOps mode)

```bash
curl -X POST http://localhost:8000/api/tools/run_shell \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"cmd": "ls -la"}'
```

### Security API

#### POST `/api/security/scan_repo`
فحص المستودع

#### POST `/api/security/scan_infra`
فحص البنية التحتية

#### POST `/api/security/scan_network`
فحص الشبكة

### CI/CD API

#### POST `/api/cicd/deploy/docker-compose`
نشر باستخدام Docker Compose

#### POST `/api/cicd/deploy/kubernetes`
نشر على Kubernetes

### Backup API

#### POST `/api/backup/postgresql`
نسخ احتياطي لـ PostgreSQL

#### POST `/api/backup/mysql`
نسخ احتياطي لـ MySQL

## 🔧 الإعدادات

### تعديل Settings

```python
# في memory/settings.json
{
  "agent_mode": "devops",           # safe, devops, root, short
  "memory_mode": "short",           # off, short, long
  "allow_shell": false,
  "allow_read_file": true,
  "allow_doc_search": true,
  "allow_logs": true,
  "require_approval": [
    "run_shell",
    "write_file",
    "restart_service",
    "backup.restore",
    "cicd.deploy"
  ]
}
```

### تعديل Settings عبر API

```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "agent_mode": "devops",
    "allow_shell": true
  }'
```

## ✅ Approval System

عندما يكون action يحتاج موافقة:

1. يتم إنشاء pending action تلقائياً
2. يتم إرجاع `action_id` في الـ response
3. Admin/DevOps يمكنهم الموافقة من `/api/pending-actions`
4. بعد الموافقة، يتم تنفيذ الـ action تلقائياً

### الموافقة على Action

```bash
curl -X POST http://localhost:8000/api/pending-actions/{action_id}/approve \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### رفض Action

```bash
curl -X POST http://localhost:8000/api/pending-actions/{action_id}/reject \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"reason": "Not safe"}'
```

## 🛠️ استخدام Permission Engine في الكود

### في API Endpoints

```python
from app.core.permission_helpers import check_action_permission

@router.post("/my-endpoint")
async def my_endpoint(current_user: dict = Depends(get_current_user)):
    # التحقق من الصلاحية
    check_action_permission("security.scan", current_user, resource="/path")
    
    # تنفيذ العملية...
    return {"status": "success"}
```

### في Tools

```python
from app.core.permission_helpers import check_tool_permission

def my_tool():
    check_tool_permission("run_shell", current_user)
    # تنفيذ الأمر...
```

## 📝 Logs

```bash
# عرض logs
tail -f /tmp/backend.log

# أو
tail -f backend.log
```

## 🔍 Troubleshooting

### Port 8000 مستخدم

```bash
# إيقاف العملية
lsof -ti:8000 | xargs kill -9

# أو
./stop.sh
```

### Permission denied للـ pending_actions.json

```bash
chmod 666 memory/pending_actions.json
# أو
sudo chmod 777 memory/
```

### Backend لا يبدأ

```bash
# تحقق من المتطلبات
pip3 install -r requirements.txt

# تحقق من الـ logs
tail -f /tmp/backend.log

# تحقق من الـ port
lsof -ti:8000
```

## 📚 المزيد من المعلومات

- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 🔗 روابط مهمة

- [Permission System Documentation](../PERMISSIONS_SYSTEM.md)
- [Frontend README](../frontend/README.md)
- [Project README](../README.md)

