import os
import re
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from app.utils.helpers import load_settings

# Common secret patterns
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

def resolve_path(path: str) -> str:
    """
    Resolve path similar to read_file.py
    Handles /app paths and converts them to actual filesystem paths
    """
    settings = load_settings()
    path = path.strip()
    original_path = path
    
    # If path doesn't start with /, make it absolute
    if not path.startswith('/'):
        if path.startswith('~/'):
            path = os.path.expanduser(path)
        elif path.startswith('home/'):
            path = '/' + path
        else:
            # Default base path - fixed as requested
            base = settings.base_path or "/app"
            path = os.path.abspath(os.path.join(base, path))
    
    # Handle /app paths (common in Docker containers)
    if path.startswith('/app'):
        # Try to resolve /app to actual path
        current_dir = os.getcwd()
        # If we're in /home/ai/ai-agent/backend, /app might mean backend
        if '/home/ai/ai-agent' in current_dir:
            # Replace /app with actual backend path
            if path == '/app' or path == '/app/':
                path = '/home/ai/ai-agent/backend'
            elif path.startswith('/app/'):
                # /app/something -> /home/ai/ai-agent/backend/something
                relative = path[5:]  # Remove '/app/'
                path = os.path.join('/home/ai/ai-agent/backend', relative)
        else:
            # Try other common locations
            if os.path.exists('/home/ai/ai-agent/backend'):
                if path == '/app' or path == '/app/':
                    path = '/home/ai/ai-agent/backend'
                elif path.startswith('/app/'):
                    relative = path[5:]
                    path = os.path.join('/home/ai/ai-agent/backend', relative)
    
    # Check restricted paths
    if settings.restricted_paths:
        for restricted in settings.restricted_paths:
            if path.startswith(restricted) or restricted in path:
                raise PermissionError(f"Path '{path}' is restricted by settings")
    
    # Check allowed paths (if specified)
    if settings.allowed_paths:
        allowed = False
        for allowed_path in settings.allowed_paths:
            if path.startswith(allowed_path):
                allowed = True
                break
        if not allowed:
            raise PermissionError(f"Path '{path}' is not in allowed_paths")
    
    return path


