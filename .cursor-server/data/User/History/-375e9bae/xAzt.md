# 🔧 SHIFTWAVE AI - Services & Tools Documentation

## 📋 جميع الخدمات (Services) والأدوات المستخدمة

---

## 🎯 CORE Services

### 1. **Dashboard** 📊
- **Route**: `/`
- **API**: `GET /api/monitor/server-metrics`, `GET /api/monitor`
- **Tools Used**:
  - **Backend**:
    - `psutil` - System metrics (CPU, RAM, Disk, Network)
    - `prometheus-client` - Metrics collection (Counter, Gauge, generate_latest)
    - `app.tools.monitor` - Monitor tool (run function)
    - `app.tools.network_monitor` - Network monitoring
    - FastAPI - API endpoints
    - System file reading (`/proc/meminfo`, `/proc/loadavg`)
  - **Frontend**:
    - React/Next.js - Frontend rendering
    - Recharts/Chart.js - Data visualization
    - Real-time data fetching
    - State management (useState, useEffect)

### 2. **Agent Console** 💻
- **Route**: `/`
- **API**: `POST /api/chat`, `WebSocket /ws/chat`, `WebSocket /ws/agent`
- **Tools Used**:
  - **Backend**:
    - `ollama` - Local AI model (LLM)
    - `app.agent.think_and_act` - Agent thinking and action execution
    - FastAPI WebSocket - Real-time communication (WebSocketDisconnect handling)
    - `app.utils.helpers.log_chat` - Chat logging
    - ConnectionManager - WebSocket connection management
    - Memory management system - Context retention
  - **Frontend**:
    - React Chat Components (ChatBox, ChatContainer, ChatMessage)
    - WebSocket client for real-time updates
    - Session management

### 3. **Global Search** 🔍
- **Route**: `/global-search`
- **API**: `GET /api/search/`, `POST /api/search/path/add`
- **Tools Used**:
  - **Backend**:
    - `app.services.global_search` - Global search engine
    - Full-text search algorithms
    - Indexing system for multiple sources (logs, files, workflows, docs, configs)
    - Path management for search sources
    - FastAPI - Search endpoints with query parameters
  - **Frontend**:
    - Search input component
    - Results display with source filtering

### 4. **AI Debugger** 🐛
- **Route**: `/debugger`
- **API**: `POST /api/debugger/analyze`, `POST /api/debugger/watch/start`, `GET /api/debugger/errors`, `WebSocket /api/debugger/ws/logs`
- **Tools Used**:
  - **Backend**:
    - `ollama` - AI model for debugging
    - `app.services.ai_debugger` - AI debugger service
    - Code analysis tools
    - Error pattern recognition
    - Log analysis algorithms
    - File system watching (`watchdog`)
    - Docker logs checking (`docker` client)
    - Systemd service status checking
    - Auto-fix capability
    - WebSocket for live log streaming
  - **Frontend**:
    - Error display components
    - Real-time log viewer
    - Auto-fix toggle

---

## 📈 OBSERVABILITY Services

### 5. **Monitoring** 📈
- **Route**: `/monitoring`
- **API**: `GET /api/monitor/server-metrics`, `GET /api/monitoring/*`, `GET /api/monitor/service-status/{service_name}`, `GET /api/monitor/container-status/{container_name}`
- **Tools Used**:
  - **Backend**:
    - `psutil` - System monitoring (CPU, memory, disk, network)
    - `prometheus-client` - Metrics collection (Counter, Gauge, generate_latest, REGISTRY)
    - `docker` - Container monitoring (docker.from_env())
    - `app.services.monitoring_service` - Monitoring service layer
    - `app.services.alert_manager` - Alert management (AlertLevel enum)
    - Systemd service checking
    - Auto-repair functionality for services and containers
    - Grafana - Visualization (optional)
    - Prometheus - Metrics storage (`/metrics` endpoint)
  - **Frontend**:
    - Real-time metrics display
    - Alert notifications
    - Service status cards

### 6. **Logs** 📋
- **Route**: `/logs`
- **API**: `GET /api/logs`, `POST /api/logs/timeline/add`, `GET /api/logs/timeline/view`
- **Tools Used**:
  - **Backend**:
    - Loki - Log aggregation
    - Promtail - Log collection
    - File system monitoring (`watchdog`)
    - `app.services.intelligent_log_timeline` - Intelligent log timeline service
    - Log parsing and filtering
    - Search indexing
    - Root cause analysis
    - Error summary generation
    - JSON log parsing (`json.loads`)
    - File reading (`chat.log` from LOG_DIR)
  - **Frontend**:
    - Log viewer component
    - Timeline visualization
    - Filtering and search

