# 📊 SaaS Workflow Diagrams - Mermaid

هذا الملف يحتوي على جميع الرسوم البيانية للـ SaaS Onboarding Workflow بصيغة Mermaid.

---

## 1. High-Level Architecture

```mermaid
graph TB
    subgraph "External World"
        Client[🏢 Client Company]
        Employees[👥 Employees]
    end

    subgraph "SHIFTWAVE Platform"
        subgraph "CRM Service"
            CRM[📊 CRM Dashboard]
            CRM_API[CRM API]
            CRM_DB[(CRM Database)]
        end

        subgraph "AAA Service"
            AAA[🔐 AAA Dashboard]
            AAA_API[AAA API]
            AAA_DB[(AAA Database)]
            AAA_Files[AAA Files]
        end

        subgraph "AI Agent Service"
            Agent[🤖 AI Agent Dashboard]
            Agent_API[AI Agent API]
            Agent_DB[(Agent Database)]
        end
    end

    Client -->|Register| CRM
    CRM -->|Manage| CRM_API
    CRM_API -->|Store| CRM_DB
    CRM_API -->|Events| AAA_API
    AAA_API -->|Store| AAA_DB
    AAA_API -->|Generate| AAA_Files

    Employees -->|Login| Agent
    Agent -->|Validate| Agent_API
    Agent_API -->|Check| CRM_API
    Agent_API -->|Check| AAA_API
    Agent_API -->|Grant Access| Employees
```

---

## 2. Complete Onboarding Sequence

```mermaid
sequenceDiagram
    participant Client as 🏢 Client
    participant CRM as 📊 CRM
    participant AAA as 🔐 AAA
    participant Portal as 🌐 Portal
    participant Agent as 🤖 AI Agent

    Note over Client,Agent: Phase 1: Registration
    Client->>CRM: Register Company
    CRM->>CRM: Create Tenant
    CRM->>CRM: Create Owner User
    CRM->>AAA: Event: TENANT_CREATED
    CRM->>AAA: Event: USER_CREATED
    AAA->>AAA: Create Identity
    AAA->>AAA: Generate AAA File
    AAA-->>CRM: ✅ AAA File Ready

    Note over Client,Agent: Phase 2: Owner Login
    Client->>Portal: Login
    Portal->>CRM: Validate User
    CRM-->>Portal: ✅ User Active
    Portal->>AAA: Validate AAA File
    AAA-->>Portal: ✅ AAA Valid
    Portal->>Agent: Request Token
    Agent->>CRM: Check Tenant
    Agent->>AAA: Check AAA File
    Agent-->>Portal: ✅ Access Granted

    Note over Client,Agent: Phase 3: Add Employee
    Client->>Portal: Add Employee
    Portal->>CRM: Create User
    CRM->>CRM: Validate Limits
    CRM->>AAA: Event: USER_CREATED
    AAA->>AAA: Generate AAA File
    AAA-->>CRM: ✅ AAA File Ready
    CRM-->>Portal: ✅ User Created

    Note over Client,Agent: Phase 4: Employee Access
    Employees->>Agent: Login
    Agent->>CRM: Validate User
    CRM-->>Agent: ✅ User Active
    Agent->>AAA: Validate AAA File
    AAA-->>Agent: ✅ AAA Valid
    Agent->>CRM: Check Features
    CRM-->>Agent: ✅ Features OK
    Agent-->>Employees: ✅ Access Granted
```

---

## 3. Data Flow Diagram

```mermaid
flowchart TD
    Start([Client Registers]) --> CreateTenant[CRM: Create Tenant]
    CreateTenant --> CreateOwner[CRM: Create Owner User]
    CreateOwner --> SendEvents[CRM: Send Events]
    
    SendEvents --> Event1[TENANT_CREATED Event]
    SendEvents --> Event2[USER_CREATED Event]
    
    Event1 --> AAAInit[AAA: Initialize Tenant]
    Event2 --> AAACreate[AAA: Create Identity]
    
    AAAInit --> AAAPolicies[AAA: Create Policies]
    AAACreate --> AAAFile[AAA: Generate AAA File]
    
    AAAFile --> StoreAAA[Store AAA File]
    StoreAAA --> Ready[✅ Ready for Login]
    
    Ready --> Login[User Logs In]
    Login --> ValidateJWT[Validate JWT Token]
    ValidateJWT --> CheckCRM[Check CRM Status]
    CheckCRM --> CheckAAA[Check AAA File]
    CheckAAA --> CheckSub[Check Subscription]
    CheckSub --> GrantAccess[✅ Grant Access]
    
    GrantAccess --> UseService[User Uses Service]
    UseService --> CheckPerm[Check Permissions]
    CheckPerm --> Allow[✅ Allow] | Deny[❌ Deny]
```

