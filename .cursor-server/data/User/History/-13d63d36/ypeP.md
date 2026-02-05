# 🔧 الأدوات المستخدمة في الخدمات

## 📋 نظرة عامة

هذا الملف يوضح جميع الأدوات (Tools) المستخدمة في خدمات المشروع الثلاثة:
1. **Security Service** - خدمة الأمان
2. **DevOps Service** - خدمة CI/CD والنشر
3. **AI & Automation Service** - خدمة الذكاء الاصطناعي والأتمتة

---

## 🔒 Security Service - أدوات الأمان

### أدوات الفحص الأساسية (Basic Scanners)

#### 1. Repository Scanner (`repo_scanner.py`)
- **الوظيفة:** فحص المستودعات (Repositories) للبحث عن الأسرار والمعلومات الحساسة
- **الأدوات المستخدمة:**
  - `grep` - للبحث عن الأنماط
  - `find` - للبحث عن الملفات
  - Python regex patterns - للبحث عن الأسرار
- **أنواع الفحص:**
  - API Keys
  - Passwords
  - Tokens
  - SSH Keys
  - Database credentials

**الكود المستخدم:**
```python
import os
import re
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, SECRET_PATTERNS, resolve_path

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
def scan_repo(path: str = "/app", max_files: int = 1000) -> Dict[str, Any]:
    """Scan repository for secrets and security issues"""
    results = {
        "path": resolved_path,
        "secrets_found": [],
        "risky_files": [],
        "summary": {
            "total_files": 0,
            "scanned_files": 0,
            "secrets_count": 0,
        }
    }
    
    # Smart exclude patterns
    excluded = [
        ".git", "__pycache__", "node_modules", ".next",
        "venv", "env", ".env", ".pyc", ".log",
    ]
    
    root = Path(resolved_path)
    for file_path in root.rglob("*"):
        if file_count >= max_files:
            break
        
        # Skip excluded patterns
        if any(exc in str(file_path) for exc in excluded):
            continue
        
        # Read file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Scan for secrets using regex patterns
        for secret_type, patterns in SECRET_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count("\n") + 1
                    file_secrets.append({
                        "type": secret_type,
                        "line": line_num,
                        "preview": secret_preview,
                    })
    
    # Calculate risk score
    results["risk_score"] = calculate_risk_score(results["summary"])
    return results
```

#### 2. Infrastructure Scanner (`infra_scanner.py`)
- **الوظيفة:** فحص ملفات البنية التحتية (Infrastructure as Code)
- **الأدوات المستخدمة:**
  - `grep` - للبحث في ملفات التكوين
  - File parsing - لتحليل YAML/JSON
- **أنواع الملفات المفحوصة:**
  - Docker Compose files
  - Kubernetes manifests
  - Terraform files
  - Ansible playbooks
  - Cloud configuration files

#### 3. Network Scanner (`network_scanner.py`)
- **الوظيفة:** فحص الشبكة للأمان
- **الأدوات المستخدمة:**
  - `netstat` / `ss` - لفحص الاتصالات المفتوحة
  - `iptables` - لفحص قواعد الجدار الناري
  - `tcpdump` - لتحليل حركة الشبكة
  - Python socket library - للاتصال بالمنافذ

#### 4. System Scanner (`system_scanner.py`)
- **الوظيفة:** فحص النظام للأمان
- **الأدوات المستخدمة:**
  - `ps` - لفحص العمليات
  - `lsof` - لفحص الملفات المفتوحة
  - `df` - لفحص مساحة القرص
  - `who` / `w` - لفحص المستخدمين المتصلين
  - `/proc` filesystem - لفحص معلومات النظام

#### 5. Docker Scanner (`docker_scanner.py`)
- **الوظيفة:** فحص Docker containers والصور
- **الأدوات المستخدمة:**
  - `docker` CLI - لفحص containers
  - `docker-compose` - لفحص التكوينات
  - Docker API - للوصول لبيانات Docker

#### 6. Log Scanner (`log_scanner.py`)
- **الوظيفة:** فحص السجلات (Logs) للبحث عن مشاكل الأمان
- **الأدوات المستخدمة:**
  - `grep` - للبحث في السجلات
  - `tail` / `head` - لقراءة السجلات
  - Python file reading - لتحليل السجلات
- **أنواع الفحص:**
  - Failed login attempts
  - Unauthorized access
  - Suspicious activities
  - Error patterns

#### 7. Vulnerability Scanner (`vulnerability_scanner.py`)
- **الوظيفة:** فحص الثغرات الأمنية
- **الأدوات المستخدمة:**
  - Package managers (`apt`, `pip`, `npm`) - لفحص الحزم المثبتة
  - CVE databases - للبحث عن الثغرات المعروفة
  - Version checking - لمقارنة الإصدارات

#### 8. File Integrity Scanner (`file_integrity_scanner.py`)
- **الوظيفة:** فحص سلامة الملفات
- **الأدوات المستخدمة:**
  - `md5sum` / `sha256sum` - لحساب checksums
  - `stat` - لفحص معلومات الملفات
  - File system monitoring - لمراقبة التغييرات