### 7. **Incidents** ⚠️
- **Route**: `/incidents`
- **API**: `GET /api/incidents`, `POST /api/incidents`, `PUT /api/incidents/{incident_id}`, `POST /api/incidents/{incident_id}/resolve`
- **Tools Used**:
  - **Backend**:
    - SQLite database (`incidents.db`)
    - `app.services.incident_service` - Incident service (IncidentStatus enum)
    - Alert Manager integration
    - Incident tracking system
    - Status management (open, investigating, resolved)
    - Root cause tracking
    - Actions taken logging
    - Notification system
  - **Frontend**:
    - Incident list view
    - Incident detail view
    - Status update forms

### 8. **Incident Center** 🚨
- **Route**: `/incident-center`
- **API**: `POST /api/incidents/command-center/create`, `GET /api/incidents/command-center/`, `POST /api/incidents/command-center/{incident_id}/chat`
- **Tools Used**:
  - **Backend**:
    - `app.services.incident_command_center` - Incident command center service
    - Command center orchestration
    - Real-time incident management
    - Multi-user collaboration
    - Chat system for team communication
    - Root cause analysis
    - Fix application tracking
    - Statistics generation
    - WebSocket for live updates (optional)
  - **Frontend**:
    - Command center dashboard
    - Team chat interface
    - Incident timeline
    - Statistics dashboard

### 9. **Visualization** 👁️
- **Route**: `/visualization`
- **API**: `GET /api/visualization/network-map`, `GET /api/visualization/architecture`, `GET /api/visualization/metrics`
- **Tools Used**:
  - **Backend**:
    - `docker` - Docker client for container inspection
    - `psutil` - System metrics for heatmap
    - Network map generation from Docker containers
    - Architecture graph generation
    - Service dependency mapping
    - Port mapping extraction
    - Container status tracking
  - **Frontend**:
    - D3.js / Recharts - Data visualization
    - Chart.js - Chart rendering
    - Network graph visualization
    - Heatmap components
    - Real-time data streaming
    - Custom visualization components

---

## 🧠 AI & AUTOMATION Services

### 10. **AI Tools** 🧠
- **Route**: `/tools`
- **API**: `POST /api/tools/read_file`, `POST /api/tools/run_shell`, `POST /api/tools/service`
- **Tools Used**:
  - **Backend**:
    - `ollama` - Local AI models
    - `app.tools.read_file` - File reading tool
    - `app.tools.run_shell` - Shell command execution
    - `app.tools.check_service` - Service status checking
    - `app.core.permissions` - Permission engine for tool access
    - `app.pending_actions` - Pending actions system for approval workflow
    - Tool execution framework
    - Plugin system
    - Dynamic tool loading
    - Permission checking (check_tool_permission)
    - Approval workflow integration
  - **Frontend**:
    - Tool execution interface
    - Results display
    - Approval status tracking

### 11. **Threat Detection** 🛡️
- **Route**: `/threat-detection`
- **API**: `POST /api/security/threat-detection/analyze`, `GET /api/security/threat-detection/summary`, `GET /api/security/threat-detection/incidents`
- **Tools Used**:
  - **Backend**:
    - `ollama` - AI threat analysis
    - `app.services.ai_threat_detection` - Threat detector service
    - `app.services.security_ai.orchestrator` - Security AI orchestrator
    - Pattern recognition algorithms
    - Log analysis engine
    - Anomaly detection (`scikit-learn`)
    - Real-time threat scoring
    - Baseline metrics management
    - Incident tracking
    - Status monitoring (start/stop)
  - **Frontend**:
    - Threat dashboard
    - Real-time threat alerts
    - Incident timeline

### 12. **ABAC** 🔐
- **Route**: `/abac`
- **API**: `POST /api/abac/check`, `POST /api/abac/policies`, `GET /api/abac/policies`, `DELETE /api/abac/policies/{policy_name}`
- **Tools Used**:
  - **Backend**:
    - `app.services.abac_service` - ABAC service layer
    - Attribute-Based Access Control engine
    - Policy evaluation system
    - Context-aware authorization (source_ip, is_vpn, etc.)
    - Permission caching
    - SQLite for policy storage
    - Policy CRUD operations (add, list, remove)
  - **Frontend**:
    - Policy management interface
    - Access check testing
    - Policy visualization