---

## 4. Multi-Tenant Isolation

```mermaid
graph TB
    subgraph "Tenant 1: دجاجتي"
        T1_Owner[Owner: owner@dajajati.com]
        T1_User1[User: ahmed@dajajati.com]
        T1_User2[User: sara@dajajati.com]
        T1_Data[(Tenant 1 Data)]
    end

    subgraph "Tenant 2: وزارة الصحة"
        T2_Owner[Owner: owner@health.gov]
        T2_User1[User: doctor@health.gov]
        T2_Data[(Tenant 2 Data)]
    end

    subgraph "Shared Infrastructure"
        SharedApp[AI Agent Application]
        SharedDB[(Shared Database)]
    end

    T1_Owner -->|Access| SharedApp
    T1_User1 -->|Access| SharedApp
    T1_User2 -->|Access| SharedApp
    T2_Owner -->|Access| SharedApp
    T2_User1 -->|Access| SharedApp

    SharedApp -->|Isolated Query| T1_Data
    SharedApp -->|Isolated Query| T2_Data

    SharedApp -.->|Tenant ID Filter| SharedDB
    SharedDB -->|Tenant 1 Only| T1_Data
    SharedDB -->|Tenant 2 Only| T2_Data
```

---

## 5. Permission Check Flow

```mermaid
flowchart TD
    Request([User Request]) --> ExtractToken[Extract JWT Token]
    ExtractToken --> VerifyJWT[Verify JWT Signature]
    VerifyJWT -->|Invalid| Deny1[❌ 401 Unauthorized]
    VerifyJWT -->|Valid| GetUserID[Get User ID + Tenant ID]
    
    GetUserID --> CheckCRM[Check CRM: User Active?]
    CheckCRM -->|No| Deny2[❌ 403 Forbidden]
    CheckCRM -->|Yes| CheckTenant[Check CRM: Tenant Active?]
    
    CheckTenant -->|No| Deny3[❌ 403 Forbidden]
    CheckTenant -->|Yes| GetAAA[Get AAA File]
    
    GetAAA -->|Not Found| Deny4[❌ 403 No AAA File]
    GetAAA -->|Found| CheckExpired[AAA File Expired?]
    
    CheckExpired -->|Yes| Deny5[❌ 403 AAA Expired]
    CheckExpired -->|No| CheckSub[Check Subscription]
    
    CheckSub -->|Inactive| Deny6[❌ 403 Subscription Inactive]
    CheckSub -->|Active| CheckFeature[Feature in Subscription?]
    
    CheckFeature -->|No| Deny7[❌ 403 Feature Not Available]
    CheckFeature -->|Yes| CheckPerm[Check Permission in AAA]
    
    CheckPerm -->|No| Deny8[❌ 403 Permission Denied]
    CheckPerm -->|Yes| Allow[✅ 200 OK - Grant Access]
```

---

## 6. Event-Driven Architecture

```mermaid
graph LR
    subgraph "CRM Service"
        CRM_Action[User Action]
        CRM_Event[Event Publisher]
    end

    subgraph "Message Queue"
        MQ[Event Bus<br/>RabbitMQ/Kafka]
    end

    subgraph "AAA Service"
        AAA_Listener[Event Listener]
        AAA_Processor[Event Processor]
        AAA_File[AAA File Generator]
    end

    subgraph "AI Agent Service"
        Agent_Listener[Event Listener]
        Agent_Cache[Cache Invalidator]
    end

    CRM_Action -->|Trigger| CRM_Event
    CRM_Event -->|Publish| MQ
    MQ -->|Subscribe| AAA_Listener
    MQ -->|Subscribe| Agent_Listener
    
    AAA_Listener --> AAA_Processor
    AAA_Processor --> AAA_File
    
    Agent_Listener --> Agent_Cache
```

---

## 7. Subscription & Feature Gating

