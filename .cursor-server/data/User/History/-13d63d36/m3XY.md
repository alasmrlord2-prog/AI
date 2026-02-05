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

**SECRET_PATTERNS (من base.py):**
```python
SECRET_PATTERNS = {
    "api_key": [
        r'api[_-]?key["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'apikey["\s:=]+([a-zA-Z0-9_\-]{20,})',
    ],
    "password": [
        r'password["\s:=]+([^\s"\']{8,})',
        r'passwd["\s:=]+([^\s"\']{8,})',
        r'pwd["\s:=]+([^\s"\']{8,})',
    ],
    "token": [
        r'token["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'bearer["\s]+([a-zA-Z0-9_\-\.]{20,})',
    ],
    "secret": [
        r'secret["\s:=]+([a-zA-Z0-9_\-]{16,})',
        r'secret[_-]key["\s:=]+([a-zA-Z0-9_\-]{16,})',
    ],
    "aws_key": [
        r'AWS[_\s]?ACCESS[_\s]?KEY[_\s]?ID["\s:=]+([A-Z0-9]{20})',
        r'AWS[_\s]?SECRET[_\s]?ACCESS[_\s]?KEY["\s:=]+([A-Za-z0-9/+=]{40})',
    ],
    "private_key": [
        r'-----BEGIN[_\s]?(RSA|EC|DSA|OPENSSH)[_\s]?PRIVATE[_\s]?KEY-----',
    ],
}
```

**scan_repo function:**
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
  - Python regex - للبحث عن الأنماط
- **أنواع الملفات المفحوصة:**
  - Docker Compose files
  - Kubernetes manifests
  - Terraform files
  - Ansible playbooks
  - Cloud configuration files

**الكود المستخدم:**
```python
import re
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, resolve_path

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
def scan_infra(path: str = "/app") -> Dict[str, Any]:
    """Scan infrastructure files for security issues"""
    results = {
        "path": resolved_path,
        "issues": [],
        "summary": {
            "containers_as_root": 0,
            "exposed_ports": [],
            "missing_secrets": 0,
            "insecure_configs": 0,
        }
    }
    
    root = Path(resolved_path)
    
    # Find docker-compose files
    for compose_file in root.rglob("docker-compose*.yml"):
        with open(compose_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for root user
        if re.search(r'user:\s*["\']?0["\']?', content, re.IGNORECASE):
            results["issues"].append({
                "file": str(compose_file.relative_to(root)),
                "type": "container_as_root",
                "severity": "high",
                "message": "Container running as root user"
            })
            results["summary"]["containers_as_root"] += 1
        
        # Check for exposed ports
        port_matches = re.finditer(r'ports:\s*["\']?(\d+):', content)
        for match in port_matches:
            port = match.group(1)
            if port not in results["summary"]["exposed_ports"]:
                results["summary"]["exposed_ports"].append(port)
        
        # Check for hardcoded secrets
        if re.search(r'password["\s:=]+[^\s"\']{6,}', content, re.IGNORECASE):
            results["issues"].append({
                "file": str(compose_file.relative_to(root)),
                "type": "hardcoded_secret",
                "severity": "high",
                "message": "Hardcoded password found"
            })
            results["summary"]["missing_secrets"] += 1
        
        # Check for insecure configurations
        insecure_patterns = [
            (r'privileged:\s*true', "privileged_container"),
            (r'network_mode:\s*["\']?host["\']?', "host_network"),
        ]
        
        for pattern, issue_type in insecure_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                results["issues"].append({
                    "file": str(compose_file.relative_to(root)),
                    "type": issue_type,
                    "severity": "high",
                    "message": f"Insecure configuration: {issue_type}"
                })
                results["summary"]["insecure_configs"] += 1
    
    # Find Kubernetes files
    for k8s_file in root.rglob("*.yaml"):
        if "k8s" in str(k8s_file) or "kubernetes" in str(k8s_file):
            with open(k8s_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check for security issues
            if re.search(r'runAsUser:\s*0', content):
                results["issues"].append({
                    "file": str(k8s_file.relative_to(root)),
                    "type": "k8s_run_as_root",
                    "severity": "high",
                    "message": "Kubernetes pod running as root"
                })
                results["summary"]["insecure_configs"] += 1
    
    results["risk_score"] = calculate_risk_score({
        "high_risk": results["summary"]["containers_as_root"] + 
                    results["summary"]["missing_secrets"] + 
                    results["summary"]["insecure_configs"],
        "medium_risk": len(results["summary"]["exposed_ports"]),
        "low_risk": 0
    })
    
    return results
```