### 13. **Behavior Alerts** 👁️
- **Route**: `/behavior-alerts`
- **API**: `POST /api/alerts/behavior/event`, `GET /api/alerts/behavior/`, `POST /api/alerts/behavior/{alert_id}/acknowledge`
- **Tools Used**:
  - **Backend**:
    - `scikit-learn` - Anomaly detection
    - `app.services.behavior_based_alerting` - Behavior alerting service
    - User behavior analysis
    - Pattern matching
    - Alert generation system
    - Event recording
    - Alert acknowledgment and resolution
    - Statistics generation
    - Severity filtering
  - **Frontend**:
    - Alert dashboard
    - Behavior pattern visualization
    - Alert management interface

### 14. **Digital Twin** 🌍
- **Route**: `/digital-twin`
- **API**: `POST /api/digital-twin/create`, `GET /api/digital-twin/`, `POST /api/digital-twin/{twin_id}/simulate/deploy`
- **Tools Used**:
  - **Backend**:
    - `app.services.digital_twin` - Digital twin service
    - System state modeling
    - Configuration tracking
    - State synchronization
    - Virtual environment simulation
    - Deployment simulation
    - Failure simulation
    - Production comparison
    - Twin lifecycle management (create, get, list, delete)
  - **Frontend**:
    - Twin visualization
    - Simulation controls
    - Comparison dashboard

### 15. **Agent Mesh** 🌐
- **Route**: `/agent-mesh`
- **API**: `POST /api/agents/mesh/start`, `GET /api/agents/mesh/status`, `POST /api/agents/mesh/task`
- **Tools Used**:
  - **Backend**:
    - `app.services.distributed_agent_mesh` - Agent mesh service
    - Distributed agent system
    - Inter-agent communication
    - Mesh networking
    - Load balancing
    - Node management (start, stop, status, list)
    - Task distribution
    - Capability-based node selection
    - WebSocket for real-time communication (optional)
  - **Frontend**:
    - Mesh visualization
    - Node status dashboard
    - Task monitoring

### 16. **Code Review** 🔍
- **Route**: `/code-review`
- **API**: `POST /api/code/review/review`, `POST /api/code/review/auto-fix`
- **Tools Used**:
  - **Backend**:
    - `ollama` - AI code analysis
    - `app.services.ai_code_review` - Code reviewer service
    - Code parsing (AST)
    - Security vulnerability detection
    - Code quality metrics
    - Best practices checking
    - Auto-fix capability
    - File reading and analysis
  - **Frontend**:
    - Code review interface
    - Issue highlighting
    - Auto-fix preview and apply

### 17. **Workflow Builder** 🔧
- **Route**: `/workflow-builder`
- **API**: `POST /api/workflows/builder/create`, `GET /api/workflows/builder/`, `POST /api/workflows/builder/{workflow_id}/step`
- **Tools Used**:
  - **Backend**:
    - `ollama` - AI workflow generation
    - `app.services.ai_workflow_builder` - Workflow builder service
    - Workflow engine
    - Visual workflow designer
    - Step orchestration
    - Step suggestion (AI-powered)
    - Auto-complete for steps
    - Workflow debugging
    - Execution map generation
  - **Frontend**:
    - Visual workflow designer
    - Step configuration
    - Workflow preview

### 18. **Workflows** ⚡
- **Route**: `/workflows`
- **API**: `POST /api/workflows`, `GET /api/workflows`, `POST /api/workflows/{workflow_id}/execute`
- **Tools Used**:
  - **Backend**:
    - `app.services.workflow_service` - Workflow service
    - Workflow execution engine
    - Task scheduling
    - State management
    - Error handling and retries
    - Node and edge management
    - Execution tracking
    - Execution history
  - **Frontend**:
    - Workflow list view
    - Execution monitoring
    - Results display

### 19. **Snapshots** 📸
- **Route**: `/snapshots`
- **API**: `POST /api/snapshots/create`, `POST /api/snapshots/rollback/{snapshot_id}`, `GET /api/snapshots/list`
- **Tools Used**:
  - **Backend**:
    - `app.services.snapshot_rollback` - Snapshot engine
    - System state capture
    - File system snapshots
    - Configuration backup
    - Rollback mechanism
    - Snapshot type management
    - Metadata storage
    - Force rollback option
  - **Frontend**:
    - Snapshot list view
    - Rollback interface
    - Snapshot creation wizard

