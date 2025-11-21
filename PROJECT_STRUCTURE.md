# 📁 SHIFTWAVE AI - Project Structure

## 🗂️ Root Directory
```
ai-agent/
├── backend/              # Backend (Python/FastAPI)
├── frontend/             # Frontend (Next.js/React)
├── alertmanager/         # Alert Manager configs
├── grafana/              # Grafana dashboards
├── loki/                 # Loki configs
├── prometheus/           # Prometheus configs
├── promtail/             # Promtail configs
├── docker-compose.yml    # Docker Compose for dev
├── docker-compose.prod.yml  # Docker Compose for production
└── README.md
```

---

## 🎨 Frontend Structure (`/frontend`)

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home/Dashboard page
│   ├── globals.css              # Global styles
│   ├── theme-script.tsx         # Theme initialization
│   ├── favicon.ico
│   │
│   ├── login/                   # Login page
│   ├── abac/                    # ABAC page
│   ├── agent-mesh/              # Agent Mesh page
│   ├── approvals/               # Approvals page
│   ├── audit/                   # Audit Trail page
│   ├── backup/                  # Backup & Restore page
│   ├── behavior-alerts/         # Behavior Alerts page
│   ├── billing/                 # Billing page
│   ├── blueprints/              # Blueprint Generator page
│   ├── cicd/                    # CI/CD page
│   ├── code-review/             # Code Review page
│   ├── cost-analyzer/           # Cost Analyzer page
│   ├── debugger/                # AI Debugger page
│   ├── digital-twin/            # Digital Twin page
│   ├── global-search/           # Global Search page
│   ├── hardening/               # Auto-Hardening page
│   ├── incident-center/         # Incident Center page
│   ├── incidents/               # Incidents page
│   ├── knowledge/               # Knowledge Base page
│   ├── logs/                    # Logs page
│   ├── monitor/                 # Monitor page
│   ├── monitoring/              # Monitoring page
│   ├── performance-tuner/      # Performance Tuner page
│   ├── plugins/                 # Plugin Store page
│   ├── secrets/                 # Secrets Manager page
│   ├── security/                # Security Center page
│   ├── settings/                # Settings page
│   ├── siem/                    # SIEM/SOC page
│   ├── snapshots/               # Snapshots page
│   ├── soc/                     # SOC page
│   ├── tenants/                 # Tenants page
│   ├── threat-detection/         # Threat Detection page
│   ├── tools/                   # AI Tools page
│   ├── visualization/           # Visualization page
│   ├── workflow-builder/        # Workflow Builder page
│   └── workflows/               # Workflows page
│
├── components/                  # React Components
│   ├── layout/                  # Layout components
│   │   ├── Sidebar.tsx         # Main sidebar navigation
│   │   └── Header.tsx          # Header component (TopNav wrapper)
│   │
│   ├── TopNav.tsx              # Top navigation bar (AWS-style)
│   ├── ServicesDrawer.tsx       # Services drawer (AWS-style)
│   ├── FavoritesBar.tsx         # Favorites bar
│   │
│   ├── alerts/                  # Alert components
│   │   └── AlertNotification.tsx
│   │
│   ├── charts/                  # Chart components
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   └── PieChart.tsx
│   │
│   ├── chat/                   # Chat components
│   │   ├── ChatBox.tsx
│   │   ├── ChatContainer.tsx
│   │   └── ChatMessage.tsx
│   │
│   └── ui/                     # UI components (shadcn/ui)
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── scroll-area.tsx
│       ├── switch.tsx
│       ├── textarea.tsx
│       └── theme-toggle.tsx
│
├── hooks/                       # Custom React Hooks
│   ├── useFavorites.ts         # Favorites management hook
│   └── useRecent.ts            # Recent pages tracking hook
│
├── config/                      # Configuration files
│   └── services.ts             # Services configuration (AWS-style)
│
├── lib/                         # Utility libraries
│   ├── api.ts                  # API client
│   ├── i18n.ts                 # Internationalization
│   └── utils.ts                # Utility functions
│
├── locales/                     # Translation files
│   ├── ar/                     # Arabic translations
│   │   └── common.json
│   └── en/                     # English translations
│       └── common.json
│
├── public/                      # Static assets
│   ├── shiftwave-logo.svg      # Main logo
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
│
├── __tests__/                   # Test files
│
├── package.json                 # Dependencies
├── package-lock.json
├── tsconfig.json                # TypeScript config
├── next.config.ts               # Next.js config
├── tailwind.config.js           # Tailwind CSS config
├── postcss.config.mjs            # PostCSS config
├── eslint.config.mjs             # ESLint config
├── jest.config.js               # Jest config
├── components.json              # shadcn/ui config
│
├── Dockerfile                   # Docker image
├── env.example                  # Environment variables example
│
├── start.sh                     # Start script
├── stop.sh                      # Stop script
├── restart.sh                   # Restart script
│
└── Documentation/
    ├── BRAND_SYSTEM.md          # Brand guidelines
    ├── SHIFTWAVE_THEME_README.md
    ├── SHIFTWAVE_THEME_EXAMPLES.md
    └── THEME_DEBUG.md