#### 3. Network Scanner (`network_scanner.py`)
- **الوظيفة:** فحص الشبكة للأمان
- **الأدوات المستخدمة:**
  - `netstat` / `ss` - لفحص الاتصالات المفتوحة
  - `iptables` - لفحص قواعد الجدار الناري
  - `tcpdump` - لتحليل حركة الشبكة
  - Python socket library - للاتصال بالمنافذ

**الكود المستخدم:**
```python
import subprocess
from typing import Dict, Any

@handle_scan_errors
@cached(ttl=timedelta(minutes=15))
def scan_network_security(detailed: bool = False) -> Dict[str, Any]:
    """Scan network for security issues"""
    results = {
        "suspicious_connections": [],
        "open_ports": [],
        "summary": {"high_risk": 0, "medium_risk": 0}
    }
    
    # Get listening ports - try ss first, fallback to netstat
    try:
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True,
            timeout=5
        )
    except FileNotFoundError:
        result = subprocess.run(
            ["netstat", "-tlnp"],
            capture_output=True,
            text=True,
            timeout=5
        )
    
    # Parse ports
    for line in result.stdout.split("\n")[1:]:
        parts = line.split()
        if len(parts) >= 4:
            addr = parts[3]
            if ":" in addr:
                port = addr.split(":")[-1]
                risky_ports = {"22": "SSH", "3306": "MySQL", "5432": "PostgreSQL"}
                if port in risky_ports:
                    results["open_ports"].append({
                        "port": port,
                        "service": risky_ports[port],
                        "risk": "high" if port == "22" else "medium",
                    })
    
    # Check for suspicious connections
    conn_result = subprocess.run(
        ["ss", "-tn"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    # Count connections per IP
    ip_counts = {}
    for line in conn_result.stdout.split("\n")[1:]:
        parts = line.split()
        if len(parts) >= 4:
            peer = parts[4]
            if ":" in peer:
                ip = peer.split(":")[0]
                ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    # Flag IPs with many connections
    for ip, count in ip_counts.items():
        if count > 10:
            results["suspicious_connections"].append({
                "ip": ip,
                "connections": count,
                "risk": "high" if count > 50 else "medium",
            })
    
    results["risk_score"] = calculate_risk_score(results["summary"])
    return results
```

#### 4. System Scanner (`system_scanner.py`)
- **الوظيفة:** فحص النظام للأمان
- **الأدوات المستخدمة:**
  - `ps` - لفحص العمليات
  - `lsof` - لفحص الملفات المفتوحة
  - `df` - لفحص مساحة القرص
  - `who` / `w` - لفحص المستخدمين المتصلين
  - `/proc` filesystem - لفحص معلومات النظام

