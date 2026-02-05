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
│   └── restart.sh       # إعادة تشغيل Backend
├── frontend/            # Next.js Frontend
│   ├── app/            # Next.js App
│   ├── start.sh        # بدء Frontend
│   ├── stop.sh         # إيقاف Frontend
│   └── restart.sh      # إعادة تشغيل Frontend
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

## 📊 مخطط النظام الكامل

```mermaid
graph TB
    subgraph "Frontend - Next.js"
        UI[واجهة المستخدم]
        
        subgraph "الصفحات الرئيسية"
            HOME[الصفحة الرئيسية<br/>Agent Console]
            MONITOR[Monitoring<br/>مراقبة النظام]
            LOGS[Logs<br/>السجلات]
            TOOLS[Tools<br/>الأدوات]
        end
        
        subgraph "ميزات DevOps"
            CICD[CI/CD<br/>النشر التلقائي]
            DEBUGGER[AI Debugger<br/>مصحح الأخطاء]
            BACKUP[Backup & Restore<br/>النسخ الاحتياطي]
            WORKFLOWS[Workflows<br/>سير العمل]
        end
        
        subgraph "ميزات الأمان"
            SECURITY[Security Center<br/>مركز الأمان]
            SIEM[SIEM/SOC<br/>مراقبة الأمان]
            THREAT[Threat Detection<br/>كشف التهديدات]
            ABAC[ABAC Access Control<br/>التحكم بالوصول]
        end
        
        subgraph "ميزات الإدارة"
            TENANTS[Tenants<br/>المواقع]
            BILLING[Billing<br/>الفواتير]
            APPROVALS[Approvals<br/>الموافقات]
            SETTINGS[Settings<br/>الإعدادات]
        end
        
        subgraph "ميزات متقدمة"
            VISUALIZATION[Visualization<br/>التصور]
            KNOWLEDGE[Knowledge Base<br/>قاعدة المعرفة]
            AUDIT[Audit Trail<br/>سجل التدقيق]
            INCIDENTS[Incidents<br/>الحوادث]
        end
        
        subgraph "ميزات AI المتقدمة"
            COST[Cost Analyzer<br/>تحليل التكاليف]
            PERFORMANCE[Performance Tuner<br/>ضبط الأداء]
            GLOBAL[Global Search<br/>البحث الشامل]
            SNAPSHOTS[Snapshots & Rollback<br/>اللقطات]
            INCIDENT_CENTER[Incident Command Center<br/>مركز قيادة الحوادث]
            SECRETS[Secret Management<br/>إدارة الأسرار]
            DEPENDENCY[Service Dependency<br/>تبعيات الخدمات]
            KERNEL[Kernel Metrics<br/>مقاييس النواة]
            HARDENING[Auto-Hardening<br/>التأمين التلقائي]
            SHADOW[Shadow Deployment<br/>النشر الخفي]
            BEHAVIOR[Behavior Alerts<br/>تنبيهات السلوك]
            BLUEPRINT[Blueprint Generator<br/>مولد المخططات]
            CODE_REVIEW[Code Review<br/>مراجعة الكود]
            PLUGINS[Plugin Store<br/>متجر الإضافات]
            WORKFLOW_BUILDER[Workflow Builder<br/>بناء سير العمل]
            AGENT_MESH[Agent Mesh<br/>شبكة الوكلاء]
            DIGITAL_TWIN[Digital Twin<br/>التوأم الرقمي]
        end
    end
    
    subgraph "Backend - FastAPI"
        API[FastAPI Server<br/>Port 8000]
        
        subgraph "Core APIs"
            AUTH_API[Auth API<br/>المصادقة]
            CHAT_API[Chat API<br/>المحادثة]
            LOGS_API[Logs API<br/>السجلات]
            TOOLS_API[Tools API<br/>الأدوات]
            MONITOR_API[Monitor API<br/>المراقبة]
        end
        
        subgraph "DevOps APIs"
            CICD_API[CI/CD API<br/>النشر]
            DEBUGGER_API[Debugger API<br/>المصحح]
            BACKUP_API[Backup API<br/>النسخ]
            WORKFLOWS_API[Workflows API<br/>سير العمل]
        end
        
        subgraph "Security APIs"
            SECURITY_API[Security API<br/>الأمان]
            THREAT_API[Threat Detection API<br/>كشف التهديدات]
            ABAC_API[ABAC API<br/>التحكم]
        end
        
        subgraph "Management APIs"
            BILLING_API[Billing API<br/>الفواتير]
            APPROVALS_API[Approvals API<br/>الموافقات]
            PERMISSIONS_API[Permissions API<br/>الصلاحيات]
            SETTINGS_API[Settings API<br/>الإعدادات]
        end
        
        subgraph "Advanced APIs"
            VISUALIZATION_API[Visualization API<br/>التصور]
            AUDIT_API[Audit API<br/>التدقيق]
            INCIDENTS_API[Incidents API<br/>الحوادث]
            MONITORING_API[Monitoring API<br/>المراقبة المتقدمة]
        end
        
        subgraph "AI Advanced APIs"
            COST_API[Cost Analyzer API]
            PERFORMANCE_API[Performance Tuner API]
            GLOBAL_API[Global Search API]
            SNAPSHOTS_API[Snapshots API]
            INCIDENT_CENTER_API[Incident Center API]
            SECRETS_API[Secrets API]
            DEPENDENCY_API[Dependency API]
            KERNEL_API[Kernel Metrics API]
            HARDENING_API[Hardening API]
            SHADOW_API[Shadow Deployment API]
            BEHAVIOR_API[Behavior Alerts API]
            BLUEPRINT_API[Blueprint API]
            CODE_REVIEW_API[Code Review API]
            PLUGINS_API[Plugins API]
            WORKFLOW_BUILDER_API[Workflow Builder API]
            AGENT_MESH_API[Agent Mesh API]
            DIGITAL_TWIN_API[Digital Twin API]
        end
        
        subgraph "Services Layer"
            SECURITY_SERVICE[Security Service]
            MONITORING_SERVICE[Monitoring Service]
            BACKUP_SERVICE[Backup Service]
            WORKFLOW_SERVICE[Workflow Service]
            INCIDENT_SERVICE[Incident Service]
            AI_SERVICES[AI Services<br/>Ollama Integration]
        end
        
        subgraph "Data Layer"
            DB[(SQLite Database)]
            MEMORY[Memory Storage]
            LOGS_STORAGE[Logs Storage]
        end
    end
    
    subgraph "External Services"
        OLLAMA[Ollama<br/>Local AI]
        PROMETHEUS[Prometheus<br/>Metrics]
        GRAFANA[Grafana<br/>Visualization]
    end
    
    %% Frontend Connections
    HOME --> API
    MONITOR --> API
    LOGS --> API
    TOOLS --> API
    CICD --> API
    DEBUGGER --> API
    BACKUP --> API
    WORKFLOWS --> API
    SECURITY --> API
    SIEM --> API
    THREAT --> API
    ABAC --> API
    TENANTS --> API
    BILLING --> API
    APPROVALS --> API
    SETTINGS --> API
    VISUALIZATION --> API
    KNOWLEDGE --> API
    AUDIT --> API
    INCIDENTS --> API
    COST --> API
    PERFORMANCE --> API
    GLOBAL --> API
    SNAPSHOTS --> API
    INCIDENT_CENTER --> API
    SECRETS --> API
    DEPENDENCY --> API
    KERNEL --> API
    HARDENING --> API
    SHADOW --> API
    BEHAVIOR --> API
    BLUEPRINT --> API
    CODE_REVIEW --> API
    PLUGINS --> API
    WORKFLOW_BUILDER --> API
    AGENT_MESH --> API
    DIGITAL_TWIN --> API
    
    %% Backend API to Service Connections
    AUTH_API --> SECURITY_SERVICE
    CHAT_API --> AI_SERVICES
    MONITOR_API --> MONITORING_SERVICE
    SECURITY_API --> SECURITY_SERVICE
    BACKUP_API --> BACKUP_SERVICE
    WORKFLOWS_API --> WORKFLOW_SERVICE
    INCIDENTS_API --> INCIDENT_SERVICE
    THREAT_API --> SECURITY_SERVICE
    COST_API --> AI_SERVICES
    PERFORMANCE_API --> AI_SERVICES
    
    %% Services to Data Layer
    SECURITY_SERVICE --> DB
    MONITORING_SERVICE --> DB
    BACKUP_SERVICE --> MEMORY
    WORKFLOW_SERVICE --> DB
    INCIDENT_SERVICE --> DB
    AI_SERVICES --> MEMORY
    
    %% External Services
    AI_SERVICES --> OLLAMA
    MONITORING_SERVICE --> PROMETHEUS
    VISUALIZATION_API --> GRAFANA
    
    style UI fill:#3b82f6
    style API fill:#10b981
    style OLLAMA fill:#f59e0b
    style DB fill:#8b5cf6
```

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