### 20. **Blueprint Generator** 📋
- **Route**: `/blueprints`
- **API**: `POST /api/blueprints/generate`, `POST /api/blueprints/docker-compose`, `POST /api/blueprints/kubernetes`, `POST /api/blueprints/nginx`
- **Tools Used**:
  - **Backend**:
    - `ollama` - AI blueprint generation
    - `app.services.blueprint_generator` - Blueprint generator service
    - Template engine
    - Configuration generation
    - YAML/JSON generation
    - Docker Compose generation
    - Kubernetes manifest generation
    - Nginx config generation
    - Systemd unit generation
    - CI/CD YAML generation
  - **Frontend**:
    - Blueprint configuration form
    - Generated file preview
    - Download functionality

### 21. **Plugin Store** 🧩
- **Route**: `/plugins`
- **API**: `GET /api/plugins/`, `POST /api/plugins/{plugin_id}/install`, `POST /api/plugins/register`
- **Tools Used**:
  - **Backend**:
    - `app.services.plugin_store` - Plugin store service
    - Plugin management system
    - Dynamic plugin loading
    - Plugin registry
    - Version management
    - Plugin installation/uninstallation
    - Plugin type filtering
    - Plugin metadata management
  - **Frontend**:
    - Plugin store interface
    - Installation controls
    - Plugin details view

---

## 🔒 SECURITY Services

### 22. **Security Center** 🔒
- **Route**: `/security`
- **API**: `POST /api/security/scan_repo`, `POST /api/security/scan_infra`, `POST /api/security/scan_logs`, `GET /api/security/siem`
- **Tools Used**:
  - **Backend**:
    - `app.services.security_service` - Security service layer
    - `app.tools.security_scan` - Security scanning tools (scan_repo, scan_infra, scan_logs_auth, scan_network_security, scan_system_security, scan_docker_security)
    - `app.tools.siem_monitor` - SIEM monitoring (add_scan_event)
    - Security dashboard aggregation
    - Threat intelligence
    - Security metrics
    - Compliance checking
    - Repository scanning
    - Infrastructure scanning
    - Log scanning
    - Network scanning
    - System scanning
    - Docker scanning
    - SIEM integration
    - Approval workflow integration (`app.pending_actions`)
  - **Frontend**:
    - Security dashboard
    - Scan results display
    - SIEM monitoring view

### 23. **SIEM/SOC** 📊
- **Route**: `/siem`
- **API**: `GET /api/security/siem`
- **Tools Used**:
  - **Backend**:
    - `app.tools.siem_monitor` - SIEM monitoring system
    - Security Information and Event Management
    - Log correlation
    - Event analysis
    - Alert aggregation
    - Incident response automation
    - Scan event tracking
    - Severity classification
    - Event timestamping
  - **Frontend**:
    - SIEM dashboard
    - Event timeline
    - Alert management

### 24. **Secrets Manager** 🔑
- **Route**: `/secrets`
- **API**: `POST /api/secrets/store`, `GET /api/secrets/{secret_id}`, `POST /api/secrets/{secret_id}/rotate`, `POST /api/secrets/auto-rotate`
- **Tools Used**:
  - **Backend**:
    - `cryptography` - Secret encryption
    - `app.services.unified_secret_management` - Secret manager service
    - Vault-like storage
    - Key management
    - Secret rotation (manual and automatic)
    - Access control
    - Access policy management
    - Audit logging
    - Secret type management (api_key, password, etc.)
    - Service-based access control
  - **Frontend**:
    - Secret management interface
    - Rotation controls
    - Access policy configuration

### 25. **Auto-Hardening** 🧱
- **Route**: `/hardening`
- **API**: `POST /api/security/hardening/apply`, `GET /api/security/hardening/status`
- **Tools Used**:
  - **Backend**:
    - `app.services.auto_hardening` - Auto-hardening service
    - Security configuration automation
    - Compliance checking
    - System hardening scripts
    - Configuration validation
    - Status tracking
  - **Frontend**:
    - Hardening dashboard
    - Apply controls
    - Status display

---

## 🚀 DEVOPS Services

