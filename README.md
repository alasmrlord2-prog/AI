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

## 📊 مخطط النظام الكامل - Complete System Architecture

```mermaid
graph TB
    subgraph FE["Frontend - Next.js :3000"]
        direction TB
        HOME[Home/Agent Console]
        MONITOR[Monitoring]
        LOGS[Logs]
        TOOLS[Tools]
        CICD[CI/CD]
        DEBUGGER[AI Debugger]
        BACKUP[Backup & Restore]
        WORKFLOWS[Workflows]
        SECURITY[Security Center]
        SIEM[SIEM/SOC]
        THREAT[Threat Detection]
        ABAC[ABAC]
        TENANTS[Tenants]
        BILLING[Billing]
        APPROVALS[Approvals]
        SETTINGS[Settings]
        VISUALIZATION[Visualization]
        KNOWLEDGE[Knowledge Base]
        AUDIT[Audit Trail]
        INCIDENTS[Incidents]
        COST[Cost Analyzer]
        PERFORMANCE[Performance Tuner]
        GLOBAL[Global Search]
        SNAPSHOTS[Snapshots]
        INCIDENT_CENTER[Incident Center]
        SECRETS[Secret Management]
        DEPENDENCY[Service Dependency]
        KERNEL[Kernel Metrics]
        HARDENING[Auto-Hardening]
        SHADOW[Shadow Deployment]
        BEHAVIOR[Behavior Alerts]
        BLUEPRINT[Blueprint Generator]
        CODE_REVIEW[Code Review]
        PLUGINS[Plugin Store]
        WORKFLOW_BUILDER[Workflow Builder]
        AGENT_MESH[Agent Mesh]
        DIGITAL_TWIN[Digital Twin]
    end
    
    subgraph BE["Backend - FastAPI :8000"]
        direction TB
        API[FastAPI Server]
        
        AUTH_API[Auth API]
        CHAT_API[Chat API]
        LOGS_API[Logs API]
        TOOLS_API[Tools API]
        MONITOR_API[Monitor API]
        CICD_API[CI/CD API]
        DEBUGGER_API[Debugger API]
        BACKUP_API[Backup API]
        WORKFLOWS_API[Workflows API]
        SECURITY_API[Security API]
        THREAT_API[Threat Detection API]
        ABAC_API[ABAC API]
        BILLING_API[Billing API]
        APPROVALS_API[Approvals API]
        PERMISSIONS_API[Permissions API]
        SETTINGS_API[Settings API]
        VISUALIZATION_API[Visualization API]
        AUDIT_API[Audit API]
        INCIDENTS_API[Incidents API]
        MONITORING_API[Monitoring API]
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
        
        SECURITY_SVC[Security Service]
        MONITORING_SVC[Monitoring Service]
        BACKUP_SVC[Backup Service]
        WORKFLOW_SVC[Workflow Service]
        INCIDENT_SVC[Incident Service]
        AI_SVC[AI Services]
        
        DB[(SQLite DB)]
        MEMORY[Memory Storage]
        LOGS_STORE[Logs Storage]
    end
    
    subgraph EXT["External Services"]
        OLLAMA[Ollama AI :11434]
        PROMETHEUS[Prometheus :9090]
        GRAFANA[Grafana :3001]
    end
    
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
    
    API --> AUTH_API
    API --> CHAT_API
    API --> LOGS_API
    API --> TOOLS_API
    API --> MONITOR_API
    API --> CICD_API
    API --> DEBUGGER_API
    API --> BACKUP_API
    API --> WORKFLOWS_API
    API --> SECURITY_API
    API --> THREAT_API
    API --> ABAC_API
    API --> BILLING_API
    API --> APPROVALS_API
    API --> PERMISSIONS_API
    API --> SETTINGS_API
    API --> VISUALIZATION_API
    API --> AUDIT_API
    API --> INCIDENTS_API
    API --> MONITORING_API
    API --> COST_API
    API --> PERFORMANCE_API
    API --> GLOBAL_API
    API --> SNAPSHOTS_API
    API --> INCIDENT_CENTER_API
    API --> SECRETS_API
    API --> DEPENDENCY_API
    API --> KERNEL_API
    API --> HARDENING_API
    API --> SHADOW_API
    API --> BEHAVIOR_API
    API --> BLUEPRINT_API
    API --> CODE_REVIEW_API
    API --> PLUGINS_API
    API --> WORKFLOW_BUILDER_API
    API --> AGENT_MESH_API
    API --> DIGITAL_TWIN_API
    
    AUTH_API --> SECURITY_SVC
    CHAT_API --> AI_SVC
    MONITOR_API --> MONITORING_SVC
    SECURITY_API --> SECURITY_SVC
    BACKUP_API --> BACKUP_SVC
    WORKFLOWS_API --> WORKFLOW_SVC
    INCIDENTS_API --> INCIDENT_SVC
    THREAT_API --> SECURITY_SVC
    COST_API --> AI_SVC
    PERFORMANCE_API --> AI_SVC
    
    SECURITY_SVC --> DB
    MONITORING_SVC --> DB
    BACKUP_SVC --> MEMORY
    WORKFLOW_SVC --> DB
    INCIDENT_SVC --> DB
    AI_SVC --> MEMORY
    
    AI_SVC --> OLLAMA
    MONITORING_SVC --> PROMETHEUS
    VISUALIZATION_API --> GRAFANA
    
    style FE fill:#3b82f6,color:#fff
    style BE fill:#10b981,color:#fff
    style EXT fill:#f59e0b,color:#fff
    style DB fill:#8b5cf6,color:#fff
    style MEMORY fill:#8b5cf6,color:#fff
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