**الكود المستخدم:**
```python
import subprocess
import pwd
from typing import Dict, Any

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
def scan_system_security() -> Dict[str, Any]:
    """Scan system for security issues"""
    results = {
        "system_info": {},
        "security_issues": [],
        "users": [],
        "services": [],
        "processes": [],
        "summary": {"high_risk": 0, "medium_risk": 0}
    }
    
    # System info
    uname = subprocess.run(["uname", "-a"], capture_output=True, text=True, timeout=5)
    results["system_info"]["os"] = uname.stdout.strip()
    
    # Check for root login
    passwd_result = subprocess.run(
        ["grep", "^root:", "/etc/passwd"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if passwd_result.returncode == 0:
        shell = passwd_result.stdout.split(":")[-1].strip()
        if shell != "/sbin/nologin":
            results["security_issues"].append({
                "type": "root_login_enabled",
                "severity": "high",
            })
    
    # Check users
    for user in pwd.getpwall():
        if user.pw_uid >= 1000:
            results["users"].append({
                "name": user.pw_name,
                "uid": user.pw_uid,
                "home": user.pw_dir,
            })
    
    # Check for passwordless sudo
    sudo_result = subprocess.run(
        ["grep", "-E", "^[^#].*ALL.*NOPASSWD", "/etc/sudoers"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if sudo_result.stdout.strip():
        results["security_issues"].append({
            "type": "passwordless_sudo",
            "severity": "high",
        })
    
    # Check running services
    systemctl_result = subprocess.run(
        ["systemctl", "list-units", "--type=service", "--state=running"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Check for suspicious processes
    ps_result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        timeout=5
    )
    suspicious_keywords = ["nc ", "netcat", "nmap", "masscan"]
    for line in ps_result.stdout.split("\n")[1:]:
        if any(keyword in line.lower() for keyword in suspicious_keywords):
            parts = line.split()
            results["processes"].append({
                "user": parts[0],
                "pid": parts[1],
                "cmd": " ".join(parts[10:]),
                "risk": "high",
            })
    
    results["risk_score"] = calculate_risk_score(results["summary"])
    return results
```

#### 5. Docker Scanner (`docker_scanner.py`)
- **الوظيفة:** فحص Docker containers والصور
- **الأدوات المستخدمة:**
  - `docker` CLI - لفحص containers
  - `docker-compose` - لفحص التكوينات
  - Docker API - للوصول لبيانات Docker

**الكود المستخدم:**
```python
import os
import re
import subprocess
from typing import Dict, Any
from pathlib import Path

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
def scan_docker_security() -> Dict[str, Any]:
    """Scan Docker configuration for security issues"""
    results = {
        "dockerfiles": [],
        "containers": [],
        "security_issues": [],
        "summary": {"high_risk": 0, "medium_risk": 0}
    }
    
    # Find Dockerfiles
    for base_path in ["/app", "."]:
        base = Path(base_path)
        if base.exists():
            for dockerfile in base.rglob("Dockerfile*"):
                with open(dockerfile, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                file_issues = []
                # Check for root user
                if re.search(r'USER\s+root|FROM.*root', content, re.IGNORECASE):
                    file_issues.append({
                        "type": "root_user",
                        "severity": "high",
                        "message": "Container running as root user",
                    })
                    results["summary"]["high_risk"] += 1
                
                # Check for latest tag
                if re.search(r'FROM\s+.*:latest', content, re.IGNORECASE):
                    file_issues.append({
                        "type": "latest_tag",
                        "severity": "medium",
                    })
                    results["summary"]["medium_risk"] += 1
                
                if file_issues:
                    results["dockerfiles"].append({
                        "file": str(dockerfile),
                        "issues": file_issues,
                    })
    
    # Check running containers
    ps_result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    for line in ps_result.stdout.split("\n"):
        if line.strip():
            parts = line.split("\t")
            if len(parts) >= 2:
                results["containers"].append({
                    "name": parts[0],
                    "image": parts[1],
                    "status": parts[2] if len(parts) > 2 else "Unknown",
                })
                
                # Check for privileged mode
                priv_result = subprocess.run(
                    ["docker", "inspect", "--format", "{{.HostConfig.Privileged}}", parts[0]],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if priv_result.stdout.strip().lower() == "true":
                    results["security_issues"].append({
                        "type": "privileged_container",
                        "severity": "high",
                        "message": f"Container {parts[0]} is running in privileged mode",
                    })
    
    results["risk_score"] = calculate_risk_score(results["summary"])
    return results
```

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