### 26. **CI/CD** 🚀
- **Route**: `/cicd`
- **API**: `POST /api/cicd/clone`, `POST /api/cicd/pull`, `POST /api/cicd/run`, `GET /api/cicd/status/{pipeline_id}`, `POST /api/cicd/deploy/docker-compose`
- **Tools Used**:
  - **Backend**:
    - `app.services.cicd_service` - CI/CD service
    - `app.services.deploy_engine` - Deployment engine
    - CI/CD pipeline engine
    - Git integration (clone, pull)
    - Build automation
    - Deployment automation (Docker Compose, Kubernetes, RSync)
    - Testing frameworks
    - Pipeline status tracking
    - Pipeline logs management
    - Rollback capability
    - Repository management
  - **Frontend**:
    - Pipeline dashboard
    - Build logs viewer
    - Deployment controls

### 27. **Deployments** 🚀
- **Route**: `/cicd?tab=deployments`
- **API**: `POST /api/cicd/deploy/docker-compose`, `POST /api/cicd/deploy/kubernetes`, `POST /api/cicd/deploy/rsync`, `GET /api/cicd/deploy/status`
- **Tools Used**:
  - **Backend**:
    - `app.services.deploy_engine` - Deployment engine
    - Deployment tracking
    - Rollback capabilities
    - Version management
    - Environment management
    - Docker Compose deployment
    - Kubernetes deployment (kubectl)
    - RSync deployment
    - Deployment status tracking
  - **Frontend**:
    - Deployment dashboard
    - Deployment history
    - Status monitoring

### 28. **Shadow Deployment** ☁️
- **Route**: `/shadow-deploy`
- **API**: `POST /api/deployment/shadow/create`, `POST /api/deployment/shadow/{shadow_id}/route`, `POST /api/deployment/shadow/{shadow_id}/promote`
- **Tools Used**:
  - **Backend**:
    - `app.services.shadow_deployment` - Shadow deployment service
    - Canary deployment
    - Traffic splitting (percentage-based)
    - A/B testing
    - Gradual rollout
    - Result comparison
    - Shadow promotion to production
    - Shadow lifecycle management
  - **Frontend**:
    - Shadow deployment dashboard
    - Traffic control interface
    - Comparison view

### 29. **Backup & Restore** 💾
- **Route**: `/backup`
- **API**: `POST /api/backup/postgresql`, `POST /api/backup/mysql`, `POST /api/backup/docker-volume`, `POST /api/backup/create`, `GET /api/backup/list`
- **Tools Used**:
  - **Backend**:
    - `app.services.backup_service` - Backup service (BackupType enum)
    - Backup scheduling
    - Data compression
    - Storage management
    - Restore automation
    - PostgreSQL backup (pg_dump)
    - MySQL backup (mysqldump)
    - Docker volume backup
    - System backup
    - Backup verification
    - Backup listing and filtering
  - **Frontend**:
    - Backup dashboard
    - Backup creation wizard
    - Restore interface

### 30. **Cost Analyzer** 💰
- **Route**: `/cost-analyzer`
- **API**: `GET /api/cost/metrics`, `GET /api/cost/summary`, `GET /api/cost/anomalies`, `POST /api/cost/service/analyze`
- **Tools Used**:
  - **Backend**:
    - `app.services.cost_analyzer` - Cost analyzer service
    - Resource usage tracking
    - Cost calculation
    - Budget management
    - Cost optimization recommendations
    - Anomaly detection
    - Service-specific cost analysis
    - Pricing data management
  - **Frontend**:
    - Cost dashboard
    - Anomaly alerts
    - Recommendations display

---

## 🏢 PLATFORM Services

### 31. **Tenants** 🏢
- **Route**: `/tenants`
- **API**: `GET /api/settings/tenants` (via settings API)
- **Tools Used**:
  - **Backend**:
    - `app.api.settings` - Settings API
    - Multi-tenancy system
    - Tenant isolation
    - Resource allocation
    - Tenant management
    - Settings persistence
  - **Frontend**:
    - Tenant management interface
    - Resource allocation dashboard

### 32. **Billing** 💳
- **Route**: `/billing`
- **API**: `GET /api/billing/invoices`, `GET /api/billing/subscriptions`, `GET /api/billing/payment-methods`
- **Tools Used**:
  - **Backend**:
    - `app.api.billing` - Billing API
    - Billing calculation
    - Invoice generation
    - Payment processing
    - Subscription management
    - Payment method management (card, manual, electronic, bank_transfer, sham_cash)
    - Default payment method setting
  - **Frontend**:
    - Invoice list view
    - Subscription dashboard
    - Payment method management