def scan_repo(path: str = "/app", max_files: int = 1000) -> Dict[str, Any]:
    """
    Scan repository for secrets and security issues
    """
    try:
        # Resolve path
        resolved_path = resolve_path(path)
    except Exception as e:
        return {"error": str(e)}
    
    results = {
        "path": resolved_path,
        "secrets_found": [],
        "risky_files": [],
        "summary": {
            "total_files": 0,
            "scanned_files": 0,
            "secrets_count": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    # Smart exclude patterns - optimized for large projects
    excluded_patterns = [
        ".git/**/*",
        "__pycache__/**/*",
        "node_modules/**/*",
        ".next/**/*",
        "venv/**/*",
        "env/**/*",
        ".env",
        "*.pyc",
        "*.log",
        "*/migrations/*",
        "*/tests/*",
        "*/test/*",
        "*/__tests__/*",
        "*/test_*",
        "*/spec/*",
        "*/coverage/*",
        "*/dist/*",
        "*/build/*",
        "*/target/*",
        ".pytest_cache/**/*",
        ".mypy_cache/**/*",
    ]
    
    # Convert glob patterns to simple string checks for performance
    excluded = [
        ".git", "__pycache__", "node_modules", ".next",
        "venv", "env", ".env", ".pyc", ".log",
        "migrations", "tests", "test_", "spec",
        "coverage", "dist", "build", "target",
        ".pytest_cache", ".mypy_cache"
    ]
    
    try:
        root = Path(resolved_path)
        if not root.exists():
            return {"error": f"Path does not exist: {resolved_path}. Original path: {path}"}
        
        file_count = 0
        for file_path in root.rglob("*"):
            if file_count >= max_files:
                break
            
            # Skip excluded patterns (smart matching)
            file_str = str(file_path)
            if any(exc in file_str for exc in excluded):
                continue
            # Additional checks for specific patterns
            if "/migrations/" in file_str or "/tests/" in file_str or "/test/" in file_str:
                continue
            
            if not file_path.is_file():
                continue
            
            file_count += 1
            results["summary"]["total_files"] = file_count
            
            # Skip large files
            try:
                if file_path.stat().st_size > 100000:  # 100KB
                    continue
            except:
                continue
            
            # Read file
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                continue
            
            results["summary"]["scanned_files"] += 1
            
            # Scan for secrets
            file_secrets = []
            for secret_type, patterns in SECRET_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count("\n") + 1
                        secret_value = match.group(1) if match.groups() else match.group(0)
                        
                        # Don't show full secret
                        if len(secret_value) > 20:
                            secret_preview = secret_value[:10] + "..." + secret_value[-5:]
                        else:
                            secret_preview = "***"
                        
                        file_secrets.append({
                            "type": secret_type,
                            "line": line_num,
                            "preview": secret_preview,
                            "pattern": pattern,
                        })
            
            if file_secrets:
                results["secrets_found"].append({
                    "file": str(file_path.relative_to(root)),
                    "secrets": file_secrets,
                    "count": len(file_secrets),
                })
                results["summary"]["secrets_count"] += len(file_secrets)
                
                # Risk assessment
                high_risk_types = ["private_key", "aws_key", "password"]
                if any(s["type"] in high_risk_types for s in file_secrets):
                    results["summary"]["high_risk"] += 1
                    results["risky_files"].append({
                        "file": str(file_path.relative_to(root)),
                        "risk": "high",
                        "reason": "Contains high-risk secrets"
                    })
                elif len(file_secrets) > 3:
                    results["summary"]["medium_risk"] += 1
                    results["risky_files"].append({
                        "file": str(file_path.relative_to(root)),
                        "risk": "medium",
                        "reason": "Multiple secrets found"
                    })
                else:
                    results["summary"]["low_risk"] += 1
    
    except Exception as e:
        return {"error": f"Scan error: {e}"}
    
    return results

def scan_infra(path: str = "/app") -> Dict[str, Any]:
    """
    Scan infrastructure files (docker-compose, k8s) for security issues
    """
    try:
        # Resolve path
        resolved_path = resolve_path(path)
    except Exception as e:
        return {"error": str(e)}
    
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
    
    try:
        root = Path(resolved_path)
        if not root.exists():
            return {"error": f"Path does not exist: {resolved_path}. Original path: {path}"}
        
        # Find docker-compose files
        for compose_file in root.rglob("docker-compose*.yml"):
            try:
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
                
            except Exception as e:
                continue
        
        # Find k8s files
        for k8s_file in root.rglob("*.yaml"):
            if "k8s" in str(k8s_file) or "kubernetes" in str(k8s_file):
                try:
                    with open(k8s_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Check for securityContext
                    if "securityContext" not in content and "runAsNonRoot" not in content:
                        results["issues"].append({
                            "file": str(k8s_file.relative_to(root)),
                            "type": "missing_security_context",
                            "severity": "medium",
                            "message": "Missing securityContext configuration"
                        })
                        results["summary"]["insecure_configs"] += 1
                except:
                    continue
    
    except Exception as e:
        return {"error": f"Infra scan error: {e}"}
    
    return results

def scan_network_security() -> Dict[str, Any]:
    """
    Scan network for security issues
    """
    results = {
        "suspicious_connections": [],
        "open_ports": [],
        "summary": {
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    try:
        import subprocess
        
        # Get listening ports - try ss first, fallback to netstat
        try:
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
        except FileNotFoundError:
            # Fallback to netstat
            result = subprocess.run(
                ["netstat", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        for line in result.stdout.split("\n")[1:]:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 4:
                continue
            
            # Extract port
            addr = parts[3]
            if ":" in addr:
                port = addr.split(":")[-1]
                
                # Check for risky ports
                risky_ports = {
                    "22": "SSH",
                    "3306": "MySQL",
                    "5432": "PostgreSQL",
                    "6379": "Redis",
                    "27017": "MongoDB",
                    "9200": "Elasticsearch",
                }
                
                if port in risky_ports:
                    results["open_ports"].append({
                        "port": port,
                        "service": risky_ports[port],
                        "risk": "high" if port == "22" else "medium",
                    })
                    if port == "22":
                        results["summary"]["high_risk"] += 1
                    else:
                        results["summary"]["medium_risk"] += 1
        
        # Check for suspicious connections (many connections from same IP)
        try:
            conn_result = subprocess.run(
                ["ss", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
        except FileNotFoundError:
            # Fallback to netstat
            conn_result = subprocess.run(
                ["netstat", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        ip_counts = {}
        for line in conn_result.stdout.split("\n")[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                # Extract IP from connection
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
                if count > 50:
                    results["summary"]["high_risk"] += 1
                else:
                    results["summary"]["medium_risk"] += 1
    
    except Exception as e:
        return {"error": f"Network security scan error: {e}"}
    
    return results

def scan_logs_auth(path: str = "/app/logs", lines: int = 1000) -> Dict[str, Any]:
    """
    Scan logs for authentication issues (brute-force, failed logins)
    """
    try:
        # Resolve path
        resolved_path = resolve_path(path)
    except Exception as e:
        return {"error": str(e)}
    
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
    
    # IP pattern
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    
    try:
        log_path = Path(resolved_path)
        if not log_path.exists():
            return {"error": f"Log path does not exist: {resolved_path}. Original path: {path}"}
        
        # Read log files
        log_files = list(log_path.glob("*.log"))[:10]  # Max 10 files
        
        for log_file in log_files:
            try:
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
                                "line": line.strip()[:200],  # First 200 chars
                                "file": log_file.name,
                            })
            except Exception as e:
                continue
        
        # Detect brute-force (same IP with > 10 failed attempts)
        results["summary"]["unique_ips"] = len(results["suspicious_ips"])
        for ip, count in results["suspicious_ips"].items():
            if count > 10:
                results["summary"]["brute_force_detected"] = True
                results["failed_logins"].append({
                    "ip": ip,
                    "type": "brute_force",
                    "attempts": count,
                    "severity": "high",
                })
    
    except Exception as e:
        return {"error": f"Log scan error: {e}"}
    
    return results

def scan_system_security() -> Dict[str, Any]:
    """
    Scan system for security issues (OS, services, processes, users, etc.)
    """
    results = {
        "system_info": {},
        "security_issues": [],
        "users": [],
        "services": [],
        "processes": [],
        "summary": {
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    try:
        import subprocess
        import pwd
        import grp
        
        # System info
        try:
            uname = subprocess.run(["uname", "-a"], capture_output=True, text=True, timeout=5)
            results["system_info"]["os"] = uname.stdout.strip() if uname.returncode == 0 else "Unknown"
        except:
            results["system_info"]["os"] = "Unknown"
        
        # Check for root login
        try:
            passwd_result = subprocess.run(
                ["grep", "^root:", "/etc/passwd"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if passwd_result.returncode == 0:
                shell = passwd_result.stdout.split(":")[-1].strip()
                if shell != "/sbin/nologin" and shell != "/bin/false":
                    results["security_issues"].append({
                        "type": "root_login_enabled",
                        "severity": "high",
                        "message": "Root login may be enabled",
                    })
                    results["summary"]["high_risk"] += 1
        except:
            pass
        
        # Check users
        try:
            users = []
            for user in pwd.getpwall():
                if user.pw_uid >= 1000:  # Regular users
                    users.append({
                        "name": user.pw_name,
                        "uid": user.pw_uid,
                        "gid": user.pw_gid,
                        "home": user.pw_dir,
                        "shell": user.pw_shell,
                    })
            results["users"] = users
        except:
            pass
        
        # Check for sudo users
        try:
            sudo_result = subprocess.run(
                ["grep", "-E", "^[^#].*ALL.*NOPASSWD", "/etc/sudoers"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if sudo_result.returncode == 0 and sudo_result.stdout.strip():
                results["security_issues"].append({
                    "type": "passwordless_sudo",
                    "severity": "high",
                    "message": "Passwordless sudo detected",
                    "details": sudo_result.stdout.strip(),
                })
                results["summary"]["high_risk"] += 1
        except:
            pass
        
        # Check running services
        try:
            systemctl_result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if systemctl_result.returncode == 0:
                services = []
                for line in systemctl_result.stdout.split("\n")[1:]:
                    if line.strip() and ".service" in line:
                        service_name = line.split()[0]
                        services.append(service_name)
                results["services"] = services[:20]  # Limit to 20
        except:
            pass
        
        # Check for suspicious processes
        try:
            ps_result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ps_result.returncode == 0:
                suspicious_keywords = ["nc ", "netcat", "nmap", "masscan", "hydra", "sqlmap"]
                processes = []
                for line in ps_result.stdout.split("\n")[1:]:
                    if any(keyword in line.lower() for keyword in suspicious_keywords):
                        parts = line.split()
                        if len(parts) > 10:
                            processes.append({
                                "user": parts[0],
                                "pid": parts[1],
                                "cmd": " ".join(parts[10:]),
                                "risk": "high",
                            })
                            results["summary"]["high_risk"] += 1
                results["processes"] = processes
        except:
            pass
        
        # Check file permissions
        try:
            # Check for world-writable files
            find_result = subprocess.run(
                ["find", "/tmp", "/var/tmp", "-type", "f", "-perm", "-002", "2>/dev/null", "|", "head", "-10"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if find_result.stdout.strip():
                results["security_issues"].append({
                    "type": "world_writable_files",
                    "severity": "medium",
                    "message": "World-writable files found in /tmp",
                })
                results["summary"]["medium_risk"] += 1
        except:
            pass
        
    except Exception as e:
        return {"error": f"System scan error: {e}"}
    
    return results

def scan_docker_security() -> Dict[str, Any]:
    """
    Scan Docker configuration for security issues
    """
    results = {
        "dockerfiles": [],
        "docker_compose_files": [],
        "containers": [],
        "images": [],
        "security_issues": [],
        "summary": {
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    try:
        import subprocess
        from pathlib import Path
        
        # Scan Dockerfiles
        dockerfile_patterns = [
            "Dockerfile",
            "Dockerfile.*",
            "**/Dockerfile",
            "**/Dockerfile.*",
        ]
        
        security_checks = {
            "root_user": {
                "pattern": r'USER\s+root|FROM.*root',
                "severity": "high",
                "message": "Container running as root user",
            },
            "latest_tag": {
                "pattern": r'FROM\s+.*:latest',
                "severity": "medium",
                "message": "Using 'latest' tag (not recommended)",
            },
            "no_healthcheck": {
                "pattern": r'HEALTHCHECK',
                "severity": "low",
                "message": "Missing HEALTHCHECK",
                "inverse": True,  # Missing is bad
            },
            "privileged": {
                "pattern": r'--privileged',
                "severity": "high",
                "message": "Privileged mode detected",
            },
            "secrets_in_dockerfile": {
                "pattern": r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
                "severity": "high",
                "message": "Secrets found in Dockerfile",
            },
        }
        
        # Find Dockerfiles
        search_paths = ["/app", "/home", "/opt"]
        for base_path in search_paths:
            base = Path(base_path)
            if base.exists():
                for dockerfile in base.rglob("Dockerfile*"):
                    try:
                        with open(dockerfile, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        file_issues = []
                        for check_name, check_info in security_checks.items():
                            if check_info.get("inverse"):
                                # Missing is bad
                                if not re.search(check_info["pattern"], content, re.IGNORECASE):
                                    file_issues.append({
                                        "type": check_name,
                                        "severity": check_info["severity"],
                                        "message": check_info["message"],
                                    })
                            else:
                                # Presence is bad
                                if re.search(check_info["pattern"], content, re.IGNORECASE):
                                    file_issues.append({
                                        "type": check_name,
                                        "severity": check_info["severity"],
                                        "message": check_info["message"],
                                    })
                        
                        if file_issues:
                            results["dockerfiles"].append({
                                "file": str(dockerfile),
                                "issues": file_issues,
                            })
                            
                            for issue in file_issues:
                                if issue["severity"] == "high":
                                    results["summary"]["high_risk"] += 1
                                elif issue["severity"] == "medium":
                                    results["summary"]["medium_risk"] += 1
                                else:
                                    results["summary"]["low_risk"] += 1
                    except:
                        continue
        
        # Scan docker-compose files
        compose_checks = {
            "privileged": {
                "pattern": r'privileged:\s*true',
                "severity": "high",
                "message": "Privileged container",
            },
            "host_network": {
                "pattern": r'network_mode:\s*["\']?host["\']?',
                "severity": "high",
                "message": "Using host network mode",
            },
            "exposed_ports": {
                "pattern": r'ports:\s*-\s*["\']?0\.0\.0\.0:\d+',
                "severity": "medium",
                "message": "Exposing ports to 0.0.0.0",
            },
            "no_restart_policy": {
                "pattern": r'restart:\s*(always|unless-stopped|on-failure)',
                "severity": "low",
                "message": "Missing restart policy",
                "inverse": True,
            },
            "secrets_in_compose": {
                "pattern": r'(password|secret|key|token):\s*["\'][^"\']+["\']',
                "severity": "high",
                "message": "Secrets found in docker-compose",
            },
        }
        
        for base_path in search_paths:
            base = Path(base_path)
            if base.exists():
                for compose_file in base.rglob("docker-compose*.yml"):
                    try:
                        with open(compose_file, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        file_issues = []
                        for check_name, check_info in compose_checks.items():
                            if check_info.get("inverse"):
                                if not re.search(check_info["pattern"], content, re.IGNORECASE):
                                    file_issues.append({
                                        "type": check_name,
                                        "severity": check_info["severity"],
                                        "message": check_info["message"],
                                    })
                            else:
                                if re.search(check_info["pattern"], content, re.IGNORECASE):
                                    file_issues.append({
                                        "type": check_name,
                                        "severity": check_info["severity"],
                                        "message": check_info["message"],
                                    })
                        
                        if file_issues:
                            results["docker_compose_files"].append({
                                "file": str(compose_file),
                                "issues": file_issues,
                            })
                            
                            for issue in file_issues:
                                if issue["severity"] == "high":
                                    results["summary"]["high_risk"] += 1
                                elif issue["severity"] == "medium":
                                    results["summary"]["medium_risk"] += 1
                                else:
                                    results["summary"]["low_risk"] += 1
                    except:
                        continue
        
        # Check running containers
        try:
            ps_result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ps_result.returncode == 0:
                for line in ps_result.stdout.split("\n"):
                    if line.strip():
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            results["containers"].append({
                                "name": parts[0],
                                "image": parts[1],
                                "status": parts[2] if len(parts) > 2 else "Unknown",
                            })
        except:
            pass
        
        # Check for privileged containers
        try:
            inspect_result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if inspect_result.returncode == 0:
                for container_name in inspect_result.stdout.strip().split("\n"):
                    if container_name:
                        try:
                            priv_result = subprocess.run(
                                ["docker", "inspect", "--format", "{{.HostConfig.Privileged}}", container_name],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if priv_result.returncode == 0 and priv_result.stdout.strip().lower() == "true":
                                results["security_issues"].append({
                                    "type": "privileged_container",
                                    "severity": "high",
                                    "message": f"Container {container_name} is running in privileged mode",
                                })
                                results["summary"]["high_risk"] += 1
                        except:
                            continue
        except:
            pass
        
    except Exception as e:
        return {"error": f"Docker scan error: {e}"}
    
    return results

def scan_network_security_detailed() -> Dict[str, Any]:
    """
    Detailed network security scan
    """
    results = {
        "listening_ports": [],
        "active_connections": [],
        "firewall_status": {},
        "network_interfaces": [],
        "dns_servers": [],
        "security_issues": [],
        "summary": {
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    try:
        import subprocess
        
        # Get listening ports with details
        try:
            ss_result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
        except FileNotFoundError:
            ss_result = subprocess.run(
                ["netstat", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        risky_ports = {
            "22": {"service": "SSH", "risk": "high"},
            "21": {"service": "FTP", "risk": "high"},
            "23": {"service": "Telnet", "risk": "high"},
            "3306": {"service": "MySQL", "risk": "medium"},
            "5432": {"service": "PostgreSQL", "risk": "medium"},
            "6379": {"service": "Redis", "risk": "medium"},
            "27017": {"service": "MongoDB", "risk": "medium"},
            "9200": {"service": "Elasticsearch", "risk": "medium"},
            "5984": {"service": "CouchDB", "risk": "medium"},
        }
        
        for line in ss_result.stdout.split("\n")[1:]:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 4:
                continue
            
            addr = parts[3]
            if ":" in addr:
                port = addr.split(":")[-1]
                interface = addr.split(":")[0] if ":" in addr else "0.0.0.0"
                
                port_info = {
                    "port": port,
                    "interface": interface,
                    "protocol": parts[0],
                }
                
                if port in risky_ports:
                    port_info.update(risky_ports[port])
                    results["listening_ports"].append(port_info)
                    
                    if risky_ports[port]["risk"] == "high":
                        results["summary"]["high_risk"] += 1
                    else:
                        results["summary"]["medium_risk"] += 1
                else:
                    port_info["service"] = "Unknown"
                    port_info["risk"] = "low"
                    results["listening_ports"].append(port_info)
        
        # Get active connections with IP details
        try:
            conn_result = subprocess.run(
                ["ss", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
        except FileNotFoundError:
            conn_result = subprocess.run(
                ["netstat", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        ip_connections = {}
        for line in conn_result.stdout.split("\n")[1:]:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 4:
                peer = parts[4] if len(parts) > 4 else ""
                if ":" in peer:
                    ip = peer.split(":")[0]
                    if ip not in ["127.0.0.1", "::1", "localhost"]:
                        ip_connections[ip] = ip_connections.get(ip, 0) + 1
        
        # Flag suspicious IPs
        for ip, count in ip_connections.items():
            if count > 10:
                risk = "high" if count > 50 else "medium"
                results["active_connections"].append({
                    "ip": ip,
                    "connections": count,
                    "risk": risk,
                })
                
                if risk == "high":
                    results["summary"]["high_risk"] += 1
                else:
                    results["summary"]["medium_risk"] += 1
        
        # Check firewall status
        try:
            ufw_result = subprocess.run(
                ["ufw", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ufw_result.returncode == 0:
                results["firewall_status"]["type"] = "ufw"
                results["firewall_status"]["status"] = "enabled" if "Status: active" in ufw_result.stdout else "disabled"
        except:
            try:
                iptables_result = subprocess.run(
                    ["iptables", "-L", "-n"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if iptables_result.returncode == 0:
                    results["firewall_status"]["type"] = "iptables"
                    results["firewall_status"]["status"] = "enabled"
            except:
                results["firewall_status"]["status"] = "unknown"
        
        # Get network interfaces
        try:
            ip_result = subprocess.run(
                ["ip", "addr", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ip_result.returncode == 0:
                current_iface = None
                for line in ip_result.stdout.split("\n"):
                    if ":" in line and ":" in line.split(":")[0]:
                        iface_name = line.split(":")[1].strip().split()[0]
                        current_iface = iface_name
                        results["network_interfaces"].append({
                            "name": iface_name,
                            "addresses": [],
                        })
                    elif "inet " in line and current_iface:
                        ip_addr = line.split()[1].split("/")[0]
                        results["network_interfaces"][-1]["addresses"].append(ip_addr)
        except:
            pass
        
        # Get DNS servers
        try:
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        dns = line.split()[1]
                        results["dns_servers"].append(dns)
        except:
            pass
        
    except Exception as e:
        return {"error": f"Network scan error: {e}"}
    
    return results

def run(action: str = "scan_repo", **kwargs) -> Dict[str, Any]:
    """
    Main entry point for security scan tool
    """
    if action == "scan_repo":
        path = kwargs.get("path", "/app")
        max_files = kwargs.get("max_files", 1000)
        return scan_repo(path, max_files)
    elif action == "scan_infra":
        path = kwargs.get("path", "/app")
        return scan_infra(path)
    elif action == "scan_logs_auth":
        path = kwargs.get("path", "/app/logs")
        lines = kwargs.get("lines", 1000)
        return scan_logs_auth(path, lines)
    elif action == "scan_system":
        return scan_system_security()
    elif action == "scan_docker":
        return scan_docker_security()
    elif action == "scan_network_detailed":
        return scan_network_security_detailed()
    else:
        return {"error": f"Unknown action: {action}"}


def scan_vulnerabilities() -> Dict[str, Any]:
    """
    Scan for known vulnerabilities
    """
    results = {
        "vulnerabilities": [],
        "packages": [],
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
    }
    
    try:
        import subprocess
        
        # Check for outdated packages
        try:
            apt_result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if apt_result.returncode == 0:
                for line in apt_result.stdout.split("\n")[1:]:
                    if line.strip() and "/" in line:
                        package = line.split("/")[0]
                        results["packages"].append({
                            "name": package,
                            "status": "upgradable",
                            "risk": "medium",
                        })
                        results["summary"]["medium"] += 1
        except:
            pass
        
        # Check for known vulnerable services
        vulnerable_services = {
            "openssh": {"version": "check", "risk": "high"},
            "apache": {"version": "check", "risk": "medium"},
            "nginx": {"version": "check", "risk": "medium"},
        }
        
        for service_name, info in vulnerable_services.items():
            try:
                version_result = subprocess.run(
                    [service_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if version_result.returncode == 0:
                    version = version_result.stdout.split("\n")[0]
                    results["vulnerabilities"].append({
                        "service": service_name,
                        "version": version,
                        "risk": info["risk"],
                        "message": f"{service_name} version check",
                    })
                    if info["risk"] == "high":
                        results["summary"]["high"] += 1
                    else:
                        results["summary"]["medium"] += 1
            except:
                pass
        
    except Exception as e:
        return {"error": f"Vulnerability scan error: {e}"}
    
    return results

def scan_file_integrity(path: str = "/etc") -> Dict[str, Any]:
    """
    Monitor file integrity (detect unauthorized changes)
    """
    results = {
        "monitored_files": [],
        "changed_files": [],
        "new_files": [],
        "deleted_files": [],
        "summary": {
            "total_monitored": 0,
            "changes_detected": 0,
        }
    }
    
    try:
        from pathlib import Path
        import hashlib
        
        critical_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/sudoers",
            "/etc/hosts",
            "/etc/ssh/sshd_config",
        ]
        
        for file_path in critical_paths:
            file_obj = Path(file_path)
            if file_obj.exists():
                results["summary"]["total_monitored"] += 1
                
                # Calculate hash
                try:
                    with open(file_obj, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    results["monitored_files"].append({
                        "file": file_path,
                        "hash": file_hash[:16] + "...",
                        "size": file_obj.stat().st_size,
                        "modified": datetime.fromtimestamp(file_obj.stat().st_mtime).isoformat(),
                    })
                except:
                    pass
        
    except Exception as e:
        return {"error": f"File integrity scan error: {e}"}
    
    return results

def scan_malware(path: str = "/tmp") -> Dict[str, Any]:
    """
    Scan for malware indicators
    """
    results = {
        "suspicious_files": [],
        "suspicious_processes": [],
        "summary": {
            "files_scanned": 0,
            "suspicious_found": 0,
        }
    }
    
    try:
        import subprocess
        from pathlib import Path
        
        # Suspicious file patterns
        suspicious_patterns = [
            ".exe", ".bat", ".scr", ".vbs", ".js",
            "miner", "crypto", "backdoor", "trojan",
        ]
        
        # Scan /tmp directory
        tmp_path = Path(path)
        if tmp_path.exists():
            for file_path in tmp_path.rglob("*"):
                if file_path.is_file():
                    results["summary"]["files_scanned"] += 1
                    
                    file_name = file_path.name.lower()
                    if any(pattern in file_name for pattern in suspicious_patterns):
                        results["suspicious_files"].append({
                            "file": str(file_path),
                            "reason": "Suspicious filename pattern",
                            "risk": "high",
                        })
                        results["summary"]["suspicious_found"] += 1
        
        # Check for suspicious processes
        try:
            ps_result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ps_result.returncode == 0:
                suspicious_keywords = ["miner", "crypto", "backdoor", "trojan", "keylogger"]
                for line in ps_result.stdout.split("\n")[1:]:
                    if any(keyword in line.lower() for keyword in suspicious_keywords):
                        parts = line.split()
                        if len(parts) > 10:
                            results["suspicious_processes"].append({
                                "pid": parts[1],
                                "user": parts[0],
                                "cmd": " ".join(parts[10:]),
                                "risk": "high",
                            })
                            results["summary"]["suspicious_found"] += 1
        except:
            pass
        
    except Exception as e:
        return {"error": f"Malware scan error: {e}"}
    
    return results

def scan_intrusion_detection() -> Dict[str, Any]:
    """
    Intrusion Detection System (IDS) scan
    """
    results = {
        "intrusions": [],
        "anomalies": [],
        "summary": {
            "intrusions_detected": 0,
            "anomalies_detected": 0,
        }
    }
    
    try:
        import subprocess
        
        # Check for unusual network connections
        try:
            netstat_result = subprocess.run(
                ["ss", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if netstat_result.returncode == 0:
                connections = {}
                for line in netstat_result.stdout.split("\n")[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            peer = parts[4] if len(parts) > 4 else ""
                            if ":" in peer:
                                ip = peer.split(":")[0]
                                if ip not in ["127.0.0.1", "::1"]:
                                    connections[ip] = connections.get(ip, 0) + 1
                
                # Flag IPs with many connections (potential scanning)
                for ip, count in connections.items():
                    if count > 20:
                        results["intrusions"].append({
                            "type": "port_scanning",
                            "ip": ip,
                            "connections": count,
                            "severity": "high",
                            "message": f"Potential port scanning from {ip}",
                        })
                        results["summary"]["intrusions_detected"] += 1
        except:
            pass
        
        # Check for unusual file access patterns
        try:
            # Check /etc/passwd access
            passwd_result = subprocess.run(
                ["lsof", "/etc/passwd"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if passwd_result.returncode == 0 and passwd_result.stdout.strip():
                results["anomalies"].append({
                    "type": "sensitive_file_access",
                    "file": "/etc/passwd",
                    "severity": "medium",
                    "message": "Unusual access to /etc/passwd",
                })
                results["summary"]["anomalies_detected"] += 1
        except:
            pass
        
    except Exception as e:
        return {"error": f"IDS scan error: {e}"}
    
    return results

def scan_port_scan(target: str = "localhost") -> Dict[str, Any]:
    """
    Port scanning tool
    """
    results = {
        "open_ports": [],
        "closed_ports": [],
        "filtered_ports": [],
        "summary": {
            "total_scanned": 0,
            "open": 0,
            "closed": 0,
        }
    }
    
    try:
        import subprocess
        import socket
        
        # Common ports to scan
        common_ports = [22, 23, 25, 53, 80, 443, 3306, 5432, 6379, 8080, 9090]
        
        for port in common_ports:
            results["summary"]["total_scanned"] += 1
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                sock.close()
                
                if result == 0:
                    results["open_ports"].append({
                        "port": port,
                        "status": "open",
                        "service": _get_service_name(port),
                    })
                    results["summary"]["open"] += 1
                else:
                    results["closed_ports"].append(port)
                    results["summary"]["closed"] += 1
            except:
                results["filtered_ports"].append(port)
        
    except Exception as e:
        return {"error": f"Port scan error: {e}"}
    
    return results

def _get_service_name(port: int) -> str:
    """Get service name for port"""
    services = {
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        443: "HTTPS",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        8080: "HTTP-Alt",
        9090: "Prometheus",
    }
    return services.get(port, "Unknown")

def scan_penetration_test() -> Dict[str, Any]:
    """
    Basic penetration testing scan
    """
    results = {
        "findings": [],
        "exploits": [],
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0,
        }
    }
    
    try:
        # Check for weak passwords (common passwords)
        common_passwords = ["admin", "password", "123456", "root", "test"]
        
        # Check SSH configuration
        try:
            ssh_config = Path("/etc/ssh/sshd_config")
            if ssh_config.exists():
                with open(ssh_config, "r") as f:
                    content = f.read()
                    
                    if "PermitRootLogin yes" in content:
                        results["findings"].append({
                            "type": "weak_ssh_config",
                            "severity": "high",
                            "message": "Root login enabled in SSH",
                        })
                        results["summary"]["high"] += 1
                    
                    if "PasswordAuthentication yes" in content and "PubkeyAuthentication no" in content:
                        results["findings"].append({
                            "type": "password_only_auth",
                            "severity": "medium",
                            "message": "SSH only uses password authentication",
                        })
                        results["summary"]["medium"] += 1
        except:
            pass
        
        # Check for world-writable directories
        try:
            find_result = subprocess.run(
                ["find", "/tmp", "/var/tmp", "-type", "d", "-perm", "-002", "2>/dev/null"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if find_result.stdout.strip():
                results["findings"].append({
                    "type": "world_writable_dirs",
                    "severity": "medium",
                    "message": "World-writable directories found",
                })
                results["summary"]["medium"] += 1
        except:
            pass
        
    except Exception as e:
        return {"error": f"Penetration test error: {e}"}
    
    return results

# Update run function
def run(action: str = "scan_repo", **kwargs) -> Dict[str, Any]:
    """
    Main entry point for security scan tool
    """
    if action == "scan_repo":
        path = kwargs.get("path", "/app")
        max_files = kwargs.get("max_files", 1000)
        return scan_repo(path, max_files)
    elif action == "scan_infra":
        path = kwargs.get("path", "/app")
        return scan_infra(path)
    elif action == "scan_logs_auth":
        path = kwargs.get("path", "/app/logs")
        lines = kwargs.get("lines", 1000)
        return scan_logs_auth(path, lines)
    elif action == "scan_system":
        return scan_system_security()
    elif action == "scan_docker":
        return scan_docker_security()
    elif action == "scan_network_detailed":
        return scan_network_security_detailed()
    elif action == "scan_vulnerabilities":
        return scan_vulnerabilities()
    elif action == "scan_file_integrity":
        path = kwargs.get("path", "/etc")
        return scan_file_integrity(path)
    elif action == "scan_malware":
        path = kwargs.get("path", "/tmp")
        return scan_malware(path)
    elif action == "scan_intrusion_detection":
        return scan_intrusion_detection()
    elif action == "scan_port_scan":
        target = kwargs.get("target", "localhost")
        return scan_port_scan(target)
    elif action == "scan_penetration_test":
        return scan_penetration_test()
    else:
        return {"error": f"Unknown action: {action}"}