```

---

## 🐍 Backend Structure (`/backend`)

```
backend/
├── app/                         # Main application
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── auth.py                 # Authentication
│   ├── pending_actions.py      # Pending actions handler
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── abac.py             # ABAC API
│   │   ├── agent.py            # Agent API
│   │   ├── ai_code_review.py   # AI Code Review
│   │   ├── ai_performance_tuner.py
│   │   ├── ai_threat_detection.py  # Threat Detection
│   │   ├── ai_workflow_builder.py
│   │   ├── approvals.py        # Approvals API
│   │   ├── audit.py            # Audit Trail API
│   │   ├── auth.py             # Auth API
│   │   ├── auto_hardening.py   # Auto-Hardening API
│   │   ├── backup.py           # Backup API
│   │   ├── behavior_alerts.py  # Behavior Alerts API
│   │   ├── billing.py          # Billing API
│   │   ├── blueprint_generator.py
│   │   ├── chat.py             # Chat API
│   │   ├── cicd.py             # CI/CD API
│   │   ├── config_drift.py     # Config Drift API
│   │   ├── cost_analyzer.py    # Cost Analyzer API
│   │   ├── debugger.py         # AI Debugger API
│   │   ├── digital_twin.py     # Digital Twin API
│   │   ├── distributed_agent_mesh.py
│   │   ├── filesystem.py       # Filesystem API
│   │   ├── global_search.py    # Global Search API
│   │   ├── incident_command_center.py
│   │   ├── incidents.py       # Incidents API
│   │   ├── intelligent_log_timeline.py
│   │   ├── kernel_metrics.py   # Kernel Metrics API
│   │   ├── knowledge.py        # Knowledge Base API
│   │   ├── logs.py             # Logs API
│   │   ├── monitor.py          # Monitor API
│   │   ├── monitoring.py       # Monitoring API
│   │   ├── permissions.py     # Permissions API
│   │   ├── plugin_store.py    # Plugin Store API
│   │   ├── prometheus.py       # Prometheus API
│   │   ├── security.py        # Security API
│   │   ├── service_dependency.py
│   │   ├── settings.py        # Settings API
│   │   ├── shadow_deployment.py
│   │   ├── snapshot_rollback.py
│   │   ├── tools.py           # Tools API
│   │   ├── unified_secrets.py  # Secrets Manager API
│   │   ├── user_behavior.py    # User Behavior API
│   │   ├── visualization.py   # Visualization API
│   │   ├── websocket.py       # WebSocket API
│   │   └── workflows.py       # Workflows API
│   │
│   ├── agent/                  # Agent logic
│   ├── core/                   # Core functionality
│   ├── docs/                   # API documentation
│   ├── exceptions/             # Custom exceptions
│   ├── logs/                   # Log files
│   ├── memory/                 # Memory management
│   │   ├── memory.json
│   │   ├── settings.json
│   │   ├── users.json
│   │   └── long_memory.json
│   │
│   ├── models/                 # Database models
│   ├── monitoring/             # Monitoring logic
│   ├── services/               # Business logic services
│   ├── tools/                  # Tools and utilities
│   └── utils/                  # Utility functions
│
├── database/                   # Database files
├── digital_twin/               # Digital Twin logic
├── migrations/                 # Database migrations
├── models/                     # Additional models
├── plugins/                    # Plugin system
├── snapshots/                  # System snapshots
├── tests/                      # Test files
├── vault/                      # Vault storage
│
├── alembic.ini                 # Alembic config
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest config
│
├── Dockerfile                  # Docker image
├── backend-compose.yml         # Docker Compose config
├── env.example                 # Environment variables example
│
├── start.sh                    # Start script
├── stop.sh                     # Stop script
├── restart.sh                  # Restart script
│
├── audit.db                    # Audit database
├── incidents.db                # Incidents database
└── backend.log                 # Backend logs
```

---

## 🔧 Configuration Files

### Frontend Config Files:
- `package.json` - Node.js dependencies
- `tsconfig.json` - TypeScript configuration
- `next.config.ts` - Next.js configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `postcss.config.mjs` - PostCSS configuration
- `eslint.config.mjs` - ESLint configuration
- `jest.config.js` - Jest test configuration
- `components.json` - shadcn/ui configuration

### Backend Config Files:
- `requirements.txt` - Python dependencies
- `alembic.ini` - Database migration configuration
- `pytest.ini` - Pytest configuration

### Docker Files:
- `docker-compose.yml` - Development Docker Compose
- `docker-compose.prod.yml` - Production Docker Compose
- `frontend/Dockerfile` - Frontend Docker image
- `backend/Dockerfile` - Backend Docker image

---

## 📊 Monitoring & Observability

```
├── alertmanager/               # Alert Manager configs
├── grafana/                    # Grafana dashboards
│   └── provisioning/
│       └── dashboards/
│           ├── ai-backend-simple.json
│           └── ai-backend-dashboard.json
├── loki/                       # Loki configs
├── prometheus/                 # Prometheus configs
└── promtail/                   # Promtail configs
```

---

## 🎯 Key Features Structure

### Navigation System:
- `components/TopNav.tsx` - AWS-style top navigation
- `components/ServicesDrawer.tsx` - Services drawer
- `components/FavoritesBar.tsx` - Favorites bar
- `components/layout/Sidebar.tsx` - Main sidebar
- `config/services.ts` - Services configuration

### State Management:
- `hooks/useFavorites.ts` - Favorites management
- `hooks/useRecent.ts` - Recent pages tracking

### API Integration:
- `lib/api.ts` - API client
- `backend/app/api/*.py` - All API endpoints

---

## 📝 Notes

- **Frontend**: Next.js 16 with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), SQLite databases
- **Styling**: Custom Shiftwave theme system with dark/light mode
- **Navigation**: AWS-style navigation with Services Drawer
- **State**: React hooks for favorites and recent pages
- **API**: RESTful API with WebSocket support