### 33. **Approvals** ✅
- **Route**: `/approvals`
- **API**: `GET /api/pending-actions`, `POST /api/pending-actions/{action_id}/approve`, `POST /api/pending-actions/{action_id}/reject`
- **Tools Used**:
  - **Backend**:
    - `app.pending_actions` - Pending actions system (add_pending_action, approve_action, reject_action, get_pending_actions, get_action_by_id)
    - `app.tools.run_shell` - Shell execution for approved actions
    - `app.tools.read_file` - File reading for approved actions
    - `app.tools.check_service` - Service checking for approved actions
    - `app.tools.security_scan` - Security scanning for approved actions
    - Approval workflow engine
    - Notification system
    - Role-based approvals (admin, devops)
    - Action execution after approval
    - Execution result storage
    - Audit trail
  - **Frontend**:
    - Approval dashboard
    - Action details view
    - Approve/reject controls

### 34. **Knowledge Base** 📚
- **Route**: `/knowledge`
- **API**: `GET /api/knowledge`, `POST /api/knowledge`, `POST /api/knowledge/search`
- **Tools Used**:
  - **Backend**:
    - `app.api.knowledge` - Knowledge API
    - Knowledge management system
    - In-memory storage (JSON-based)
    - Search engine (keyword matching with scoring)
    - Content management (CRUD operations)
    - Category and tag management
    - Semantic search (simple keyword-based, can be enhanced with embeddings)
    - Relevance scoring
  - **Frontend**:
    - Knowledge base interface
    - Search functionality
    - Content editor

### 35. **Audit Trail** 📝
- **Route**: `/audit`
- **API**: `POST /api/audit/log`, `GET /api/audit/logs`, `GET /api/audit/export`
- **Tools Used**:
  - **Backend**:
    - SQLite database (`audit.db`)
    - `app.services.audit_service` - Audit service (ActionType enum)
    - Event logging
    - Audit query system (filtering by user, action, date range)
    - Compliance reporting
    - Log export (JSON)
    - Action type enumeration
    - IP address tracking
    - Status tracking (success/failure)
  - **Frontend**:
    - Audit log viewer
    - Filtering interface
    - Export functionality

### 36. **Settings** ⚙️
- **Route**: `/settings`
- **API**: `GET /api/settings`, `PUT /api/settings`, `POST /api/settings/test-email`
- **Tools Used**:
  - **Backend**:
    - `app.models.settings` - Settings model (SettingsModel)
    - `app.utils.helpers` - Settings helpers (load_settings, save_settings)
    - Configuration management
    - Settings persistence (JSON file)
    - User preferences
    - System configuration
    - Email alerts configuration (SMTP settings)
    - Email testing (smtplib, MIMEText, MIMEMultipart)
  - **Frontend**:
    - Settings interface
    - Configuration forms
    - Email test functionality

---

## 🛠️ Core Technologies & Libraries

### Backend (Python/FastAPI):
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Python-JOSE** - JWT authentication
- **Passlib** - Password hashing
- **psutil** - System metrics
- **docker** - Container management
- **ollama** - Local AI models
- **scikit-learn** - Machine learning
- **cryptography** - Encryption
- **watchdog** - File system monitoring
- **prometheus-client** - Metrics
- **httpx** - HTTP client
- **pyyaml** - YAML parsing

### Frontend (Next.js/React):
- **Next.js 16** - React framework (App Router, Server Components, Client Components)
- **React 19.2.0** - UI library (useState, useEffect, useMemo, useRef, hooks)
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling (utility-first CSS)
- **shadcn/ui** - UI components (Button, Card, Input, Label, ScrollArea, Switch, Textarea)
- **Lucide React** - Icons (Search, Bell, HelpCircle, Settings, ChevronDown, Menu, Sun, Moon, Zap, Globe)
- **Recharts/Chart.js** - Charts (LineChart, BarChart, PieChart)
- **WebSocket** - Real-time communication (native WebSocket API)
- **next/navigation** - Navigation (useRouter, usePathname, Link)
- **localStorage** - Client-side storage (favorites, recent pages)
- **class-variance-authority** - Component variants
- **clsx** - Conditional class names
- **tailwind-merge** - Tailwind class merging

