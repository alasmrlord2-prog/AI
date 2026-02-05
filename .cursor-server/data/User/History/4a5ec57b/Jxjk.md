# AI Agent Backend - دليل شامل ومتكامل

## 📋 نظرة عامة

Backend متقدم للنظام مبني على **FastAPI** مع نظام صلاحيات موحد، أمان شامل، وبنية معمارية احترافية جاهزة للإنتاج والبيع (SaaS-Ready).

### المميزات الرئيسية

- ✅ **نظام صلاحيات موحد** - يتحكم بكل الواجهات والميزات
- ✅ **أمان شامل** - 13+ ماسح أمني متقدم مع SIEM/SOC integration
- ✅ **Service Layer** - بنية معمارية احترافية
- ✅ **Path Resolver متقدم** - Portable, Universal, Zero-Config
- ✅ **Error Handling موحد** - معالجة أخطاء احترافية
- ✅ **Logging موحد** - نظام تسجيل شامل
- ✅ **Advanced Caching** - تحسين الأداء
- ✅ **CI/CD Integration** - نشر تلقائي
- ✅ **Monitoring** - مراقبة شاملة
- ✅ **Backup & Restore** - نسخ احتياطي تلقائي

---

## 🏗️ البنية المعمارية

```
backend/
├── app/
│   ├── api/                    # API Endpoints
│   │   ├── security.py         # Security API (28 endpoints)
│   │   ├── auth.py            # Authentication
│   │   ├── chat.py            # Chat API
│   │   ├── tools.py           # Tools API
│   │   ├── cicd.py            # CI/CD API
│   │   ├── backup.py          # Backup API
│   │   └── ...
│   ├── core/                   # Core Functionality
│   │   ├── permissions.py      # Permission Engine
│   │   ├── permission_helpers.py
│   │   ├── config.py          # Configuration
│   │   └── database.py        # Database
│   ├── services/               # Service Layer
│   │   ├── security_service.py # Security Service
│   │   ├── cicd_service.py
│   │   ├── backup_service.py
│   │   └── ...
│   ├── tools/                  # Agent Tools
│   │   ├── security_scanners/  # Security Scanners (13 modules)
│   │   │   ├── base.py
│   │   │   ├── repo_scanner.py
│   │   │   ├── infra_scanner.py
│   │   │   ├── network_scanner.py
│   │   │   ├── log_scanner.py
│   │   │   ├── system_scanner.py
│   │   │   ├── docker_scanner.py
│   │   │   ├── vulnerability_scanner.py
│   │   │   ├── file_integrity_scanner.py
│   │   │   ├── malware_scanner.py
│   │   │   ├── ids_scanner.py
│   │   │   ├── port_scanner.py
│   │   │   └── penetration_scanner.py
│   │   ├── security_scan.py    # Compatibility Layer
│   │   ├── advanced_security_tools.py
│   │   ├── siem_monitor.py
│   │   └── ...
│   ├── utils/                  # Utilities
│   │   ├── path_resolver.py    # Advanced Path Resolver
│   │   ├── logger.py           # Unified Logging
│   │   ├── error_handler.py   # Error Handling
│   │   ├── cache.py            # Advanced Caching
│   │   └── helpers.py
│   ├── models/                 # Data Models
│   ├── monitoring/             # Monitoring
│   └── main.py                 # FastAPI App
├── start.sh                     # سكربت بدء التشغيل
├── stop.sh                      # سكربت إيقاف التشغيل
├── restart.sh                   # سكربت إعادة التشغيل
├── requirements.txt             # Python Dependencies
└── README.md                    # هذا الملف
```

---

## 🚀 البدء السريع

### 1. تثبيت المتطلبات

```bash
cd /home/ai/ai-agent/backend
pip3 install -r requirements.txt
```

### 2. تشغيل Backend