### Core APIs
- `GET /health` - فحص حالة النظام
- `POST /api/auth/login` - تسجيل الدخول
- `POST /api/chat` - محادثة مع AI Agent
- `GET /api/logs` - الحصول على السجلات
- `GET /api/monitor` - مراقبة النظام

### DevOps APIs
- `POST /api/cicd/deploy` - نشر التطبيقات
- `POST /api/debugger/analyze` - تحليل الأخطاء
- `POST /api/backup/create` - إنشاء نسخة احتياطية
- `POST /api/workflows/execute` - تنفيذ سير العمل

### Security APIs
- `POST /api/security/scan` - فحص الأمان
- `GET /api/threat-detection/alerts` - تنبيهات التهديدات
- `GET /api/abac/validate` - التحقق من الصلاحيات

### Management APIs
- `GET /api/billing/invoices` - الفواتير
- `POST /api/approvals/request` - طلب موافقة
- `GET /api/permissions/list` - قائمة الصلاحيات

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

## 📊 الميزات المتاحة

### Core Features
- ✅ Agent Console - واجهة المحادثة مع AI
- ✅ Monitoring - مراقبة النظام
- ✅ Logs - إدارة السجلات
- ✅ Tools - أدوات النظام

### DevOps Features
- ✅ CI/CD - النشر التلقائي
- ✅ AI Debugger - مصحح الأخطاء بالذكاء الاصطناعي
- ✅ Backup & Restore - النسخ الاحتياطي
- ✅ Workflows - إدارة سير العمل

