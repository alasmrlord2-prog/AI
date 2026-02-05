import os
import re
import json
from typing import Dict, List, Any
from pathlib import Path

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

def scan_repo(path: str = "/app", max_files: int = 1000) -> Dict[str, Any]:
    """
    Scan repository for secrets and security issues
    """
    results = {
        "path": path,
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
    
    # Excluded patterns
    excluded = [
        ".git", "__pycache__", "node_modules", ".next",
        "venv", "env", ".env", "*.pyc", "*.log"
    ]
    
    try:
        root = Path(path)
        if not root.exists():
            return {"error": f"Path does not exist: {path}"}
        
        file_count = 0
        for file_path in root.rglob("*"):
            if file_count >= max_files:
                break
            
            # Skip excluded
            if any(exc in str(file_path) for exc in excluded):
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
    results = {
        "path": path,
        "issues": [],
        "summary": {
            "containers_as_root": 0,
            "exposed_ports": [],
            "missing_secrets": 0,
            "insecure_configs": 0,
        }
    }
    
    try:
        root = Path(path)
        
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
        
        # Get listening ports
        result = subprocess.run(
            ["ss", "-tlnp"],
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
        conn_result = subprocess.run(
            ["ss", "-tn"],
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
    results = {
        "path": path,
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
        log_path = Path(path)
        if not log_path.exists():
            return {"error": f"Log path does not exist: {path}"}
        
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
    else:
        return {"error": f"Unknown action: {action}"}