**الكود المستخدم:**
```python
import re
from typing import Dict, Any
from pathlib import Path

@handle_scan_errors
@cached(ttl=timedelta(minutes=10))
def scan_logs_auth(path: str = "/app/logs", lines: int = 1000) -> Dict[str, Any]:
    """Scan logs for authentication issues"""
    results = {
        "path": resolved_path,
        "failed_logins": [],
        "suspicious_ips": {},
        "summary": {
            "total_failed": 0,
            "unique_ips": 0,
            "brute_force_detected": False,
        }
    }
    
    # Patterns for failed logins
    failed_patterns = [
        r'failed[\s_]+login',
        r'authentication[\s_]+failed',
        r'invalid[\s_]+password',
        r'access[\s_]+denied',
        r'401',
        r'403',
    ]
    
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    
    log_path = Path(resolved_path)
    log_files = list(log_path.glob("*.log"))[:10]
    
    for log_file in log_files:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            log_lines = f.readlines()[-lines:]
        
        for line in log_lines:
            # Check for failed login patterns
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in failed_patterns):
                results["summary"]["total_failed"] += 1
                
                # Extract IP
                ip_match = re.search(ip_pattern, line)
                if ip_match:
                    ip = ip_match.group(0)
                    if ip not in results["suspicious_ips"]:
                        results["suspicious_ips"][ip] = 0
                    results["suspicious_ips"][ip] += 1
                    
                    results["failed_logins"].append({
                        "ip": ip,
                        "line": line.strip()[:200],
                        "file": log_file.name,
                    })
    
    # Detect brute-force (same IP with > 10 failed attempts)
    for ip, count in results["suspicious_ips"].items():
        if count > 10:
            results["summary"]["brute_force_detected"] = True
            results["failed_logins"].append({
                "ip": ip,
                "type": "brute_force",
                "attempts": count,
                "severity": "high",
            })
    
    results["risk_score"] = calculate_risk_score(results["summary"])
    return results
```

#### 7. Vulnerability Scanner (`vulnerability_scanner.py`)
- **الوظيفة:** فحص الثغرات الأمنية
- **الأدوات المستخدمة:**
  - Package managers (`apt`, `pip`, `npm`) - لفحص الحزم المثبتة
  - `pip-audit` - لفحص ثغرات Python packages
  - `npm audit` - لفحص ثغرات Node.js packages
  - CVE databases - للبحث عن الثغرات المعروفة
  - Version checking - لمقارنة الإصدارات

**الكود المستخدم:**
```python
import subprocess
import json
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, resolve_path

@handle_scan_errors
@cached(ttl=timedelta(hours=2))
def scan_vulnerabilities() -> Dict[str, Any]:
    """Enhanced vulnerability scan with pip/npm audit support"""
    results = {
        "vulnerabilities": [],
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
    }
    
    # Try pip-audit first (if installed)
    try:
        pip_audit_result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if pip_audit_result.returncode == 0:
            audit_data = json.loads(pip_audit_result.stdout)
            for vuln in audit_data.get("vulnerabilities", []):
                severity = vuln.get("severity", "medium").lower()
                results["vulnerabilities"].append({
                    "package": vuln.get("name", "unknown"),
                    "version": vuln.get("version", "unknown"),
                    "cve": vuln.get("id", "unknown"),
                    "severity": severity,
                    "description": vuln.get("description", ""),
                })
                if severity == "critical":
                    results["summary"]["critical"] += 1
                elif severity == "high":
                    results["summary"]["high"] += 1
                elif severity == "medium":
                    results["summary"]["medium"] += 1
                else:
                    results["summary"]["low"] += 1
    except FileNotFoundError:
        # Fallback: check requirements.txt
        project_root = resolve_path(".")
        for req_file in Path(project_root).rglob("requirements.txt"):
            if req_file.exists():
                with open(req_file, "r") as f:
                    for line in f:
                        if "==" in line:
                            pkg = line.split("==")[0].strip()
                            results["vulnerabilities"].append({
                                "package": pkg,
                                "severity": "medium",
                                "message": "Package found (pip-audit not available)",
                            })
                            results["summary"]["medium"] += 1
    
    # Check Node.js packages (npm audit)
    project_root = resolve_path(".")
    for pkg_json in Path(project_root).rglob("package.json"):
        if pkg_json.exists():
            pkg_dir = pkg_json.parent
            npm_audit_result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=str(pkg_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            if npm_audit_result.returncode == 0:
                audit_data = json.loads(npm_audit_result.stdout)
                for vuln_id, vuln_info in audit_data.get("vulnerabilities", {}).items():
                    severity = vuln_info.get("severity", "medium").lower()
                    results["vulnerabilities"].append({
                        "package": vuln_id,
                        "severity": severity,
                        "cve": vuln_info.get("cves", [""])[0] if vuln_info.get("cves") else "",
                        "description": vuln_info.get("title", ""),
                    })
                    if severity == "critical":
                        results["summary"]["critical"] += 1
                    elif severity == "high":
                        results["summary"]["high"] += 1
                    elif severity == "medium":
                        results["summary"]["medium"] += 1
                    else:
                        results["summary"]["low"] += 1
    
    results["risk_score"] = calculate_risk_score(results["summary"])
    return results
```

