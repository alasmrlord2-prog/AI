# Security AI & Advanced Modules - 100% Local/Offline Mode

## ✅ نظام أمني ذكي + موديولات متقدمة - محلي بالكامل - لا يخرج بايت واحد خارج السيرفر

---

## 📦 الموديولات المكتملة (14 موديول)

### ✅ 1. Zero-Trust Access Control (ABAC)
- نظام صلاحيات متقدم يعتمد على الصفات
- `/api/abac/*`

### ✅ 2. AI Threat Detection (100% Local)
- كشف التهديدات بالذكاء الاصطناعي
- Log Collector + Anomaly Detection + AI Explainer + Auto-Response
- `/api/security/threat-detection/*`

### ✅ 3. Intelligent Log Timeline
- Timeline ذكي للـlogs مع ربط الأحداث
- `/api/logs/timeline/*`

### ✅ 4. Configuration Drift Detector
- كاشف تغييرات الـconfig
- `/api/config/drift/*`

### ✅ 5. Infrastructure Cost Analyzer
- محلل تكاليف البنية التحتية
- `/api/cost/*`

### ✅ 6. User Behavior Engine
- مراقبة سلوك المستخدمين
- `/api/user-behavior/*`

### ✅ 7. Global Search
- محرك بحث شامل (Logs, Files, Workflows, Docs, Configs)
- `/api/search/*`

### ✅ 8. Snapshot + Rollback Engine
- نظام snapshots وrollback (Containers, Volumes, Configs, Full System)
- `/api/snapshots/*`

### ✅ 9. Incident Command Center
- مركز إدارة الحوادث (Timeline, Root Cause, Fixes, Logs, Chat)
- `/api/incidents/command-center/*`

### ✅ 10. Unified Secret Management
- إدارة الأسرار الموحدة (Encryption at rest, Auto rotation, Per-service access)
- `/api/secrets/*`

### ✅ 11. Service Dependency Graph
- خريطة التبعيات بين الخدمات (Containers, Databases, Ports, Connections)
- `/api/services/dependency/*`

---

---

## 🎯 المبدأ الأساسي

**كل شي لوكل، ولا حدا يشم ريحة الـlogs**

- ✅ Agent + AI Security Brain على نفس السيرفر أو VPC مغلقة
- ✅ LLM من Ollama محلي (localhost)
- ✅ لا اتصال مع خدمات خارجية
- ✅ ممنوع: API خارجي، SaaS logging، HTTP requests للخارج

---

## 🏗️ البنية المعمارية

### 4 طبقات - كلها محلية:

#### 1️⃣ Log Collector (جامع اللوغ)
- يراقب ملفات الـlogs: NGINX, FastAPI, systemd, Docker, DB
- يستخدم `watchdog` لمراقبة التغييرات
- يرسل الأحداث عبر callbacks محلية
- **لا يحتاج إنترنت**

#### 2️⃣ Anomaly Detection Engine (العقل الأمني)

**أ) Rules بسيطة:**
- 10 محاولات فاشلة login من IP واحد → suspicious
- استعلامات DB غريبة
- خدمة تعطي 500 بنسبة عالية
- **Python عادي - if/else و counters**

**ب) ML محلي (اختياري):**
- Isolation Forest من scikit-learn
- Models محفوظة على الديسك
- تدريب محلي
- **لا يحتاج إنترنت**

#### 3️⃣ AI Explainer (LLM للتفسير)
- يستخدم Ollama محلي (localhost:11434)
- يشرح التهديدات والحوادث
- **لا يحتاج إنترنت** (Ollama محلي)

#### 4️⃣ Auto-Response (العقاب)
- حظر IP عبر iptables/ufw
- إيقاف container/service
- تعطيل user account
- Lockdown mode
- **كلها أوامر shell محلية**

---

## 📁 الملفات

```
app/services/security_ai/
├── __init__.py
├── collector.py      # Log Collector
├── detector.py       # Anomaly Detection (Rules + ML)
├── explainer.py      # AI Explainer (Ollama)
├── responder.py      # Auto-Response
└── orchestrator.py   # المنسق الرئيسي
```

---

## ⚙️ الإعدادات

في `.env` أو `config.py`:

```python
# Security AI - 100% Local/Offline Mode
OFFLINE_MODE = True  # منع جميع الاتصالات الخارجية
SECURITY_AI_ENABLED = True
SECURITY_AI_AUTO_RESPONSE = False  # تفعيل الاستجابة التلقائية
SECURITY_AI_USE_OLLAMA = True  # استخدام Ollama محلي
SECURITY_AI_LOG_PATHS = [
    "/var/log/nginx/access.log",
    "/var/log/nginx/error.log",
    "/var/log/auth.log",
    "/var/log/app/backend.log",
]
```

---

## 🚀 الاستخدام

### 1. بدء النظام

```python
from app.services.security_ai.orchestrator import get_security_ai_orchestrator

orchestrator = get_security_ai_orchestrator()
orchestrator.start()
```

### 2. API Endpoints

```bash
# بدء النظام الأمني
POST /api/security/threat-detection/start

# الحصول على الحوادث
GET /api/security/threat-detection/incidents?hours=24&severity=high

# حالة النظام
GET /api/security/threat-detection/status

# تحليل logs
POST /api/security/threat-detection/analyze
{
    "log_lines": ["ERROR: SQL injection attempt"],
    "source": "backend"
}
```

---

## 🔒 ضمان 100% محلي

### 1. OFFLINE_MODE Flag

