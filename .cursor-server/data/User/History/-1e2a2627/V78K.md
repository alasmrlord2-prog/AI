# 📁 بنية المشروع الكاملة - SHIFTWAVE AI Platform

## 🏗️ البنية العامة

```
ai-agent/
├── 📄 README.md                    # الوثائق الرئيسية
├── 📄 SERVICES_TOOLS.md            # جميع السيرفس مع الأدوات والكود
├── 📄 PROJECT_STRUCTURE.md         # هذا الملف - بنية المشروع
├── 📄 docker-compose.yml           # إعدادات Docker
├── 📄 ecosystem.config.js          # إعدادات PM2 (اختياري)
├── 📄 SCRIPTS.md                   # دليل السكربتات
│
├── 📄 backend-start.sh             # Start Backend Script
├── 📄 backend-stop.sh              # Stop Backend Script
├── 📄 backend-restart.sh           # Restart Backend Script
├── 📄 frontend-start.sh            # Start Frontend Script
├── 📄 frontend-stop.sh             # Stop Frontend Script
├── 📄 frontend-restart.sh          # Restart Frontend Script
├── 📄 start-all.sh                 # Start All Services
├── 📄 stop-all.sh                  # Stop All Services
├── 📄 restart-all.sh               # Restart All Services
├── 📄 clean-containers.sh          # Clean Containers Script
├── 📄 fix-all.sh                   # Fix All Issues Script
│
├── 📂 backend/                     # Backend - FastAPI (port 8000)
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 alembic.ini              # Database migrations
│   ├── 📄 pytest.ini               # Test configuration
│   ├── 📄 env.example              # Environment variables example
│   │
│   ├── 📂 app/                     # الكود الرئيسي للتطبيق
│   │   ├── 📄 main.py              # نقطة البداية - FastAPI app
│   │   ├── 📄 auth.py              # Authentication
│   │   ├── 📄 pending_actions.py   # الإجراءات المعلقة
│   │   │
│   │   ├── 📂 api/                 # API Endpoints
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 agent.py         # AI Agent API
│   │   │   ├── 📄 auth.py          # Authentication API
│   │   │   ├── 📄 chat.py          # Chat API
│   │   │   ├── 📄 websocket.py     # WebSocket API
│   │   │   ├── 📄 capabilities.py  # Capabilities API
│   │   │   ├── 📄 tools.py         # Tools API
│   │   │   ├── 📄 workflows.py     # Workflows API
│   │   │   ├── 📄 security.py      # Security API
│   │   │   ├── 📄 monitoring.py    # Monitoring API
│   │   │   ├── 📄 logs.py          # Logs API
│   │   │   ├── 📄 incidents.py     # Incidents API
│   │   │   ├── 📄 audit.py         # Audit API
│   │   │   ├── 📄 backup.py        # Backup API
│   │   │   ├── 📄 cicd.py          # CI/CD API
│   │   │   ├── 📄 billing.py       # Billing API
│   │   │   ├── 📄 crm_api.py       # CRM API
│   │   │   ├── 📄 identity_api.py  # Identity API
│   │   │   ├── 📄 access_api.py    # Access API
│   │   │   ├── 📄 policy_api.py     # Policy API
│   │   │   ├── 📄 abac.py          # ABAC API
│   │   │   ├── 📄 permissions.py   # Permissions API
│   │   │   ├── 📄 settings.py      # Settings API
│   │   │   ├── 📄 subscription_api.py # Subscription API
│   │   │   ├── 📄 knowledge.py     # Knowledge API
│   │   │   ├── 📄 digital_twin.py  # Digital Twin API
│   │   │   ├── 📄 snapshot_rollback.py # Snapshot API
│   │   │   ├── 📄 shadow_deployment.py # Shadow Deployment API
│   │   │   ├── 📄 config_drift.py  # Config Drift API
│   │   │   ├── 📄 cost_analyzer.py # Cost Analyzer API
│   │   │   ├── 📄 auto_hardening.py # Auto Hardening API
│   │   │   ├── 📄 behavior_alerts.py # Behavior Alerts API
│   │   │   ├── 📄 user_behavior.py  # User Behavior API
│   │   │   ├── 📄 incident_command_center.py # Incident Center API
│   │   │   ├── 📄 intelligent_log_timeline.py # Log Timeline API
│   │   │   ├── 📄 kernel_metrics.py # Kernel Metrics API
│   │   │   ├── 📄 service_dependency.py # Service Dependency API
│   │   │   ├── 📄 visualization.py # Visualization API
│   │   │   ├── 📄 global_search.py # Global Search API
│   │   │   ├── 📄 blueprint_generator.py # Blueprint Generator API
│   │   │   ├── 📄 distributed_agent_mesh.py # Agent Mesh API
│   │   │   ├── 📄 ai_code_review.py # AI Code Review API
│   │   │   ├── 📄 ai_performance_tuner.py # AI Performance Tuner API
│   │   │   ├── 📄 ai_threat_detection.py # AI Threat Detection API
│   │   │   ├── 📄 ai_workflow_builder.py # AI Workflow Builder API
│   │   │   ├── 📄 debugger.py      # Debugger API
│   │   │   ├── 📄 unified_secrets.py # Secrets API
│   │   │   ├── 📄 filesystem.py    # Filesystem API
│   │   │   ├── 📄 prometheus.py    # Prometheus API
│   │   │   ├── 📄 monitor.py       # Monitor API
│   │   │   ├── 📄 approvals.py     # Approvals API
│   │   │   └── 📄 plugin_store.py  # Plugin Store API
│   │   │
│   │   ├── 📂 services/            # Business Logic Services
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 security_service.py # Security Service
│   │   │   ├── 📄 workflow_service.py # Workflow Service
│   │   │   ├── 📄 incident_service.py # Incident Service
│   │   │   ├── 📄 monitoring_service.py # Monitoring Service
│   │   │   ├── 📄 audit_service.py # Audit Service
│   │   │   ├── 📄 backup_service.py # Backup Service
│   │   │   ├── 📄 cicd_service.py  # CI/CD Service
│   │   │   ├── 📄 deploy_engine.py # Deployment Engine
│   │   │   ├── 📄 cost_analyzer.py # Cost Analyzer Service
│   │   │   ├── 📄 auto_hardening.py # Auto Hardening Service
│   │   │   ├── 📄 behavior_based_alerting.py # Behavior Alerting
│   │   │   ├── 📄 user_behavior_engine.py # User Behavior Engine
│   │   │   ├── 📄 incident_command_center.py # Incident Center
│   │   │   ├── 📄 intelligent_log_timeline.py # Log Timeline
│   │   │   ├── 📄 live_kernel_metrics.py # Kernel Metrics
│   │   │   ├── 📄 service_dependency_graph.py # Dependency Graph
│   │   │   ├── 📄 shadow_deployment.py # Shadow Deployment
│   │   │   ├── 📄 snapshot_rollback.py # Snapshot Rollback
│   │   │   ├── 📄 config_drift_detector.py # Config Drift
│   │   │   ├── 📄 blueprint_generator.py # Blueprint Generator
│   │   │   ├── 📄 distributed_agent_mesh.py # Agent Mesh
│   │   │   ├── 📄 global_search.py # Global Search
│   │   │   ├── 📄 unified_secret_management.py # Secrets Management
│   │   │   ├── 📄 plugin_store.py  # Plugin Store
│   │   │   ├── 📄 alert_manager.py # Alert Manager
│   │   │   ├── 📄 abac_service.py  # ABAC Service
│   │   │   ├── 📄 ai_code_review.py # AI Code Review
│   │   │   ├── 📄 ai_debugger.py   # AI Debugger
│   │   │   ├── 📄 ai_performance_tuner.py # AI Performance Tuner
│   │   │   ├── 📄 ai_threat_detection.py # AI Threat Detection
│   │   │   ├── 📄 ai_workflow_builder.py # AI Workflow Builder
│   │   │   │
│   │   │   └── 📂 security_ai/     # Security AI Services
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 orchestrator.py # Security AI Orchestrator
│   │   │       ├── 📄 collector.py # Data Collector
│   │   │       ├── 📄 detector.py  # Threat Detector
│   │   │       ├── 📄 responder.py # Incident Responder
│   │   │       └── 📄 explainer.py # AI Explainer
│   │   │
│   │   ├── 📂 agent/               # AI Agent Core
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 agent.py         # Main Agent
│   │   │   ├── 📄 agent_core.py    # Agent Core Logic
│   │   │   ├── 📄 core_llm.py      # LLM Integration
│   │   │   └── 📄 think_and_act.py # Decision Making
│   │   │
│   │   ├── 📂 tools/               # Agent Tools
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 read_file.py     # File Reader Tool
│   │   │   ├── 📄 read_logs.py     # Log Reader Tool
│   │   │   ├── 📄 run_shell.py     # Shell Command Tool
│   │   │   ├── 📄 security_scan.py # Security Scanner Tool
│   │   │   ├── 📄 network_monitor.py # Network Monitor Tool
│   │   │   ├── 📄 monitor.py       # Monitor Tool
│   │   │   ├── 📄 check_service.py # Service Check Tool
│   │   │   ├── 📄 doc_search.py   # Documentation Search
│   │   │   ├── 📄 siem_monitor.py # SIEM Monitor
│   │   │   ├── 📄 advanced_security_tools.py # Advanced Security
│   │   │   │
│   │   │   └── 📂 security_scanners/ # Security Scanners
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 base.py      # Base Scanner
│   │   │       ├── 📄 repo_scanner.py # Repository Scanner
│   │   │       ├── 📄 network_scanner.py # Network Scanner
│   │   │       ├── 📄 system_scanner.py # System Scanner
│   │   │       ├── 📄 docker_scanner.py # Docker Scanner
│   │   │       ├── 📄 log_scanner.py # Log Scanner
│   │   │       ├── 📄 vulnerability_scanner.py # Vulnerability Scanner
│   │   │       ├── 📄 ids_scanner.py # IDS Scanner
│   │   │       ├── 📄 penetration_scanner.py # Penetration Scanner
│   │   │       ├── 📄 port_scanner.py # Port Scanner
│   │   │       ├── 📄 file_integrity_scanner.py # File Integrity
│   │   │       ├── 📄 infra_scanner.py # Infrastructure Scanner
│   │   │       └── 📄 malware_scanner.py # Malware Scanner
│   │   │
│   │   ├── 📂 core/                # Core Components
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 config.py        # Configuration
│   │   │   ├── 📄 database.py      # Database Connection
│   │   │   ├── 📄 security.py      # Security Core
│   │   │   ├── 📄 permissions.py   # Permissions Core
│   │   │   ├── 📄 permission_helpers.py # Permission Helpers
│   │   │   ├── 📄 abac.py          # ABAC Core
│   │   │   └── 📄 aaa_middleware.py # AAA Middleware
│   │   │
│   │   ├── 📂 models/              # Data Models
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 auth.py          # Auth Models
│   │   │   ├── 📄 chat.py          # Chat Models
│   │   │   ├── 📄 settings.py      # Settings Models
│   │   │   └── 📄 tools.py         # Tools Models
│   │   │
│   │   ├── 📂 access/              # Access Control
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 models.py        # Access Models
│   │   │   ├── 📄 schemas.py       # Access Schemas
│   │   │   └── 📄 service.py       # Access Service
│   │   │
│   │   ├── 📂 identity/            # Identity Management
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 models.py        # Identity Models
│   │   │   ├── 📄 schemas.py       # Identity Schemas
│   │   │   └── 📄 service.py       # Identity Service
│   │   │
│   │   ├── 📂 policy/              # Policy Management
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 models.py        # Policy Models
│   │   │   ├── 📄 schemas.py       # Policy Schemas
│   │   │   ├── 📄 service.py       # Policy Service
│   │   │   └── 📄 engine.py        # Policy Engine
│   │   │
│   │   ├── 📂 audit/               # Audit System
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 models.py        # Audit Models
│   │   │   ├── 📄 schemas.py       # Audit Schemas
│   │   │   └── 📄 service.py       # Audit Service
│   │   │
│   │   ├── 📂 subscription/       # Subscription Management
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 models.py        # Subscription Models
│   │   │   ├── 📄 schemas.py       # Subscription Schemas
│   │   │   └── 📄 service.py       # Subscription Service
│   │   │
│   │   ├── 📂 crm/                 # CRM Module
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 schemas.py       # CRM Schemas
│   │   │   └── 📄 service.py       # CRM Service
│   │   │
│   │   ├── 📂 utils/               # Utilities
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 logger.py        # Logging Utility
│   │   │   ├── 📄 helpers.py       # Helper Functions
│   │   │   ├── 📄 cache.py         # Caching Utility
│   │   │   ├── 📄 error_handler.py # Error Handling
│   │   │   ├── 📄 capability_detector.py # Capability Detection
│   │   │   ├── 📄 env_adapter.py   # Environment Adapter
│   │   │   └── 📄 path_resolver.py # Path Resolver
│   │   │
│   │   ├── 📂 exceptions/          # Exception Handlers
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 base.py          # Base Exceptions
│   │   │   └── 📄 handlers.py      # Exception Handlers
│   │   │
│   │   ├── 📂 monitoring/          # Monitoring
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 logging.py       # Logging Configuration
│   │   │   ├── 📄 metrics.py       # Metrics Collection
│   │   │   └── 📄 health_checks.py # Health Checks
│   │   │
│   │   ├── 📂 memory/              # Agent Memory
│   │   │   ├── 📄 memory.json      # Short-term Memory
│   │   │   ├── 📄 long_memory.json # Long-term Memory
│   │   │   ├── 📄 settings.json    # Settings Memory
│   │   │   └── 📄 users.json       # Users Memory
│   │   │
│   │   ├── 📂 docs/                # Documentation
│   │   └── 📂 logs/                # Application Logs
│   │
│   ├── 📂 database/                # Database Models
│   │   ├── 📄 __init__.py
│   │   └── 📂 models/
│   │       ├── 📄 __init__.py
│   │       ├── 📄 user.py          # User Model
│   │       ├── 📄 invoice.py       # Invoice Model
│   │       └── 📄 payment_method.py # Payment Method Model
│   │
│   ├── 📂 migrations/              # Database Migrations (Alembic)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 env.py
│   │   └── 📂 versions/            # Migration Versions
│   │
│   ├── 📂 models/                  # Additional Models
│   │   └── 📂 security_ai/         # Security AI Models
│   │
│   ├── 📂 plugins/                 # Plugin System
│   │   ├── 📂 installed/           # Installed Plugins
│   │   └── 📂 store/               # Plugin Store
│   │
│   ├── 📂 scripts/                 # Utility Scripts
│   │   └── 📄 setup_initial_data.py # Initial Data Setup
│   │
│   ├── 📂 tests/                   # Tests
│   │   ├── 📄 __init__.py
│   │   ├── 📄 conftest.py          # Test Configuration
│   │   ├── 📂 test_api/            # API Tests
│   │   └── 📂 test_services/       # Service Tests
│   │
│   ├── 📂 memory/                  # Backend Memory Storage
│   │   ├── 📄 memory.json
│   │   ├── 📄 pending_actions.json
│   │   └── 📄 settings.json
│   │
│   ├── 📂 logs/                    # Backend Logs
│   ├── 📂 snapshots/               # System Snapshots
│   ├── 📂 vault/                   # Secrets Vault
│   ├── 📂 digital_twin/            # Digital Twin Data
│   │
│   └── 📄 Dockerfile               # Backend Docker image
│
├── 📂 frontend/                    # Frontend - Next.js
│   ├── 📄 package.json             # Node.js Dependencies
│   ├── 📄 package-lock.json
│   ├── 📄 tsconfig.json            # TypeScript Configuration
│   ├── 📄 next.config.ts           # Next.js Configuration
│   ├── 📄 tailwind.config.js       # Tailwind CSS Configuration
│   ├── 📄 postcss.config.mjs       # PostCSS Configuration
│   ├── 📄 eslint.config.mjs        # ESLint Configuration
│   ├── 📄 jest.config.js           # Jest Test Configuration
│   ├── 📄 components.json          # Components Configuration
│   ├── 📄 shiftwave-theme.css      # Custom Theme
│   ├── 📄 Dockerfile
│   ├── 📄 env.example
│   │
│   ├── 📂 app/                     # Next.js App Router
│   │   ├── 📄 layout.tsx           # Root Layout
│   │   ├── 📄 page.tsx             # Home Page
│   │   ├── 📄 globals.css          # Global Styles
│   │   ├── 📄 favicon.ico
│   │   ├── 📄 theme-script.tsx     # Theme Script
│   │   │
│   │   ├── 📂 login/               # Login Page
│   │   ├── 📂 agent-mesh/          # Agent Mesh Page
│   │   ├── 📂 workflows/           # Workflows Page
│   │   ├── 📂 workflow-builder/    # Workflow Builder
│   │   ├── 📂 security/            # Security Page
│   │   ├── 📂 monitoring/          # Monitoring Page
│   │   ├── 📂 monitor/             # Monitor Page
│   │   ├── 📂 logs/                # Logs Page
│   │   ├── 📂 incidents/           # Incidents Page
│   │   ├── 📂 incident-center/    # Incident Center
│   │   ├── 📂 audit/                # Audit Page
│   │   ├── 📂 backup/              # Backup Page
│   │   ├── 📂 cicd/                # CI/CD Page
│   │   ├── 📂 billing/             # Billing Page
│   │   ├── 📂 settings/            # Settings Page
│   │   ├── 📂 knowledge/           # Knowledge Base
│   │   ├── 📂 digital-twin/        # Digital Twin
│   │   ├── 📂 snapshots/           # Snapshots
│   │   ├── 📂 secrets/             # Secrets Management
│   │   ├── 📂 plugins/             # Plugins
│   │   ├── 📂 tools/               # Tools
│   │   ├── 📂 visualization/       # Visualization
│   │   ├── 📂 global-search/       # Global Search
│   │   ├── 📂 blueprints/          # Blueprints
│   │   ├── 📂 cost-analyzer/       # Cost Analyzer
│   │   ├── 📂 hardening/           # Hardening
│   │   ├── 📂 behavior-alerts/     # Behavior Alerts
│   │   ├── 📂 threat-detection/    # Threat Detection
│   │   ├── 📂 performance-tuner/   # Performance Tuner
│   │   ├── 📂 code-review/         # Code Review
│   │   ├── 📂 debugger/            # Debugger
│   │   ├── 📂 siem/                # SIEM
│   │   ├── 📂 soc/                 # SOC
│   │   ├── 📂 tenants/             # Tenants
│   │   │
│   │   ├── 📂 crm/                 # CRM Frontend
│   │   │   ├── 📂 login/           # CRM Login
│   │   │   └── 📂 tenants/         # CRM Tenants
│   │   │       └── 📂 [tenantId]/  # Tenant Details
│   │   │           ├── 📂 subscription/ # Subscription
│   │   │           └── 📂 users/   # Tenant Users
│   │   │
│   │   ├── 📂 aaa/                 # AAA Frontend
│   │   │   ├── 📂 login/           # AAA Login
│   │   │   ├── 📂 users/           # AAA Users
│   │   │   ├── 📂 sessions/        # AAA Sessions
│   │   │   ├── 📂 tokens/          # AAA Tokens
│   │   │   └── 📂 audit/           # AAA Audit
│   │   │
│   │   ├── 📂 iam/                 # IAM Frontend
│   │   │   ├── 📂 roles/           # Roles
│   │   │   ├── 📂 permissions/     # Permissions
│   │   │   ├── 📂 policies/        # Policies
│   │   │   └── 📂 access-control/  # Access Control
│   │   │
│   │   └── 📂 abac/                # ABAC Frontend
│   │
│   ├── 📂 components/              # React Components
│   │   ├── 📄 TopNav.tsx           # Top Navigation
│   │   ├── 📄 ServicesDrawer.tsx   # Services Drawer
│   │   ├── 📄 FavoritesBar.tsx     # Favorites Bar
│   │   │
│   │   ├── 📂 ui/                  # UI Components (shadcn/ui)
│   │   ├── 📂 chat/                # Chat Components
│   │   ├── 📂 charts/              # Chart Components
│   │   ├── 📂 alerts/              # Alert Components
│   │   ├── 📂 layout/              # Layout Components
│   │   ├── 📂 crm/                 # CRM Components
│   │   └── 📂 aaa/                 # AAA Components
│   │
│   ├── 📂 lib/                     # Library Functions
│   │   ├── 📄 api.ts               # API Client
│   │   ├── 📄 utils.ts             # Utilities
│   │   └── 📄 i18n.ts              # Internationalization
│   │
│   ├── 📂 hooks/                   # React Hooks
│   ├── 📂 config/                  # Configuration
│   │
│   ├── 📂 locales/                 # Translations
│   │   ├── 📂 ar/                  # Arabic Translations
│   │   └── 📂 en/                  # English Translations
│   │
│   ├── 📂 public/                  # Static Assets
│   │   ├── 📄 shiftwave-logo.svg   # Logo
│   │   ├── 📄 next.svg
│   │   ├── 📄 vercel.svg
│   │   ├── 📄 file.svg
│   │   ├── 📄 globe.svg
│   │   └── 📄 window.svg
│   │
│   ├── 📂 __tests__/               # Frontend Tests
│   │
│   └── 📄 Dockerfile               # Frontend Docker image
│
├── 📂 prometheus/                  # Prometheus Configuration
├── 📂 grafana/                     # Grafana Configuration
│   └── 📂 provisioning/
│       ├── 📂 dashboards/
│       └── 📂 datasources/
├── 📂 loki/                        # Loki Configuration
├── 📂 promtail/                    # Promtail Configuration
└── 📂 alertmanager/                # Alertmanager Configuration
    └── 📄 alertmanager.yml
```