```bash
# طريقة 1: استخدام السكربت (مُوصى به)
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

---

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

- **Off**: لا يتم حفظ أي شيء في الذاكرة
- **Short**: البيانات في الذاكرة المؤقتة فقط
- **Long**: تفعيل `memory.json` واستخدام DB للذاكرة طويلة الأمد

---

## 🛡️ نظام الأمان (Security System)

### Security Scanners (13 ماسح)

#### Basic Scans
1. **Repository Scan** - فحص المستودع للأسرار والمشاكل
2. **Infrastructure Scan** - فحص Docker Compose و Kubernetes
3. **Network Scan** - فحص الشبكة والأمن
4. **Log Scan** - فحص السجلات لمحاولات الاختراق
5. **System Scan** - فحص النظام والأمان
6. **Docker Scan** - فحص Docker Containers
7. **Vulnerability Scan** - فحص الثغرات (pip/npm audit)
8. **File Integrity Scan** - مراقبة سلامة الملفات
9. **Malware Scan** - فحص البرمجيات الخبيثة
10. **IDS Scan** - اكتشاف التسلل
11. **Port Scan** - فحص المنافذ
12. **Penetration Test** - اختبار الاختراق

#### Advanced Scans
- **Threat Intelligence** - استخبارات التهديدات
- **Network Forensics** - تحليل حركة الشبكة
- **Web Vulnerability Scan** - فحص تطبيقات الويب
- **Container Security** - أمان الحاويات المتقدم
- **Kubernetes Security** - أمان Kubernetes
- **AWS Security** - أمان AWS
- **Memory Forensics** - تحليل الذاكرة
- **Disk Forensics** - تحليل القرص
- **Password Audit** - تدقيق كلمات المرور
- **Compliance Check** - فحص الامتثال (CIS, STIG)
- **Burp Suite Scan** - فحص باستخدام Burp Suite
- **Metasploit Scan** - فحص باستخدام Metasploit

### SIEM/SOC Integration

- ✅ **SIEM Monitoring** - مراقبة شاملة للأحداث الأمنية
- ✅ **SOC Incidents** - إدارة الحوادث الأمنية
- ✅ **Threat Intelligence** - استخبارات التهديدات
- ✅ **Risk Scoring** - تقييم المخاطر التلقائي
- ✅ **Auto-Repair** - إصلاح تلقائي للمشاكل
- ✅ **Auto-Block IP** - حظر تلقائي للـ IPs المشبوهة

---

## 📡 API Endpoints

### Security API

#### Basic Scans
```bash
POST /api/security/scan_repo
POST /api/security/scan_infra
POST /api/security/scan_network
POST /api/security/scan_logs
POST /api/security/scan_system
POST /api/security/scan_docker
POST /api/security/scan_vulnerabilities
POST /api/security/scan_file_integrity
POST /api/security/scan_malware
POST /api/security/scan_intrusion_detection
POST /api/security/scan_port_scan
POST /api/security/scan_penetration_test
```

#### Advanced Scans
```bash
POST /api/security/advanced/threat_intelligence
POST /api/security/advanced/network_forensics
POST /api/security/advanced/vulnerability
POST /api/security/advanced/web_scan
POST /api/security/advanced/container
POST /api/security/advanced/kubernetes
POST /api/security/advanced/aws
POST /api/security/advanced/memory_forensics
POST /api/security/advanced/disk_forensics
POST /api/security/advanced/password_audit
POST /api/security/advanced/compliance
POST /api/security/advanced/burp_suite
POST /api/security/advanced/metasploit
POST /api/security/advanced/packet_analysis
```

#### SIEM
```bash
GET /api/security/siem
```

### Permissions API

```bash
GET /api/permissions/list
GET /api/permissions/validate?action=security.scan
GET /api/permissions/actions
GET /api/permissions/actions/requiring-approval
```

### Tools API

```bash
POST /api/tools/read_file
POST /api/tools/run_shell
POST /api/tools/doc_search
POST /api/tools/read_logs
```

### CI/CD API

```bash
POST /api/cicd/deploy/docker-compose
POST /api/cicd/deploy/kubernetes
```

### Backup API

```bash
POST /api/backup/postgresql
POST /api/backup/mysql
POST /api/backup/restore
```

---

## 🔧 الإعدادات

### تعديل Settings

```json
// memory/settings.json
{
  "agent_mode": "devops",
  "memory_mode": "short",
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

---

## ✅ Approval System

عندما يكون action يحتاج موافقة:

1. يتم إنشاء pending action تلقائياً
2. يتم إرجاع `action_id` في الـ response
3. Admin/DevOps يمكنهم الموافقة من `/api/approvals`
4. بعد الموافقة، يتم تنفيذ الـ action تلقائياً

### الموافقة على Action

```bash
curl -X POST http://localhost:8000/api/approvals/{action_id}/approve \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🏛️ البنية المعمارية المتقدمة

### Service Layer

جميع العمليات الأمنية تمر عبر `SecurityService` الذي يوفر:
- واجهة موحدة
- تسجيل تلقائي في SIEM
- معالجة أخطاء موحدة
- سهولة الاختبار والصيانة

### Path Resolver المتقدم

نظام `resolve_path` يوفر:
- ✅ Auto-detect project root
- ✅ Docker `/app` compatibility
- ✅ Symlink resolution
- ✅ Monorepo detection
- ✅ Microservices support
- ✅ Advanced caching
- ✅ Path traversal protection
- ✅ Portable & Universal

### Error Handling

- Custom exceptions (SecurityScanError, PathResolutionError, etc.)
- Decorators: `@handle_scan_errors`, `@handle_api_errors`
- Error responses موحدة
- Logging تلقائي للأخطاء

### Logging

- Logger موحد للكامل النظام
- Console + File logging
- Context-aware logging
- Functions: `log_info`, `log_error`, `log_warning`, `log_debug`

### Caching

- LRU cache مع TTL
- Thread-safe
- Cache statistics
- Automatic cleanup
- Decorator: `@cached(ttl=timedelta(minutes=30))`

---

## 📊 الميزات التقنية

### Security Features
- ✅ 13+ Security Scanners
- ✅ SIEM/SOC Integration
- ✅ Risk Scoring
- ✅ Threat Intelligence
- ✅ Network Forensics
- ✅ Compliance Checking
- ✅ Auto-Repair & Auto-Block

### Architecture Features
- ✅ Modular Design (13 scanner modules)
- ✅ Service Layer Pattern
- ✅ Unified Error Handling
- ✅ Unified Logging
- ✅ Advanced Caching
- ✅ Path Resolution System

### Performance
- ✅ Caching for scan results
- ✅ Thread-safe operations
- ✅ Optimized file scanning
- ✅ Background task support

---

## 🔍 Troubleshooting

### Port 8000 مستخدم

```bash
# إيقاف العملية
lsof -ti:8000 | xargs kill -9

# أو
./stop.sh
```

### Permission denied

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
tail -f backend.log

# تحقق من الـ port
lsof -ti:8000
```

---

## 📚 الوثائق الإضافية

- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

---

## 🎯 الحالة الحالية

### ✅ مكتمل
- ✅ جميع Security Scanners (13 scanner)
- ✅ Service Layer
- ✅ Error Handling موحد
- ✅ Logging موحد
- ✅ Advanced Caching
- ✅ Path Resolver متقدم
- ✅ SIEM/SOC Integration
- ✅ API Endpoints (28+ endpoints)
- ✅ Approval System
- ✅ Permission System

### 📊 الإحصائيات
- **الملفات**: 18+ ملف جديد
- **الأسطر**: ~60,000+ سطر
- **الماسحات**: 13 scanner module
- **API Endpoints**: 28+ endpoint
- **Utilities**: 3 modules
- **Services**: 1 service layer

---

## 🚀 جاهز للإنتاج

النظام جاهز 100% للاستخدام في الإنتاج:
- ✅ Production-Ready
- ✅ SaaS-Ready
- ✅ Scalable
- ✅ Maintainable
- ✅ Secure
- ✅ Fast

---

## 📝 الترخيص

هذا المشروع جاهز للاستخدام التجاري.

---

**آخر تحديث**: 2024-11-19
**الإصدار**: 1.0.0