### Infrastructure:
- **Docker** - Containerization (docker-compose.yml, Dockerfile)
- **Docker Compose** - Orchestration (docker-compose.yml, docker-compose.prod.yml)
- **Prometheus** - Metrics collection (metrics endpoint, Counter, Gauge)
- **Grafana** - Visualization (dashboards: ai-backend-simple.json, ai-backend-dashboard.json)
- **Loki** - Log aggregation (log storage and querying)
- **Promtail** - Log collection (log shipping to Loki)
- **Alert Manager** - Alerting (alert routing and notification)

### Databases & Storage:
- **SQLite** - Primary database
  - `audit.db` - Audit trail (audit_service)
  - `incidents.db` - Incidents (incident_service)
- **JSON files** - Configuration storage
  - `backend/app/memory/memory.json` - Agent memory
  - `backend/app/memory/settings.json` - Memory settings
  - `backend/app/memory/users.json` - User data
  - `backend/app/memory/long_memory.json` - Long-term memory
  - `backend/audit_export.json` - Audit exports
  - `frontend/locales/en/common.json` - English translations
  - `frontend/locales/ar/common.json` - Arabic translations
- **File System** - Additional storage
  - `backend/snapshots/` - System snapshots
  - `backend/vault/` - Vault storage (secrets)
  - `backend/logs/` - Application logs
  - `backend/plugins/` - Plugin storage
  - `backend/digital_twin/` - Digital twin data

---

## 📊 Service Categories Summary

| Category | Services Count | Key Tools |
|----------|---------------|-----------|
| **CORE** | 4 | FastAPI, Ollama, WebSocket, React |
| **OBSERVABILITY** | 5 | Prometheus, Loki, Grafana, psutil |
| **AI & AUTOMATION** | 12 | Ollama, scikit-learn, Workflow Engine |
| **SECURITY** | 4 | Cryptography, ABAC, Threat Detection AI |
| **DEVOPS** | 5 | Docker, CI/CD Engine, Backup System |
| **PLATFORM** | 6 | Multi-tenancy, Billing, Audit System |
| **TOTAL** | **36 Services** | |

---

## 🔗 API Endpoints Summary

### Authentication & Authorization:
- `/api/auth/*` - Authentication
- `/api/abac/*` - ABAC authorization
- `/api/permissions/*` - Permission management

### Core Services:
- `/api/chat` - Agent console
- `/api/monitor/*` - System monitoring
- `/api/tools/*` - AI tools

### Security:
- `/api/security/*` - Security center
- `/api/security/threat-detection/*` - Threat detection
- `/api/unified-secrets/*` - Secrets management
- `/api/auto-hardening/*` - Auto-hardening

### Observability:
- `/api/logs/*` - Log management
- `/api/monitoring/*` - Advanced monitoring
- `/api/incidents/*` - Incident management
- `/api/visualization/*` - Data visualization

### AI & Automation:
- `/api/ai-code-review/*` - Code review
- `/api/ai-workflow-builder/*` - Workflow builder
- `/api/ai-threat-detection/*` - Threat detection
- `/api/ai-performance-tuner/*` - Performance tuning
- `/api/blueprint-generator/*` - Blueprint generation

### DevOps:
- `/api/cicd/*` - CI/CD pipelines
- `/api/backup/*` - Backup & restore
- `/api/shadow-deployment/*` - Shadow deployment
- `/api/cost-analyzer/*` - Cost analysis

### Platform:
- `/api/settings/*` - Settings management
- `/api/billing/*` - Billing
- `/api/approvals/*` - Approvals
- `/api/audit/*` - Audit trail
- `/api/knowledge/*` - Knowledge base

---

## 🔧 Additional Tools & Services

### System-Level Tools:
- **File System Operations**:
  - `app.tools.file_explorer` - File system exploration (list_dir, read_file, tail_file)
  - `app.api.filesystem` - Filesystem API (`/api/fs/list`, `/api/fs/read`, `/api/fs/tail`)
  - File permission checking
  - Settings-based file access control

- **Network Operations**:
  - `app.tools.network_monitor` - Network monitoring (RX/TX stats, connections)
  - Network interface inspection
  - Connection tracking
  - Bandwidth calculation

- **Service Management**:
  - `app.tools.check_service` - Service status checking
  - Systemd service management
  - Container status checking
  - Auto-repair functionality