```mermaid
graph TB
    subgraph "Subscription Plans"
        Basic[Basic Plan<br/>Features: ai.agent.chat]
        Pro[Pro Plan<br/>Features: ai.agent.*, monitoring.basic]
        Enterprise[Enterprise Plan<br/>Features: *]
    end

    subgraph "User Permissions"
        Owner[Owner<br/>Permissions: *]
        Admin[Admin<br/>Permissions: ai.agent.*, monitoring.*]
        Analyst[Analyst<br/>Permissions: ai.agent.chat, logs.viewer]
    end

    subgraph "Final Access"
        Access1[✅ ai.agent.chat]
        Access2[✅ monitoring.basic]
        Access3[✅ logs.viewer]
        Denied[❌ logs.edit]
    end

    Basic --> Access1
    Pro --> Access1
    Pro --> Access2
    Enterprise --> Access1
    Enterprise --> Access2
    Enterprise --> Access3

    Owner --> Access1
    Owner --> Access2
    Owner --> Access3
    Admin --> Access1
    Admin --> Access2
    Analyst --> Access1
    Analyst --> Access3

    Analyst -.->|No Permission| Denied
```

---

## 8. AAA File Structure

```mermaid
graph TD
    AAAFile[AAA File] --> UserInfo[User Information]
    AAAFile --> Permissions[Permissions List]
    AAAFile --> ABAC[ABAC Attributes]
    AAAFile --> Metadata[Metadata]

    UserInfo --> UID[user_id]
    UserInfo --> TID[tenant_id]
    UserInfo --> Email[email]

    Permissions --> Perm1[ai.agent.chat]
    Permissions --> Perm2[logs.viewer]
    Permissions --> Perm3[monitoring.view]

    ABAC --> Role[role: analyst]
    ABAC --> Dept[department: IT]
    ABAC --> Project[project: null]

    Metadata --> Version[policy_version: 1.0]
    Metadata --> Created[created_at]
    Metadata --> Expires[expires_at]
```

---

## 9. Error Handling Flow

```mermaid
flowchart TD
    Error([Error Occurs]) --> ErrorType{Error Type?}
    
    ErrorType -->|401| AuthError[Authentication Error]
    ErrorType -->|403| ForbiddenError[Forbidden Error]
    ErrorType -->|404| NotFoundError[Not Found Error]
    ErrorType -->|500| ServerError[Server Error]
    
    AuthError --> AuthMsg[Invalid credentials<br/>Token expired<br/>Token invalid]
    AuthMsg --> LogAuth[Log Security Event]
    
    ForbiddenError --> ForbiddenCheck{Reason?}
    ForbiddenCheck -->|No AAA| NoAAA[No AAA File]
    ForbiddenCheck -->|Inactive| Inactive[User/Tenant Inactive]
    ForbiddenCheck -->|No Permission| NoPerm[Permission Denied]
    ForbiddenCheck -->|No Feature| NoFeature[Feature Not in Subscription]
    
    NoAAA --> LogForbidden[Log Access Denied]
    Inactive --> LogForbidden
    NoPerm --> LogForbidden
    NoFeature --> LogForbidden
    
    NotFoundError --> NotFoundMsg[User not found<br/>Tenant not found<br/>AAA file not found]
    NotFoundMsg --> LogNotFound[Log Not Found Event]
    
    ServerError --> ServerMsg[Internal server error<br/>Database error<br/>Service unavailable]
    ServerMsg --> LogServer[Log Error + Stack Trace]
    
    LogAuth --> Alert[Alert Security Team]
    LogForbidden --> Alert
    LogNotFound --> Alert
    LogServer --> AlertOps[Alert Operations Team]
```

