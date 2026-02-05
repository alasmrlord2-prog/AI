# 🔧 SHIFTWAVE AI - Services & Tools Documentation

## 📋 جميع الخدمات (Services) والأدوات المستخدمة

---

## 🎯 CORE Services

### 1. **Dashboard** 📊
- **Route**: `/`
- **API**: `GET /api/monitor/server-metrics`
- **Tools Used**:
  - `psutil` - System metrics (CPU, RAM, Disk, Network)
  - `prometheus-client` - Metrics collection
  - FastAPI - API endpoints
  - React/Next.js - Frontend rendering
  - Recharts/Chart.js - Data visualization

### 2. **Agent Console** 💻
- **Route**: `/`
- **API**: `POST /api/chat`
- **Tools Used**:
  - `ollama` - Local AI model (LLM)
  - FastAPI WebSocket - Real-time communication
  - React Chat Components - UI
  - Memory management system - Context retention

### 3. **Global Search** 🔍
- **Route**: `/global-search`
- **API**: `POST /api/global-search/search`
- **Tools Used**:
  - Elasticsearch-like search (local implementation)
  - Full-text search algorithms
  - Indexing system
  - FastAPI - Search endpoints

### 4. **AI Debugger** 🐛
- **Route**: `/debugger`
- **API**: `POST /api/debugger/analyze`
- **Tools Used**:
  - `ollama` - AI model for debugging
  - Code analysis tools
  - Error pattern recognition
  - Log analysis algorithms

---

## 📈 OBSERVABILITY Services

### 5. **Monitoring** 📈
- **Route**: `/monitoring`
- **API**: `GET /api/monitor/server-metrics`, `GET /api/monitoring/*`
- **Tools Used**:
  - `psutil` - System monitoring
  - `prometheus-client` - Metrics collection
  - `docker` - Container monitoring
  - Grafana - Visualization (optional)
  - Prometheus - Metrics storage
  - Real-time WebSocket updates

### 6. **Logs** 📋
- **Route**: `/logs`
- **API**: `GET /api/logs`, `POST /api/logs/search`
- **Tools Used**:
  - Loki - Log aggregation
  - Promtail - Log collection
  - File system monitoring (`watchdog`)
  - Log parsing and filtering
  - Search indexing

### 7. **Incidents** ⚠️
- **Route**: `/incidents`
- **API**: `GET /api/incidents`, `POST /api/incidents`
- **Tools Used**:
  - SQLite database (`incidents.db`)
  - Alert Manager integration
  - Incident tracking system
  - Notification system

### 8. **Incident Center** 🚨
- **Route**: `/incident-center`
- **API**: `POST /api/incident-command-center/*`
- **Tools Used**:
  - Command center orchestration
  - Real-time incident management
  - Multi-user collaboration
  - WebSocket for live updates

### 9. **Visualization** 👁️
- **Route**: `/visualization`
- **API**: `GET /api/visualization/*`
- **Tools Used**:
  - D3.js / Recharts - Data visualization
  - Chart.js - Chart rendering
  - Real-time data streaming
  - Custom visualization components

---

## 🧠 AI & AUTOMATION Services

### 10. **AI Tools** 🧠
- **Route**: `/tools`
- **API**: `GET /api/tools`, `POST /api/tools/execute`
- **Tools Used**:
  - `ollama` - Local AI models
  - Tool execution framework
  - Plugin system
  - Dynamic tool loading

### 11. **Threat Detection** 🛡️
- **Route**: `/threat-detection`
- **API**: `POST /api/security/threat-detection/analyze`
- **Tools Used**:
  - `ollama` - AI threat analysis
  - Pattern recognition algorithms
  - Log analysis engine
  - Anomaly detection (`scikit-learn`)
  - Security AI orchestrator
  - Real-time threat scoring

### 12. **ABAC** 🔐
- **Route**: `/abac`
- **API**: `POST /api/abac/check`, `GET /api/abac/policies`
- **Tools Used**:
  - Attribute-Based Access Control engine
  - Policy evaluation system
  - Context-aware authorization
  - Permission caching
  - SQLite for policy storage

### 13. **Behavior Alerts** 👁️
- **Route**: `/behavior-alerts`
- **API**: `POST /api/behavior-alerts/*`
- **Tools Used**:
  - `scikit-learn` - Anomaly detection
  - User behavior analysis
  - Pattern matching
  - Alert generation system

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