```python
OFFLINE_MODE = True  # في config.py
```

في الكود:
```python
def http_call(...):
    if OFFLINE_MODE:
        raise RuntimeError("External HTTP calls are disabled in OFFLINE_MODE")
```

### 2. Outbound Firewall

منع أي اتصال للخارج من:
- حاوية الـAI
- حاوية الـbackend

### 3. No External Keys

- ❌ لا OpenAI key
- ❌ لا SaaS keys
- ❌ لا Elastic Cloud
- ✅ كلو محلي

---

## 🧠 AI Explainer (Ollama)

### المتطلبات:

```bash
# تثبيت Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# تحميل موديل محلي
ollama pull llama3.2
```

### الاستخدام:

```python
from app.services.security_ai.explainer import get_ai_explainer

explainer = get_ai_explainer()
explanation = explainer.explain_threat(threat)
```

**ملاحظة:** إذا لم يكن Ollama متاحاً، يستخدم rule-based explanations.

---

## 🤖 Auto-Response

### الإجراءات المتاحة:

1. **Block IP** - حظر IP عبر iptables/ufw
2. **Isolate Service** - إيقاف container/service
3. **Disable User** - تعطيل حساب مستخدم
4. **Lockdown Mode** - إغلاق SSH وتقييد الوصول

### تفعيل Auto-Response:

```python
SECURITY_AI_AUTO_RESPONSE = True  # في config
```

**تحذير:** Auto-Response يمكن أن يوقف خدمات حقيقية. استخدم بحذر!

---

## 📊 Anomaly Detection

### Rules-Based (دائماً متاح):

- Failed logins threshold
- Error rate threshold
- IP spike detection
- Unusual user activity

### ML-Based (اختياري - يحتاج scikit-learn):

```bash
pip install scikit-learn
```

- Isolation Forest
- Auto-training على البيانات المحلية
- Models محفوظة في `models/security_ai/`

---

## 🔍 Log Collector

### المسارات المراقبة:

- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/auth.log`
- `/var/log/app/backend.log`
- أي مسار تضيفه في `SECURITY_AI_LOG_PATHS`

### إضافة مسار جديد:

```python
from app.services.security_ai.collector import get_log_collector

collector = get_log_collector()
collector.add_monitored_path("/path/to/logs")
```

---

## 📝 مثال كامل

```python
from app.services.security_ai.orchestrator import get_security_ai_orchestrator

# بدء النظام
orchestrator = get_security_ai_orchestrator()
orchestrator.start()

# تحليل logs
result = orchestrator.analyze_realtime(
    log_lines=[
        "2024-01-01 10:00:00 ERROR: SQL injection attempt detected",
        "2024-01-01 10:01:00 WARN: Failed login from 192.168.1.100"
    ],
    source="backend"
)

# الحصول على الحوادث
incidents = orchestrator.get_incidents(hours=24, severity="high")

# حالة النظام
status = orchestrator.get_status()
```

---

## ✅ التحقق من OFFLINE_MODE

### في الكود:

```python
from app.core.config import get_settings

settings = get_settings()
if settings.OFFLINE_MODE:
    # التأكد من أن كل شيء محلي
    assert "localhost" in ollama_url or "127.0.0.1" in ollama_url
```

### في Runtime:

```python
# أي محاولة لاستدعاء API خارجي ستفشل
if OFFLINE_MODE:
    raise RuntimeError("External connections blocked")
```

---

## 🎯 الخلاصة

✅ **100% محلي** - لا يخرج بايت واحد خارج السيرفر  
✅ **Ollama محلي** - للـAI explanations  
✅ **ML محلي** - scikit-learn على السيرفر  
✅ **Rules محلية** - Python عادي  
✅ **Auto-Response محلي** - iptables, systemctl, docker  
✅ **OFFLINE_MODE** - منع جميع الاتصالات الخارجية  

**النظام جاهز للاستخدام - محلي بالكامل! 🔒**

---

## 📚 الملفات المرجعية

### Security AI
- `app/services/security_ai/` - جميع المكونات
- `app/core/config.py` - الإعدادات
- `app/api/ai_threat_detection.py` - API endpoints

### الموديولات الأخرى
- `app/services/user_behavior_engine.py` - User Behavior
- `app/services/global_search.py` - Global Search
- `app/services/snapshot_rollback.py` - Snapshots & Rollback
- `app/services/incident_command_center.py` - Incident Center
- `app/api/user_behavior.py` - User Behavior API
- `app/api/global_search.py` - Search API
- `app/api/snapshot_rollback.py` - Snapshots API
- `app/api/incident_command_center.py` - Incident Center API

---

## 🎯 ملخص الموديولات

| الموديول | الحالة | API Prefix |
|---------|--------|------------|
| ABAC | ✅ | `/api/abac` |
| AI Threat Detection | ✅ | `/api/security/threat-detection` |
| Log Timeline | ✅ | `/api/logs/timeline` |
| Config Drift | ✅ | `/api/config/drift` |
| Cost Analyzer | ✅ | `/api/cost` |
| User Behavior | ✅ | `/api/user-behavior` |
| Global Search | ✅ | `/api/search` |
| Snapshots | ✅ | `/api/snapshots` |
| Incident Center | ✅ | `/api/incidents/command-center` |
| Secret Management | ✅ | `/api/secrets` |
| Service Dependency | ✅ | `/api/services/dependency` |

**المجموع: 11 موديول مكتمل وجاهز للاستخدام! 🚀**