#### 8. File Integrity Scanner (`file_integrity_scanner.py`)
- **الوظيفة:** فحص سلامة الملفات
- **الأدوات المستخدمة:**
  - `md5sum` / `sha256sum` - لحساب checksums
  - Python `hashlib` - لحساب hashes
  - `stat` - لفحص معلومات الملفات
  - File system monitoring - لمراقبة التغييرات

**الكود المستخدم:**
```python
import hashlib
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from .base import calculate_risk_score, resolve_path

@handle_scan_errors
@cached(ttl=timedelta(hours=1))
def scan_file_integrity(path: str = "/etc") -> Dict[str, Any]:
    """Monitor file integrity (detect unauthorized changes)"""
    results = {
        "monitored_files": [],
        "changed_files": [],
        "new_files": [],
        "deleted_files": [],
        "summary": {
            "files_monitored": 0,
            "changes_detected": 0,
        }
    }
    
    # Monitor key files
    key_files = [
        "passwd", "shadow", "group", "sudoers",
        "hosts", "hostname", "resolv.conf",
    ]
    
    monitored_path = Path(path)
    for key_file in key_files:
        file_path = monitored_path / key_file
        if file_path.exists():
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            results["monitored_files"].append({
                "file": str(file_path),
                "hash": file_hash[:16] + "...",
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            })
            results["summary"]["files_monitored"] += 1
    
    results["risk_score"] = calculate_risk_score({
        "high_risk": results["summary"]["changes_detected"],
        "medium_risk": 0,
        "low_risk": 0
    })
    return results
```

#### 9. Malware Scanner (`malware_scanner.py`)
- **الوظيفة:** فحص البرمجيات الخبيثة
- **الأدوات المستخدمة:**
  - File signature scanning
  - Pattern matching
  - Heuristic analysis
  - Python `hashlib` - لحساب hashes للملفات
  - Binary header analysis - لفحص رؤوس الملفات الثنائية

