# 🚀 الميزات الجديدة - New Features

تم إضافة الميزات التالية إلى النظام:

## 1. CI/CD داخل الداشبورد

### الميزات:
- ✅ Git Integration - Clone و Pull repositories
- ✅ Pipeline Runner - تشغيل pipelines من `.shiftwave/pipeline.sh`
- ✅ Deploy Engine - Docker Compose, Kubernetes, RSync
- ✅ API Endpoints:
  - `POST /api/cicd/clone` - Clone repository
  - `POST /api/cicd/pull` - Pull latest changes
  - `GET /api/cicd/repos` - List repositories
  - `POST /api/cicd/run` - Run pipeline
  - `GET /api/cicd/status/{pipeline_id}` - Get pipeline status
  - `GET /api/cicd/logs/{pipeline_id}` - Get pipeline logs
  - `POST /api/cicd/rollback/{pipeline_id}` - Rollback pipeline
  - `POST /api/cicd/deploy/docker-compose` - Deploy with Docker Compose
  - `POST /api/cicd/deploy/kubernetes` - Deploy to Kubernetes
  - `POST /api/cicd/deploy/rsync` - Deploy with RSync

### الاستخدام:
```bash
# Clone repository
curl -X POST http://localhost:8000/api/cicd/clone \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo.git", "repo_name": "my-repo"}'

# Run pipeline
curl -X POST http://localhost:8000/api/cicd/run \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "my-repo", "pipeline_script": ".shiftwave/pipeline.sh"}'
```

## 2. AI Debugger

### الميزات:
- ✅ Log Watcher - مراقبة ملفات الـ logs تلقائياً
- ✅ AI Analyzer - تحليل الأخطاء باستخدام LLM (Ollama)
- ✅ Auto Patch - إصلاح تلقائي للأخطاء الآمنة
- ✅ Docker Logs Monitoring
- ✅ Systemd Service Monitoring
- ✅ WebSocket للـ logs المباشرة

### API Endpoints:
- `POST /api/debugger/watch/start` - Start watching logs
- `POST /api/debugger/watch/stop` - Stop watching
- `POST /api/debugger/analyze` - Analyze error
- `GET /api/debugger/errors` - Get recent errors
- `GET /api/debugger/docker/{container_name}` - Check Docker logs
- `GET /api/debugger/service/{service_name}` - Check service status
- `WS /api/debugger/ws/logs` - WebSocket for live logs

## 3. Monitoring + Auto Repair

### الميزات:
- ✅ Health Checks - Services, Containers, Server Metrics
- ✅ Auto Repair Engine - إصلاح تلقائي للخدمات المتوقفة
- ✅ Alert Manager - Telegram + Dashboard alerts
- ✅ Real-time Monitoring

### API Endpoints:
- `GET /api/monitor/service-status/{service_name}` - Check service
- `GET /api/monitor/container-status/{container_name}` - Check container
- `GET /api/monitor/server-metrics` - Get server metrics
- `POST /api/monitor/auto-repair/service/{service_name}` - Auto repair service
- `POST /api/monitor/auto-repair/container/{container_name}` - Auto repair container
- `GET /api/monitor/alerts` - Get alerts
- `POST /api/monitor/alerts/{alert_id}/read` - Mark alert as read

## 4. Workflow Builder

### الميزات:
- ✅ Node-based Workflow System
- ✅ Flow Executor
- ✅ Multiple Node Types: Trigger, Action, Condition, Transform
- ✅ Actions: restart_service, run_shell, send_notification, backup_database

### API Endpoints:
- `POST /api/workflows` - Create workflow
- `GET /api/workflows` - List workflows
- `GET /api/workflows/{workflow_id}` - Get workflow
- `POST /api/workflows/{workflow_id}/execute` - Execute workflow
- `GET /api/workflows/executions` - List executions

### مثال Workflow:
```json
{
  "name": "Auto Restart Service",
  "nodes": [
    {
      "id": "trigger1",
      "type": "trigger",
      "config": {}
    },
    {
      "id": "action1",
      "type": "action",
      "config": {
        "action_type": "restart_service",
        "service_name": "nginx"
      }
    }
  ],
  "edges": [
    {
      "source": "trigger1",
      "target": "action1"
    }
  ]
}
```

## 5. Full Audit Trail

### الميزات:
- ✅ تسجيل كل العمليات: API calls, shell commands, file operations, etc.
- ✅ Database structure مع indexes
- ✅ Filtering: by user, action, date range
- ✅ Export to JSON

### API Endpoints:
- `POST /api/audit/log` - Log an action
- `GET /api/audit/logs` - Get audit logs (with filters)
- `GET /api/audit/export` - Export logs to JSON
- `GET /api/audit/actions` - Get available action types

## 6. Visualization Engine

### الميزات:
- ✅ Network Map - Services, Ports, Links
- ✅ Architecture Graph - Service dependencies
- ✅ Metrics Heatmap - CPU, Memory, Disk, Errors

### API Endpoints:
- `GET /api/visualization/network-map` - Get network map
- `GET /api/visualization/architecture` - Get architecture graph
- `GET /api/visualization/metrics` - Get metrics for heatmap

## 7. Incident Management

### الميزات:
- ✅ Incident Tracking - Create, Update, Resolve
- ✅ Timeline - Track all actions
- ✅ Root Cause Analysis
- ✅ Filtering by status, severity

### API Endpoints:
- `POST /api/incidents` - Create incident
- `GET /api/incidents` - List incidents
- `GET /api/incidents/{incident_id}` - Get incident
- `PUT /api/incidents/{incident_id}` - Update incident
- `POST /api/incidents/{incident_id}/resolve` - Resolve incident

## 8. Backup Manager

### الميزات:
- ✅ Database Backups - PostgreSQL, MySQL
- ✅ Docker Volumes Backup
- ✅ MD5 Verification
- ✅ Backup Management - List, Verify, Delete

### API Endpoints:
- `POST /api/backup/postgresql` - Backup PostgreSQL
- `POST /api/backup/mysql` - Backup MySQL
- `POST /api/backup/docker-volume` - Backup Docker volume
- `GET /api/backup/list` - List backups
- `GET /api/backup/verify/{backup_id}` - Verify backup
- `DELETE /api/backup/{backup_id}` - Delete backup

## 📦 التبعيات الجديدة

تم إضافة المكتبات التالية إلى `requirements.txt`:
- `watchdog` - لمراقبة الملفات
- `docker` - للتعامل مع Docker
- `pyyaml` - لمعالجة ملفات YAML

## 🔧 الإعداد

1. تثبيت التبعيات:
```bash
cd /home/ai/ai-agent/backend
pip install -r requirements.txt
```

2. إنشاء مجلدات البيانات:
```bash
mkdir -p /data/repos
mkdir -p /data/backups
```

3. إعداد Telegram Bot (اختياري):
```bash
# في .env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 📝 ملاحظات

- جميع الـ APIs تتطلب authentication (استثناء `/health`)
- CI/CD repositories تُحفظ في `/data/repos/`
- Backups تُحفظ في `/data/backups/`
- Audit logs تُحفظ في `audit.db`
- Incidents تُحفظ في `incidents.db`

## 🎯 الخطوات التالية

- [ ] إنشاء UI pages للـ Frontend
- [ ] إضافة Workflow Builder UI (React + drag-and-drop)
- [ ] إضافة Audit Trail UI page
- [ ] إضافة Incident Management UI
- [ ] إضافة Backup Scheduler (cron jobs)
- [ ] إضافة Visualization Charts (React components)

