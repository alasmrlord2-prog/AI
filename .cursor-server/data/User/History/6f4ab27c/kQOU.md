# دليل الموديولات الجديدة - New Modules Guide

## نظرة عامة

تم إضافة 5 موديولات أساسية جديدة للنظام، مع إمكانية إضافة المزيد لاحقاً.

---

## 1. Zero-Trust Access Control (ABAC)

### الوصف
نظام صلاحيات متقدم يعتمد على الصفات والظروف بدلاً من الأدوار فقط.

### مثال على الاستخدام

```python
# إنشاء سياسة جديدة
POST /api/abac/policies
{
    "name": "devops_vpn_deploy",
    "description": "DevOps team from VPN can deploy",
    "conditions": {
        "user.team": "devops",
        "environment.is_vpn": True,
        "user.last_login_days": {"$lt": 7}
    },
    "effect": "allow",
    "priority": 10,
    "actions": ["cicd.deploy"],
    "resources": ["*"]
}

# التحقق من الصلاحيات
POST /api/abac/check
{
    "action": "cicd.deploy",
    "resource": "/app",
    "context": {
        "source_ip": "10.0.0.1",
        "is_vpn": True,
        "vpn_ips": ["10.0.0.1"]
    }
}
```

### الصفات المدعومة
- `user.team` - فريق المستخدم
- `user.role` - دور المستخدم
- `user.last_login_days` - عدد الأيام منذ آخر تسجيل دخول
- `environment.source_ip` - IP المصدر
- `environment.is_vpn` - هل الاتصال من VPN
- `environment.time_of_day` - الوقت من اليوم
- `resource.type` - نوع المورد

---

## 2. AI Threat Detection

### الوصف
نظام كشف التهديدات بالذكاء الاصطناعي يراقب الـlogs real-time.

### مثال على الاستخدام

```python
# تحليل logs
POST /api/security/threat-detection/analyze
{
    "log_lines": [
        "2024-01-01 10:00:00 ERROR: SQL injection attempt detected",
        "2024-01-01 10:01:00 WARN: Suspicious activity from IP 192.168.1.100"
    ],
    "source": "application"
}

# ملخص التهديدات
GET /api/security/threat-detection/summary?hours=24
```

### الأنماط المكتشفة
- SQL Injection
- XSS Attacks
- Command Injection
- Path Traversal
- Brute Force
- Privilege Escalation
- Data Exfiltration
- Suspicious Processes

---

## 3. Intelligent Log Timeline

### الوصف
نظام timeline ذكي يربط الأحداث ويحدد السبب الجذري.

### مثال على الاستخدام

```python
# إضافة logs
POST /api/logs/timeline/add
{
    "log_lines": [
        "2024-01-01 10:00:00 INFO: Service started",
        "2024-01-01 10:01:00 ERROR: Connection failed",
        "2024-01-01 10:02:00 ERROR: Timeout occurred"
    ],
    "source": "backend"
}

# عرض timeline
GET /api/logs/timeline/view?hours=24&level=error

# العثور على السبب الجذري
GET /api/logs/timeline/root-cause?event_index=5
```

### الميزات
- ربط الأحداث ذات الصلة تلقائياً
- تحديد السبب الجذري للأخطاء
- تصفية حسب الوقت والمستوى والمصدر
- ملخص الأخطاء

---

## 4. Configuration Drift Detector

### الوصف
كاشف تغييرات الـconfig غير المصرح بها.

### مثال على الاستخدام

```python
# إنشاء snapshot قبل deploy
POST /api/config/drift/snapshot
{
    "path": "/etc/nginx/nginx.conf",
    "deployment_id": "deploy-123"
}

# فحص جميع المسارات
POST /api/config/drift/scan

# استعادة من snapshot
POST /api/config/drift/restore
{
    "path": "/etc/nginx/nginx.conf"
}
```

### المسارات المراقبة افتراضياً
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/`
- `/etc/apache2/`
- `/etc/systemd/system/`
- `/app/config/`
- `/app/.env`
- `/etc/docker/daemon.json`

---

## 5. Infrastructure Cost Analyzer

### الوصف
محلل تكاليف البنية التحتية.

### مثال على الاستخدام

```python
# مقاييس التكلفة الحالية
GET /api/cost/metrics

# ملخص التكاليف
GET /api/cost/summary?hours=24

# كشف الشذوذات
GET /api/cost/anomalies

# توصيات
GET /api/cost/recommendations

# تحليل خدمة محددة
POST /api/cost/service/analyze
{
    "service_name": "backend-api",
    "cpu_usage": 2.5,
    "memory_usage_gb": 4.0
}
```

### المقاييس المحسوبة
- CPU Cost (per core per hour)
- Memory Cost (per GB per hour)
- Storage Cost (per GB per hour)
- Network Cost (per GB transferred)
- Total Cost (hourly, daily, monthly, yearly)

---

## التكامل

### إضافة الموديولات إلى main.py

تم إضافة الموديولات تلقائياً في `app/main.py`:

```python
from app.api.abac import router as abac_router
from app.api.ai_threat_detection import router as threat_detection_router
from app.api.intelligent_log_timeline import router as timeline_router
from app.api.config_drift import router as config_drift_router
from app.api.cost_analyzer import router as cost_analyzer_router

app.include_router(abac_router)
app.include_router(threat_detection_router)
app.include_router(timeline_router)
app.include_router(config_drift_router)
app.include_router(cost_analyzer_router)
```

### الصلاحيات

يمكن إضافة صلاحيات جديدة في `app/core/permissions.py`:

```python
"abac.check": {
    "tools": [],
    "description": "Check ABAC permissions"
},
"security.threat_detection": {
    "tools": ["read_logs"],
    "description": "AI threat detection"
},
"cost.view": {
    "tools": [],
    "description": "View cost metrics"
},
"config.view": {
    "tools": ["read_file"],
    "description": "View configuration"
},
"config.manage": {
    "tools": ["read_file", "write_file"],
    "description": "Manage configuration",
    "requires_approval": True
}
```

---

## الخطوات التالية

1. **اختبار الموديولات**: تأكد من عمل جميع الـendpoints
2. **التكامل مع Frontend**: إضافة واجهات المستخدم
3. **التكوين**: ضبط الإعدادات حسب البيئة
4. **المراقبة**: إضافة alerts وnotifications
5. **التوثيق**: إضافة أمثلة أكثر تفصيلاً

---

## ملاحظات مهمة

- جميع الموديولات تستخدم نظام Permissions الموجود
- جميع الموديولات تستخدم نظام Authentication الموجود
- جميع الموديولات قابلة للتوسع والتخصيص
- يمكن إضافة موديولات جديدة بسهولة

---

## الدعم

للمساعدة أو الاستفسارات، راجع:
- `MODULES.md` - قائمة الموديولات
- `app/core/abac.py` - كود ABAC
- `app/services/` - جميع الـservices
- `app/api/` - جميع الـAPI endpoints