---

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX Load Balancer]
    end

    subgraph "CRM Service Cluster"
        CRM1[CRM Instance 1]
        CRM2[CRM Instance 2]
        CRM3[CRM Instance 3]
        CRM_DB[(CRM Database<br/>PostgreSQL)]
    end

    subgraph "AAA Service Cluster"
        AAA1[AAA Instance 1]
        AAA2[AAA Instance 2]
        AAA3[AAA Instance 3]
        AAA_DB[(AAA Database<br/>PostgreSQL)]
    end

    subgraph "AI Agent Service Cluster"
        Agent1[Agent Instance 1]
        Agent2[Agent Instance 2]
        Agent3[Agent Instance 3]
        Agent_DB[(Agent Database<br/>PostgreSQL)]
    end

    subgraph "Message Queue"
        MQ[RabbitMQ/Kafka<br/>Event Bus]
    end

    subgraph "Cache Layer"
        Redis[(Redis Cache)]
    end

    LB --> CRM1
    LB --> CRM2
    LB --> CRM3
    LB --> AAA1
    LB --> AAA2
    LB --> AAA3
    LB --> Agent1
    LB --> Agent2
    LB --> Agent3

    CRM1 --> CRM_DB
    CRM2 --> CRM_DB
    CRM3 --> CRM_DB

    AAA1 --> AAA_DB
    AAA2 --> AAA_DB
    AAA3 --> AAA_DB

    Agent1 --> Agent_DB
    Agent2 --> Agent_DB
    Agent3 --> Agent_DB

    CRM1 --> MQ
    CRM2 --> MQ
    CRM3 --> MQ

    AAA1 --> MQ
    AAA2 --> MQ
    AAA3 --> MQ

    Agent1 --> Redis
    Agent2 --> Redis
    Agent3 --> Redis
```

---

## 11. Security Layers

```mermaid
graph TB
    Request([Incoming Request]) --> Layer1[Layer 1: Network Security]
    Layer1 -->|DDoS Protection| Layer2[Layer 2: Rate Limiting]
    Layer2 -->|IP Whitelist| Layer3[Layer 3: Authentication]
    Layer3 -->|JWT Validation| Layer4[Layer 4: Authorization]
    Layer4 -->|CRM Check| Layer5[Layer 5: AAA Validation]
    Layer5 -->|Permission Check| Layer6[Layer 6: ABAC Rules]
    Layer6 -->|Feature Check| Layer7[Layer 7: Subscription Check]
    Layer7 -->|Audit Log| Allow[✅ Allow Request]

    Layer1 -.->|Block| Block1[❌ Blocked]
    Layer2 -.->|Block| Block2[❌ Rate Limited]
    Layer3 -.->|Block| Block3[❌ Unauthorized]
    Layer4 -.->|Block| Block4[❌ Forbidden]
    Layer5 -.->|Block| Block5[❌ No AAA]
    Layer6 -.->|Block| Block6[❌ No Permission]
    Layer7 -.->|Block| Block7[❌ No Feature]
```

---

## 12. Monitoring & Observability

```mermaid
graph TB
    subgraph "Services"
        CRM[CRM Service]
        AAA[AAA Service]
        Agent[AI Agent Service]
    end

    subgraph "Metrics Collection"
        Prometheus[Prometheus<br/>Metrics]
    end

    subgraph "Log Aggregation"
        Loki[Loki<br/>Logs]
    end

    subgraph "Tracing"
        Jaeger[Jaeger<br/>Distributed Tracing]
    end

    subgraph "Visualization"
        Grafana[Grafana<br/>Dashboards]
    end

    subgraph "Alerting"
        AlertManager[AlertManager<br/>Alerts]
    end

    CRM -->|Metrics| Prometheus
    AAA -->|Metrics| Prometheus
    Agent -->|Metrics| Prometheus

    CRM -->|Logs| Loki
    AAA -->|Logs| Loki
    Agent -->|Logs| Loki

    CRM -->|Traces| Jaeger
    AAA -->|Traces| Jaeger
    Agent -->|Traces| Jaeger

    Prometheus --> Grafana
    Loki --> Grafana
    Jaeger --> Grafana

    Prometheus --> AlertManager
    AlertManager -->|Email/Slack| OpsTeam[Operations Team]
```

---

## كيفية استخدام هذه الرسوم البيانية

### في Markdown
```markdown
```mermaid
[Paste diagram code here]
```
```

### في Mermaid Live Editor
1. افتح [https://mermaid.live](https://mermaid.live)
2. الصق كود الرسم البياني
3. احفظ كـ PNG أو SVG

### في GitHub/GitLab
GitHub و GitLab يدعمان Mermaid تلقائياً في ملفات Markdown.

### في الوثائق
يمكن استخدام هذه الرسوم في:
- README.md
- API Documentation
- Architecture Documentation
- Presentations

---

**تم إنشاء هذا الملف بواسطة:** Shiftwave Team  
**آخر تحديث:** 2024-01-15  
**الإصدار:** 1.0.0