### Security Scanning Tools:
- **Repository Scanning**:
  - Secret detection (API keys, passwords, tokens)
  - Pattern matching for sensitive data
  - File type filtering
  - Max files limit

- **Infrastructure Scanning**:
  - Configuration file analysis
  - Security misconfiguration detection
  - Best practices checking

- **Network Scanning**:
  - Port scanning
  - Network security analysis
  - Connection analysis
  - Detailed network forensics

- **System Scanning**:
  - System security assessment
  - Vulnerability detection
  - Compliance checking
  - File integrity checking

- **Docker Scanning**:
  - Container security analysis
  - Image vulnerability scanning
  - Configuration review

### Advanced Security Tools:
- **Threat Intelligence**:
  - IP reputation checking
  - Threat feed integration
  - Malware detection

- **Forensics**:
  - Network forensics analysis
  - Memory forensics
  - Disk forensics
  - Packet analysis

- **Penetration Testing**:
  - Automated penetration testing
  - Vulnerability exploitation testing
  - Security assessment

- **Compliance**:
  - CIS compliance checking
  - Standard-based compliance (CIS, PCI-DSS, etc.)
  - Compliance reporting

### Performance & Monitoring Tools:
- **Kernel Metrics**:
  - `app.services.live_kernel_metrics` - Kernel metrics service
  - IO latency monitoring
  - Kernel scheduling metrics
  - Packet drops tracking
  - Cgroup throttling
  - Disk queues monitoring

- **Service Dependencies**:
  - `app.services.service_dependency_graph` - Dependency graph service
  - Service discovery
  - Dependency mapping
  - Impact analysis
  - Connection tracking

- **Config Drift Detection**:
  - `app.services.config_drift_detector` - Config drift detector
  - Configuration snapshotting
  - Drift detection
  - Configuration restoration
  - Monitored paths management

### AI & Machine Learning Tools:
- **AI Services**:
  - `app.services.ai_threat_detection` - AI threat detection
  - `app.services.ai_code_review` - AI code review
  - `app.services.ai_workflow_builder` - AI workflow builder
  - `app.services.ai_performance_tuner` - AI performance tuning
  - `app.services.security_ai.orchestrator` - Security AI orchestrator

- **ML Libraries**:
  - `scikit-learn` - Machine learning (anomaly detection, clustering)
  - Pattern recognition algorithms
  - Statistical analysis

### Workflow & Automation Tools:
- **Workflow Engine**:
  - `app.services.workflow_service` - Workflow execution engine
  - Node-based workflow system
  - Edge management
  - Execution tracking
  - State management

- **Deployment Engine**:
  - `app.services.deploy_engine` - Deployment automation
  - Docker Compose deployment
  - Kubernetes deployment (kubectl integration)
  - RSync deployment
  - Deployment status tracking

### Permission & Authorization Tools:
- **Permission System**:
  - `app.core.permissions` - Permission engine
  - `app.core.permission_helpers` - Permission helpers (check_action_permission)
  - Role-based access control (RBAC)
  - Attribute-based access control (ABAC)
  - Action-based permissions
  - Approval workflow integration

- **Authentication**:
  - `app.core.security` - Security utilities (create_access_token, verify_token)
  - JWT token management
  - Password hashing (bcrypt)
  - User authentication
  - Role management

### Data Management Tools:
- **Memory Management**:
  - `app.memory` - Memory management system
  - Long-term memory storage
  - User memory tracking
  - Settings persistence

- **Audit & Logging**:
  - `app.services.audit_service` - Audit service
  - Action logging
  - Event tracking
  - Compliance logging
  - Export functionality

- **User Behavior**:
  - `app.services.user_behavior_engine` - User behavior analysis
  - Action tracking
  - Suspicious activity detection
  - Safe mode recommendations
  - User profiling

---

## 📝 Notes

- **Total Services**: 36 services
- **Total API Endpoints**: 100+ endpoints
- **AI-Powered Services**: 8 services use AI (Ollama)
- **Real-time Services**: 5 services use WebSocket
- **Security Services**: 4 dedicated security services + 20+ security scanning tools
- **All services are 100% local/offline** - No external API dependencies
- **Backend Services**: 50+ service modules
- **Frontend Components**: 30+ React components
- **Tools**: 20+ system tools
- **Storage**: SQLite databases + JSON files + File system