## 📊 إحصائيات المشروع

### Backend (Python/FastAPI)
- **API Endpoints**: 50+ endpoint files
- **Services**: 30+ service files
- **Tools**: 10+ tool files
- **Security Scanners**: 12+ scanner types
- **Database Models**: Multiple models for users, invoices, payments
- **Tests**: Comprehensive test suite

### Frontend (Next.js/TypeScript)
- **Pages**: 40+ pages/modules
- **Components**: Multiple component libraries
- **Services**: AI-Agent, CRM, AAA (3 separate frontends)
- **Internationalization**: Arabic & English support

### Infrastructure
- **Docker**: docker-compose.yml for containerization
- **Monitoring**: Prometheus, Grafana, Loki, Promtail
- **Process Management**: PM2 configuration
- **Reverse Proxy**: NGINX setup scripts

## 🔑 الملفات المهمة

### Backend
- `backend/app/main.py` - نقطة البداية الرئيسية
- `backend/app/api/` - جميع API endpoints
- `backend/app/services/` - Business logic
- `backend/app/tools/` - Agent tools
- `backend/app/agent/` - AI Agent core

### Frontend
- `frontend/app/layout.tsx` - Root layout
- `frontend/app/page.tsx` - Home page
- `frontend/components/` - React components
- `frontend/lib/api.ts` - API client