**الكود المستخدم:**
```python
import hashlib
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, resolve_path

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
def scan_malware(path: str = "/tmp") -> Dict[str, Any]:
    """Scan for malware indicators with enhanced detection"""
    results = {
        "suspicious_files": [],
        "suspicious_processes": [],
        "summary": {
            "files_scanned": 0,
            "suspicious_found": 0,
        }
    }
    
    scan_path = Path(path)
    
    # Suspicious filename patterns
    suspicious_patterns = [
        ".exe", ".bat", ".scr", ".vbs", ".sh", ".py",
        "miner", "crypto", "backdoor", "trojan", "virus",
    ]
    
    # Malware signatures (placeholder - in production, use real signatures)
    malware_signatures = {
        # Example: "abc123...": "Trojan.Generic"
    }
    
    for file_path in scan_path.rglob("*"):
        if not file_path.is_file():
            continue
        
        results["summary"]["files_scanned"] += 1
        
        # Check filename
        file_name = file_path.name.lower()
        if any(pattern in file_name for pattern in suspicious_patterns):
            # Calculate hash
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Check against signatures
            is_malware = file_hash in malware_signatures
            
            # Check binary headers (ELF vs PE)
            with open(file_path, "rb") as f:
                header = f.read(4)
                is_binary = header.startswith(b'\x7fELF') or header.startswith(b'MZ')
                if is_binary and not file_name.endswith(('.so', '.dll', '.exe')):
                    is_malware = True
            
            if is_malware or any(pattern in file_name for pattern in ["miner", "backdoor", "trojan"]):
                results["suspicious_files"].append({
                    "file": str(file_path),
                    "hash": file_hash[:16] + "...",
                    "reason": "Suspicious filename or signature match",
                    "risk": "high",
                })
                results["summary"]["suspicious_found"] += 1
    
    results["risk_score"] = calculate_risk_score({
        "high_risk": results["summary"]["suspicious_found"],
        "medium_risk": 0,
        "low_risk": 0
    })
    return results
```

#### 10. Intrusion Detection Scanner (`ids_scanner.py`)
- **الوظيفة:** كشف محاولات الاختراق
- **الأدوات المستخدمة:**
  - Log analysis - تحليل السجلات
  - `ss` / `netstat` - لفحص الاتصالات
  - `crontab` - لفحص المهام المجدولة
  - Network traffic analysis - تحليل حركة الشبكة
  - Anomaly detection - كشف الشذوذ

**الكود المستخدم:**
```python
import subprocess
from typing import Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from .base import calculate_risk_score

@handle_scan_errors
@cached(ttl=timedelta(minutes=15))
def scan_intrusion_detection() -> Dict[str, Any]:
    """Enhanced Intrusion Detection System (IDS) scan"""
    results = {
        "intrusions": [],
        "anomalies": [],
        "summary": {
            "intrusions_detected": 0,
            "anomalies_detected": 0,
        }
    }
    
    # Check auth.log for sudo failures
    auth_logs = [Path("/var/log/auth.log"), Path("/var/log/secure")]
    for auth_log in auth_logs:
        if auth_log.exists():
            with open(auth_log, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-1000:]  # Last 1000 lines
            
            sudo_failures = 0
            for line in lines:
                if "sudo" in line.lower() and ("failed" in line.lower() or "incorrect" in line.lower()):
                    sudo_failures += 1
                    if sudo_failures > 10:
                        results["intrusions"].append({
                            "type": "excessive_sudo_failures",
                            "severity": "high",
                            "message": f"Excessive sudo failures detected: {sudo_failures}",
                        })
                        results["summary"]["intrusions_detected"] += 1
                        break
    
    # Check for new cron jobs
    cron_result = subprocess.run(
        ["crontab", "-l"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if cron_result.returncode == 0:
        suspicious_patterns = ["curl", "wget", "bash", "sh", "python", "perl"]
        for line in cron_result.stdout.split("\n"):
            if any(pattern in line.lower() for pattern in suspicious_patterns):
                results["anomalies"].append({
                    "type": "suspicious_cron_job",
                    "severity": "medium",
                    "message": f"Suspicious cron job: {line.strip()[:100]}",
                })
                results["summary"]["anomalies_detected"] += 1
    
    # Check for unusual network connections
    netstat_result = subprocess.run(
        ["ss", "-tn"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if netstat_result.returncode == 0:
        suspicious_ports = [4444, 5555, 6666, 31337]
        for line in netstat_result.stdout.split("\n"):
            for port in suspicious_ports:
                if f":{port}" in line:
                    results["intrusions"].append({
                        "type": "suspicious_port_connection",
                        "severity": "high",
                        "message": f"Connection to suspicious port {port}",
                    })
                    results["summary"]["intrusions_detected"] += 1
                    break
    
    results["risk_score"] = calculate_risk_score({
        "high_risk": results["summary"]["intrusions_detected"],
        "medium_risk": results["summary"]["anomalies_detected"],
        "low_risk": 0
    })
    return results
```

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

