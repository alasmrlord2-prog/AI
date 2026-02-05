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
- **API**: `POST /api/digital-twin/*`
- **Tools Used**:
  - System state modeling
  - Configuration tracking
  - State synchronization
  - Virtual environment simulation

### 15. **Agent Mesh** 🌐
- **Route**: `/agent-mesh`
- **API**: `POST /api/agent-mesh/*`
- **Tools Used**:
  - Distributed agent system
  - Inter-agent communication
  - Mesh networking
  - Load balancing
  - WebSocket for real-time communication

### 16. **Code Review** 🔍
- **Route**: `/code-review`
- **API**: `POST /api/ai-code-review/review`
- **Tools Used**:
  - `ollama` - AI code analysis
  - Code parsing (AST)
  - Security vulnerability detection
  - Code quality metrics
  - Best practices checking

### 17. **Workflow Builder** 🔧
- **Route**: `/workflow-builder`
- **API**: `POST /api/ai-workflow-builder/generate`
- **Tools Used**:
  - `ollama` - AI workflow generation
  - Workflow engine
  - Visual workflow designer
  - Step orchestration

### 18. **Workflows** ⚡
- **Route**: `/workflows`
- **API**: `GET /api/workflows`, `POST /api/workflows/execute`
- **Tools Used**:
  - Workflow execution engine
  - Task scheduling
  - State management
  - Error handling and retries

### 19. **Snapshots** 📸
- **Route**: `/snapshots`
- **API**: `GET /api/snapshots`, `POST /api/snapshot-rollback/rollback`
- **Tools Used**:
  - System state capture
  - File system snapshots
  - Configuration backup
  - Rollback mechanism

### 20. **Blueprint Generator** 📋
- **Route**: `/blueprints`
- **API**: `POST /api/blueprint-generator/generate`
- **Tools Used**:
  - `ollama` - AI blueprint generation
  - Template engine
  - Configuration generation
  - YAML/JSON generation

### 21. **Plugin Store** 🧩
- **Route**: `/plugins`
- **API**: `GET /api/plugin-store`, `POST /api/plugin-store/install`
- **Tools Used**:
  - Plugin management system
  - Dynamic plugin loading
  - Plugin registry
  - Version management

---

## 🔒 SECURITY Services

### 22. **Security Center** 🔒
- **Route**: `/security`
- **API**: `GET /api/security/*`
- **Tools Used**:
  - Security dashboard aggregation
  - Threat intelligence
  - Security metrics
  - Compliance checking

### 23. **SIEM/SOC** 📊
- **Route**: `/siem`
- **API**: `GET /api/security/siem/*`
- **Tools Used**:
  - Security Information and Event Management
  - Log correlation
  - Event analysis
  - Alert aggregation
  - Incident response automation

### 24. **Secrets Manager** 🔑
- **Route**: `/secrets`
- **API**: `GET /api/unified-secrets/*`
- **Tools Used**:
  - `cryptography` - Secret encryption
  - Vault-like storage
  - Key management
  - Secret rotation
  - Access control

### 25. **Auto-Hardening** 🧱
- **Route**: `/hardening`
- **API**: `POST /api/auto-hardening/harden`
- **Tools Used**:
  - Security configuration automation
  - Compliance checking
  - System hardening scripts
  - Configuration validation

---

## 🚀 DEVOPS Services

### 26. **CI/CD** 🚀
- **Route**: `/cicd`
- **API**: `POST /api/cicd/*`
- **Tools Used**:
  - CI/CD pipeline engine
  - Git integration
  - Build automation
  - Deployment automation
  - Testing frameworks

### 27. **Deployments** 🚀
- **Route**: `/cicd?tab=deployments`
- **API**: `GET /api/cicd/deployments`
- **Tools Used**:
  - Deployment tracking
  - Rollback capabilities
  - Version management
  - Environment management

### 28. **Shadow Deployment** ☁️
- **Route**: `/shadow-deploy`
- **API**: `POST /api/shadow-deployment/*`
- **Tools Used**:
  - Canary deployment
  - Traffic splitting
  - A/B testing
  - Gradual rollout

### 29. **Backup & Restore** 💾
- **Route**: `/backup`
- **API**: `GET /api/backup`, `POST /api/backup/restore`
- **Tools Used**:
  - Backup scheduling
  - Data compression
  - Storage management
  - Restore automation

### 30. **Cost Analyzer** 💰
- **Route**: `/cost-analyzer`
- **API**: `GET /api/cost-analyzer/*`
- **Tools Used**:
  - Resource usage tracking
  - Cost calculation
  - Budget management
  - Cost optimization recommendations

---

## 🏢 PLATFORM Services

### 31. **Tenants** 🏢
- **Route**: `/tenants`
- **API**: `GET /api/settings/tenants`
- **Tools Used**:
  - Multi-tenancy system
  - Tenant isolation
  - Resource allocation
  - Tenant management

### 32. **Billing** 💳
- **Route**: `/billing`
- **API**: `GET /api/billing/*`
- **Tools Used**:
  - Billing calculation
  - Invoice generation
  - Payment processing
  - Subscription management

### 33. **Approvals** ✅
- **Route**: `/approvals`
- **API**: `GET /api/approvals`, `POST /api/approvals`
- **Tools Used**:
  - Approval workflow engine
  - Notification system
  - Role-based approvals
  - Audit trail

### 34. **Knowledge Base** 📚
- **Route**: `/knowledge`
- **API**: `GET /api/knowledge/*`
- **Tools Used**:
  - Knowledge management system
  - Search engine
  - Content management
  - AI-powered search (`ollama`)

### 35. **Audit Trail** 📝
- **Route**: `/audit`
- **API**: `GET /api/audit/*`
- **Tools Used**:
  - SQLite database (`audit.db`)
  - Event logging
  - Audit query system
  - Compliance reporting

### 36. **Settings** ⚙️
- **Route**: `/settings`
- **API**: `GET /api/settings`, `POST /api/settings`
- **Tools Used**:
  - Configuration management
  - Settings persistence
  - User preferences
  - System configuration

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
- **Next.js 16** - React framework
- **React** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Lucide React** - Icons
- **Recharts/Chart.js** - Charts
- **WebSocket** - Real-time communication

### Infrastructure:
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Loki** - Log aggregation
- **Promtail** - Log collection
- **Alert Manager** - Alerting

### Databases:
- **SQLite** - Primary database
  - `audit.db` - Audit trail
  - `incidents.db` - Incidents
- **JSON files** - Configuration storage
  - Memory management
  - Settings
  - User data

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

## 📝 Notes

- **Total Services**: 36 services
- **Total API Endpoints**: 40+ endpoints
- **AI-Powered Services**: 8 services use AI (Ollama)
- **Real-time Services**: 5 services use WebSocket
- **Security Services**: 4 dedicated security services
- **All services are 100% local/offline** - No external API dependencies