### Configuration
- `docker-compose.yml` - Docker services
- `ecosystem.config.js` - PM2 config
- `setup-all-services.sh` - NGINX setup

## 🚀 الخدمات الرئيسية (Docker Containers)

### Backend Services
1. **Backend API** - `ai-backend` (port 8000)
2. **PostgreSQL** - `ai-agent-postgres` (port 5432)
3. **Ollama** - `ai-agent-ollama` (port 11434)

### Frontend Services
4. **Dashboard** - `ai-agent-frontend-dashboard` (port 3000)
5. **CRM** - `ai-agent-frontend-crm` (port 3001)
6. **AAA** - `ai-agent-frontend-aaa` (port 3002)

## 📝 ملاحظات

- جميع الخدمات تعمل في Docker containers منفصلة
- جميع الملفات المهمة موثقة في `SERVICES_TOOLS.md`
- البنية مصممة لتكون قابلة للتوسع والاختبار
- يدعم المشروع Multi-tenancy و AAA
- نظام أمان شامل مع فحوصات متعددة
- نظام مراقبة متكامل مع Prometheus/Grafana
- استخدام `docker compose` (بدلاً من `docker-compose`) في جميع السكربتات

---

**تم إنشاء هذا الملف تلقائياً - آخر تحديث: $(date)**