**الكود المستخدم:**
```python
import subprocess
import shutil
from pathlib import Path

class CICDService:
    def clone_repo(self, repo_url: str, repo_name: str, branch: str = "main") -> Dict:
        """Clone a repository"""
        repo_path = self.repos_dir / repo_name
        
        # Remove if exists
        if repo_path.exists():
            shutil.rmtree(repo_path)
        
        # Clone repository
        result = subprocess.run(
            ["git", "clone", "-b", branch, repo_url, str(repo_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        return {
            "success": True,
            "repo_path": str(repo_path),
            "message": "Repository cloned successfully"
        }
    
    def pull_repo(self, repo_name: str, branch: str = "main") -> Dict:
        """Pull latest changes from repository"""
        repo_path = self.repos_dir / repo_name
        
        # Fetch and pull
        subprocess.run(
            ["git", "-C", str(repo_path), "fetch", "origin"],
            capture_output=True,
            check=True
        )
        
        result = subprocess.run(
            ["git", "-C", str(repo_path), "pull", "origin", branch],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        return {"success": True, "message": "Repository updated successfully"}
    
    def get_repo_info(self, repo_name: str) -> Dict:
        """Get repository information"""
        repo_path = self.repos_dir / repo_name
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "-C", str(repo_path), "branch", "--show-current"],
            capture_output=True,
            text=True
        )
        branch = branch_result.stdout.strip()
        
        # Get last commit
        commit_result = subprocess.run(
            ["git", "-C", str(repo_path), "log", "-1", "--format=%H|%s|%an|%ad"],
            capture_output=True,
            text=True
        )
        
        return {
            "exists": True,
            "repo_path": str(repo_path),
            "branch": branch,
            "last_commit": commit_info
        }
```

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

**الكود المستخدم:**
```python
import subprocess
from pathlib import Path

class DeployEngine:
    def deploy_docker_compose(
        self,
        compose_file: str,
        project_name: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> Dict:
        """Deploy using Docker Compose"""
        compose_path = Path(compose_file)
        
        # Build command
        cmd = ["docker", "compose", "-f", str(compose_path)]
        
        if project_name:
            cmd.extend(["-p", project_name])
        
        # Pull images
        pull_result = subprocess.run(
            cmd + ["pull"],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if pull_result.returncode != 0:
            return {"success": False, "error": f"Failed to pull images: {pull_result.stderr}"}
        
        # Start services
        up_cmd = cmd + ["up", "-d"]
        if services:
            up_cmd.extend(services)
        
        up_result = subprocess.run(
            up_cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if up_result.returncode != 0:
            return {"success": False, "error": f"Failed to start services: {up_result.stderr}"}
        
        return {
            "success": True,
            "message": "Deployment successful",
            "output": up_result.stdout
        }
```

#### 2. Kubernetes Deployment
- **الوظيفة:** النشر على Kubernetes
- **الأدوات المستخدمة:**
  - `kubectl` - لـ Kubernetes CLI
  - `kubectl apply` - لتطبيق الـ manifests
  - `kubectl get` - لفحص الموارد
  - `kubectl describe` - لعرض التفاصيل
  - YAML parsing - لتحليل ملفات Kubernetes

**الكود المستخدم:**
```python
import subprocess
import json
from pathlib import Path

def deploy_kubernetes(
    self,
    manifest_file: str,
    namespace: str = "default",
    apply: bool = True
) -> Dict:
    """Deploy to Kubernetes"""
    manifest_path = Path(manifest_file)
    
    if apply:
        # Apply manifest
        result = subprocess.run(
            ["kubectl", "apply", "-f", str(manifest_path), "-n", namespace],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return {"success": False, "error": f"Failed to apply manifest: {result.stderr}"}
        
        return {
            "success": True,
            "message": "Kubernetes deployment successful",
            "output": result.stdout
        }
    else:
        # Just validate
        result = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", str(manifest_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "message": "Validation successful" if result.returncode == 0 else "Validation failed",
            "output": result.stdout if result.returncode == 0 else result.stderr
        }
```