#### 9. Malware Scanner (`malware_scanner.py`)
- **الوظيفة:** فحص البرمجيات الخبيثة
- **الأدوات المستخدمة:**
  - File signature scanning
  - Pattern matching
  - Heuristic analysis

#### 10. Intrusion Detection Scanner (`ids_scanner.py`)
- **الوظيفة:** كشف محاولات الاختراق
- **الأدوات المستخدمة:**
  - Log analysis
  - Network traffic analysis
  - Anomaly detection

#### 11. Port Scanner (`port_scanner.py`)
- **الوظيفة:** فحص المنافذ المفتوحة
- **الأدوات المستخدمة:**
  - `nmap` (إذا متوفر)
  - Python socket library
  - `nc` (netcat)

#### 12. Penetration Scanner (`penetration_scanner.py`)
- **الوظيفة:** اختبار الاختراق
- **الأدوات المستخدمة:**
  - Vulnerability assessment
  - Exploit testing
  - Security configuration review

### أدوات الأمان المتقدمة (Advanced Security Tools)

#### 1. Threat Intelligence (`advanced_security_tools.py`)
- **الوظيفة:** تحليل التهديدات
- **الأدوات المستخدمة:**
  - IP reputation databases
  - Domain analysis
  - Malware databases

#### 2. Network Forensics
- **الوظيفة:** تحليل حركة الشبكة
- **الأدوات المستخدمة:**
  - `tcpdump` - لالتقاط الحزم
  - `wireshark` (إذا متوفر)
  - Packet analysis libraries

#### 3. Web Vulnerability Scanner
- **الوظيفة:** فحص تطبيقات الويب
- **الأدوات المستخدمة:**
  - HTTP requests
  - OWASP Top 10 checks
  - SQL injection testing
  - XSS testing

#### 4. Container Security Scanner
- **الوظيفة:** فحص أمان الحاويات
- **الأدوات المستخدمة:**
  - `docker` CLI
  - Container image scanning
  - Configuration analysis

#### 5. Kubernetes Security Scanner
- **الوظيفة:** فحص أمان Kubernetes
- **الأدوات المستخدمة:**
  - `kubectl` - للوصول لـ Kubernetes
  - RBAC analysis
  - Network policies review
  - Security contexts check

#### 6. AWS Security Scanner
- **الوظيفة:** فحص أمان AWS
- **الأدوات المستخدمة:**
  - AWS CLI (`aws`)
  - IAM policy analysis
  - S3 bucket security
  - Security groups review

#### 7. Memory Forensics
- **الوظيفة:** تحليل الذاكرة
- **الأدوات المستخدمة:**
  - `/proc` filesystem
  - Memory dumps analysis

#### 8. Disk Forensics
- **الوظيفة:** تحليل القرص
- **الأدوات المستخدمة:**
  - File system analysis
  - Deleted file recovery
  - Metadata analysis

#### 9. Password Audit
- **الوظيفة:** فحص كلمات المرور
- **الأدوات المستخدمة:**
  - Password strength checking
  - Common password detection
  - Hash analysis

#### 10. Compliance Checker
- **الوظيفة:** فحص الامتثال للمعايير
- **المعايير المدعومة:**
  - CIS Benchmarks
  - NIST
  - PCI-DSS
  - GDPR

#### 11. Burp Suite Integration
- **الوظيفة:** فحص تطبيقات الويب باستخدام Burp Suite
- **الأدوات المستخدمة:**
  - Burp Suite API
  - Web application scanning

#### 12. Metasploit Integration
- **الوظيفة:** اختبار الاختراق باستخدام Metasploit
- **الأدوات المستخدمة:**
  - Metasploit Framework
  - Exploit modules

### أدوات المراقبة (Monitoring Tools)

#### SIEM Monitor (`siem_monitor.py`)
- **الوظيفة:** مراقبة الأحداث الأمنية
- **الأدوات المستخدمة:**
  - Event logging
  - Real-time monitoring
  - Alert generation

---

## 🚀 DevOps Service - أدوات CI/CD والنشر

### أدوات Git

#### 1. Git Operations
- **الأدوات المستخدمة:**
  - `git` CLI - لجميع عمليات Git
  - `git clone` - لاستنساخ المستودعات
  - `git pull` - لسحب التحديثات
  - `git branch` - لإدارة الفروع
  - `git log` - لعرض السجلات

### أدوات CI/CD

#### 1. Pipeline Runner
- **الوظيفة:** تشغيل خطوط الأنابيب (Pipelines)
- **الأدوات المستخدمة:**
  - `bash` - لتشغيل سكربتات Pipeline
  - Shell scripts (`.shiftwave/pipeline.sh`)
  - Environment variables management

#### 2. Repository Management
- **الوظيفة:** إدارة المستودعات
- **الأدوات المستخدمة:**
  - Git operations
  - File system operations
  - Path management

### أدوات النشر (Deployment Tools)

