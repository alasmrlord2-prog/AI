# 🔄 تعليمات إعادة التشغيل - Restart Instructions

## لإظهار الميزات الجديدة في الداشبورد:

### 1. تثبيت التبعيات الجديدة (إذا لم تكن مثبتة):
```bash
cd /home/ai/ai-agent/backend
pip install watchdog docker pyyaml
```

### 2. إعادة تشغيل Backend:
```bash
cd /home/ai/ai-agent/backend
./restart_backend.sh
```

أو يدوياً:
```bash
cd /home/ai/ai-agent/backend
./stop_backend.sh
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. التحقق من أن الـ APIs تعمل:
```bash
# تحقق من Swagger UI
curl http://localhost:8000/docs

# أو تحقق من endpoint معين
curl http://localhost:8000/api/cicd/repos
```

### 4. الميزات الجديدة المتاحة:

#### CI/CD:
- `/api/cicd/clone` - Clone repository
- `/api/cicd/run` - Run pipeline
- `/api/cicd/status/{pipeline_id}` - Get pipeline status
- `/api/cicd/logs/{pipeline_id}` - Get pipeline logs

#### AI Debugger:
- `/api/debugger/watch/start` - Start watching logs
- `/api/debugger/analyze` - Analyze error
- `/api/debugger/errors` - Get recent errors

#### Monitoring:
- `/api/monitor/service-status/{service_name}` - Check service
- `/api/monitor/container-status/{container_name}` - Check container
- `/api/monitor/server-metrics` - Get server metrics
- `/api/monitor/auto-repair/service/{service_name}` - Auto repair

#### Audit Trail:
- `/api/audit/logs` - Get audit logs
- `/api/audit/export` - Export logs

#### Backup:
- `/api/backup/postgresql` - Backup PostgreSQL
- `/api/backup/mysql` - Backup MySQL
- `/api/backup/docker-volume` - Backup Docker volume
- `/api/backup/list` - List backups

#### Incidents:
- `/api/incidents` - List/create incidents
- `/api/incidents/{incident_id}` - Get/update incident

#### Workflows:
- `/api/workflows` - List/create workflows
- `/api/workflows/{workflow_id}/execute` - Execute workflow

#### Visualization:
- `/api/visualization/network-map` - Get network map
- `/api/visualization/architecture` - Get architecture
- `/api/visualization/metrics` - Get metrics

### 5. عرض جميع الـ APIs:
افتح المتصفح واذهب إلى:
```
http://localhost:8000/docs
```

ستجد جميع الـ endpoints الجديدة في Swagger UI.

### 6. إنشاء مجلدات البيانات (إذا لم تكن موجودة):
```bash
sudo mkdir -p /data/repos /data/backups
sudo chown -R $USER:$USER /data/repos /data/backups
```

### ملاحظات:
- جميع الـ APIs تتطلب authentication (استثناء `/health`)
- يمكنك استخدام Swagger UI (`/docs`) لاختبار الـ APIs
- الـ logs ستظهر في console عند تشغيل Backend