#### 3. RSync Deployment
- **الوظيفة:** النشر باستخدام RSync
- **الأدوات المستخدمة:**
  - `rsync` - لمزامنة الملفات
  - SSH - للاتصال بالخوادم البعيدة
  - File synchronization

**الكود المستخدم:**
```python
import subprocess

def deploy_rsync(
    self,
    source: str,
    destination: str,
    host: Optional[str] = None,
    user: Optional[str] = None,
    exclude: Optional[List[str]] = None,
    delete: bool = False
) -> Dict:
    """Deploy using RSync"""
    # Build rsync command
    cmd = ["rsync", "-avz"]
    
    if delete:
        cmd.append("--delete")
    
    if exclude:
        for pattern in exclude:
            cmd.extend(["--exclude", pattern])
    
    # Add source
    cmd.append(source.rstrip("/") + "/")
    
    # Add destination
    if host:
        if user:
            dest = f"{user}@{host}:{destination}"
        else:
            dest = f"{host}:{destination}"
    else:
        dest = destination
    
    cmd.append(dest)
    
    # Execute rsync
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600
    )
    
    if result.returncode != 0:
        return {"success": False, "error": f"RSync failed: {result.stderr}"}
    
    return {
        "success": True,
        "message": "RSync deployment successful",
        "output": result.stdout
    }
```

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

**الكود المستخدم:**
```python
import os
import json
import requests
from app.core.config import get_settings

settings = get_settings()
OLLAMA_URL = settings.OLLAMA_URL
MODEL_NAME = os.getenv("AGENT_MODEL", "llama3.2:1b")

def _check_ollama_connection():
    """التحقق من اتصال Ollama وتوفر الموديل"""
    try:
        # التحقق من أن Ollama يعمل
        health_check = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if health_check.status_code != 200:
            return False, f"Ollama service returned status {health_check.status_code}"
        
        # التحقق من وجود الموديل
        models = health_check.json().get("models", [])
        model_names = [m.get("name", "") for m in models]
        if MODEL_NAME not in model_names:
            return False, f"Model '{MODEL_NAME}' not found"
        
        return True, None
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to Ollama at {OLLAMA_URL}"
    except Exception as e:
        return False, f"Error checking Ollama: {str(e)}"

def _call_ollama(
    prompt: str,
    temperature: float = 0.2,
    num_predict: int = 256,
    timeout: int = 300,
) -> dict:
    """استدعاء عام لـ Ollama"""
    is_connected, error_msg = _check_ollama_connection()
    if not is_connected:
        raise ConnectionError(f"Ollama connection failed: {error_msg}")
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()

def llm_text(user_prompt: str) -> str:
    """رد نصي عادي للمستخدم"""
    data = _call_ollama(
        user_prompt,
        temperature=0.4,
        num_predict=256,
        timeout=300,
    )
    return data.get("response", "").strip()

def llm_json(system_instructions: str, user_prompt: str) -> dict:
    """نطلب من الموديل يرجع JSON واحد فقط"""
    prompt = f"""{system_instructions.strip()}

User message:
{user_prompt}
"""

    json_enforce = """
You MUST reply with ONLY ONE valid JSON object.
JSON ONLY. No explanation, no markdown, no backticks.
"""

    full_prompt = prompt + "\n\n" + json_enforce

    data = _call_ollama(
        full_prompt,
        temperature=0.1,
        num_predict=128,
        timeout=300,
    )
    raw = data.get("response", "").strip()

    # محاولة parsing للـ JSON
    try:
        return json.loads(raw)
    except Exception:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {"raw": raw}
```

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