#### 1. Docker Compose Deployment
- **الوظيفة:** النشر باستخدام Docker Compose
- **الأدوات المستخدمة:**
  - `docker compose` - لبناء وتشغيل الخدمات
  - `docker compose pull` - لسحب الصور
  - `docker compose up` - لبدء الخدمات
  - `docker compose ps` - لفحص الحالة

#### 2. Kubernetes Deployment
- **الوظيفة:** النشر على Kubernetes
- **الأدوات المستخدمة:**
  - `kubectl` - لـ Kubernetes CLI
  - `kubectl apply` - لتطبيق الـ manifests
  - `kubectl get` - لفحص الموارد
  - `kubectl describe` - لعرض التفاصيل
  - YAML parsing - لتحليل ملفات Kubernetes

#### 3. RSync Deployment
- **الوظيفة:** النشر باستخدام RSync
- **الأدوات المستخدمة:**
  - `rsync` - لمزامنة الملفات
  - SSH - للاتصال بالخوادم البعيدة
  - File synchronization

### أدوات إضافية

#### 1. YAML Parser
- **الوظيفة:** تحليل ملفات YAML
- **الأدوات المستخدمة:**
  - Python `yaml` library
  - JSON conversion

#### 2. Subprocess Management
- **الوظيفة:** إدارة العمليات
- **الأدوات المستخدمة:**
  - Python `subprocess` module
  - Process monitoring
  - Log collection

---

## 🤖 AI & Automation Service - أدوات الذكاء الاصطناعي والأتمتة

### أدوات AI الأساسية

#### 1. Ollama Integration (`core_llm.py`)
- **الوظيفة:** التفاعل مع نماذج الذكاء الاصطناعي
- **الأدوات المستخدمة:**
  - `requests` - للاتصال بـ Ollama API
  - Ollama API endpoints:
    - `/api/tags` - لعرض النماذج المتاحة
    - `/api/generate` - لتوليد النصوص
    - `/api/chat` - للمحادثة
- **النماذج المدعومة:**
  - `llama3.2:1b` (افتراضي)
  - أي نموذج متوفر في Ollama

#### 2. LLM Functions
- **الوظائف المتوفرة:**
  - `llm_text()` - توليد نص عادي
  - `llm_json()` - توليد JSON منظم
  - `_call_ollama()` - استدعاء مباشر لـ Ollama

### أدوات الأتمتة

#### 1. Agent Core (`agent_core.py`, `agent.py`)
- **الوظيفة:** نواة الوكيل الذكي
- **الأدوات المستخدمة:**
  - Think-and-Act framework
  - Tool calling
  - Decision making

#### 2. Tool Integration
- **الأدوات المتكاملة:**
  - Security scanners
  - File operations
  - Network operations
  - System commands

### أدوات إضافية

#### 1. Chat Interface (`chat.py`)
- **الوظيفة:** واجهة المحادثة
- **الأدوات المستخدمة:**
  - WebSocket - للاتصال المباشر
  - REST API - للطلبات

#### 2. Workflow Builder (`ai_workflow_builder.py`)
- **الوظيفة:** بناء سير العمل
- **الأدوات المستخدمة:**
  - AI-powered workflow generation
  - Task automation

#### 3. Code Review (`ai_code_review.py`)
- **الوظيفة:** مراجعة الكود باستخدام AI
- **الأدوات المستخدمة:**
  - Code analysis
  - Security review
  - Best practices checking

---

## 📊 ملخص الأدوات حسب الخدمة

### Security Service
- **أدوات النظام:** `grep`, `find`, `netstat`, `ss`, `ps`, `lsof`, `df`, `who`, `w`
- **أدوات Docker:** `docker`, `docker-compose`
- **أدوات الشبكة:** `tcpdump`, `nmap`, `nc` (netcat)
- **أدوات الأمان:** `iptables`, checksums (`md5sum`, `sha256sum`)
- **مكتبات Python:** regex, socket, file operations

### DevOps Service
- **أدوات Git:** `git` (clone, pull, branch, log)
- **أدوات Docker:** `docker compose`
- **أدوات Kubernetes:** `kubectl`
- **أدوات النشر:** `rsync`, `ssh`
- **مكتبات Python:** `subprocess`, `yaml`, `json`

### AI & Automation Service
- **أدوات AI:** Ollama API (`/api/tags`, `/api/generate`, `/api/chat`)
- **مكتبات Python:** `requests`, `json`
- **بروتوكولات:** HTTP, WebSocket

---

## 🔗 التكامل بين الخدمات

- **Security + DevOps:** فحص أمان الكود قبل النشر
- **AI + Security:** تحليل ذكي للتهديدات
- **AI + DevOps:** أتمتة ذكية لعمليات CI/CD
- **All Services:** تكامل شامل عبر API موحد

---

## 📝 ملاحظات

1. **الأدوات الاختيارية:** بعض الأدوات مثل `nmap`, `wireshark`, `metasploit` قد لا تكون مثبتة بشكل افتراضي
2. **الصلاحيات:** بعض الأدوات تحتاج صلاحيات root أو sudo
3. **التوفر:** النظام يتحقق من توفر الأدوات قبل استخدامها
4. **البدائل:** النظام يوفر بدائل عند عدم توفر أداة معينة