### Security Features
- ✅ Security Center - مركز الأمان
- ✅ SIEM/SOC - مراقبة الأمان
- ✅ Threat Detection - كشف التهديدات
- ✅ ABAC - التحكم بالوصول المتقدم

### Management Features
- ✅ Tenants - إدارة المواقع
- ✅ Billing - إدارة الفواتير
- ✅ Approvals - نظام الموافقات
- ✅ Settings - الإعدادات

### Advanced Features
- ✅ Visualization - تصور البيانات
- ✅ Knowledge Base - قاعدة المعرفة
- ✅ Audit Trail - سجل التدقيق
- ✅ Incidents - إدارة الحوادث

### AI Advanced Features
- ✅ Cost Analyzer - تحليل التكاليف
- ✅ Performance Tuner - ضبط الأداء
- ✅ Global Search - البحث الشامل
- ✅ Snapshots & Rollback - اللقطات والتراجع
- ✅ Incident Command Center - مركز قيادة الحوادث
- ✅ Secret Management - إدارة الأسرار
- ✅ Service Dependency - تبعيات الخدمات
- ✅ Kernel Metrics - مقاييس النواة
- ✅ Auto-Hardening - التأمين التلقائي
- ✅ Shadow Deployment - النشر الخفي
- ✅ Behavior Alerts - تنبيهات السلوك
- ✅ Blueprint Generator - مولد المخططات
- ✅ Code Review - مراجعة الكود
- ✅ Plugin Store - متجر الإضافات
- ✅ Workflow Builder - بناء سير العمل
- ✅ Agent Mesh - شبكة الوكلاء
- ✅ Digital Twin - التوأم الرقمي

## 📄 الترخيص

هذا المشروع خاص.

## 👥 المساهمون

AI Agent Team

---

**ملاحظة**: تأكد من تشغيل Backend قبل Frontend للحصول على أفضل تجربة.
