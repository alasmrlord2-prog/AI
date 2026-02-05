"""
Advanced Security Tools - أدوات أمنية متقدمة
"""
import os
import re
import json
import subprocess
import hashlib
import socket
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from app.utils.path_resolver import resolve_path

# ===== Threat Intelligence =====

def check_abuseipdb(ip: str) -> Dict[str, Any]:
    """Check IP against AbuseIPDB (requires API key)"""
    return {
        "ip": ip,
        "source": "abuseipdb",
        "status": "requires_api_key",
        "message": "AbuseIPDB check requires API key configuration"
    }

def check_virustotal(ip_or_hash: str) -> Dict[str, Any]:
    """Check IP/Hash against VirusTotal (requires API key)"""
    return {
        "target": ip_or_hash,
        "source": "virustotal",
        "status": "requires_api_key",
        "message": "VirusTotal check requires API key configuration"
    }

def check_shodan(ip: str) -> Dict[str, Any]:
    """Check IP against Shodan (requires API key)"""
    return {
        "ip": ip,
        "source": "shodan",
        "status": "requires_api_key",
        "message": "Shodan check requires API key configuration"
    }

def threat_intelligence_scan(ip: str) -> Dict[str, Any]:
    """Comprehensive threat intelligence scan"""
    results = {
        "ip": ip,
        "checks": [],
        "reputation": "unknown",
        "threat_level": "low"
    }
    
    # Basic checks without API keys
    try:
        # Check if IP is private
        parts = ip.split(".")
        if len(parts) == 4:
            first_octet = int(parts[0])
            if first_octet == 10 or (first_octet == 172 and 16 <= int(parts[1]) <= 31) or (first_octet == 192 and int(parts[1]) == 168):
                results["reputation"] = "private"
                results["threat_level"] = "low"
                results["checks"].append({
                    "source": "internal",
                    "status": "private_ip",
                    "message": "Private IP address"
                })
    except:
        pass
    
    # Add API-based checks (placeholder)
    results["checks"].append(check_abuseipdb(ip))
    results["checks"].append(check_virustotal(ip))
    results["checks"].append(check_shodan(ip))
    
    return results

# ===== Network Forensics =====

def analyze_packet_capture(file_path: str) -> Dict[str, Any]:
    """Analyze packet capture file (pcap)"""
    results = {
        "file": file_path,
        "packets": 0,
        "protocols": {},
        "connections": [],
        "suspicious_activity": []
    }
    
    try:
        # Resolve path using advanced path resolver
        resolved_path = resolve_path(file_path)
        
        # Try tcpdump/tshark analysis
        if not Path(resolved_path).exists():
            return {"error": f"File not found: {file_path} (resolved to: {resolved_path})"}
        
        # Basic analysis with tcpdump
        try:
            tcpdump_result = subprocess.run(
                ["tcpdump", "-r", resolved_path, "-c", "100"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if tcpdump_result.returncode == 0:
                lines = tcpdump_result.stdout.split("\n")
                results["packets"] = len([l for l in lines if l.strip()])
                results["file"] = resolved_path  # Update with resolved path
        except:
            pass
        
    except Exception as e:
        return {"error": f"Packet analysis error: {e}"}
    
    return results

def network_traffic_analysis() -> Dict[str, Any]:
    """Real-time network traffic analysis"""
    results = {
        "active_connections": [],
        "bandwidth_usage": {},
        "top_connections": [],
        "suspicious_patterns": []
    }
    
    try:
        # Get active connections
        try:
            ss_result = subprocess.run(
                ["ss", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ss_result.returncode == 0:
                connections = {}
                for line in ss_result.stdout.split("\n")[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            peer = parts[4] if len(parts) > 4 else ""
                            if ":" in peer:
                                ip = peer.split(":")[0]
                                connections[ip] = connections.get(ip, 0) + 1
                
                results["top_connections"] = sorted(
                    connections.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
        except:
            pass
        
    except Exception as e:
        return {"error": f"Traffic analysis error: {e}"}
    
    return results

# ===== Vulnerability Assessment =====

def advanced_vulnerability_scan() -> Dict[str, Any]:
    """Advanced vulnerability scanning"""
    results = {
        "cve_database": [],
        "vulnerable_packages": [],
        "exploits": [],
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0
        }
    }
    
    try:
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
                        results["vulnerable_packages"].append({
                            "package": package,
                            "status": "upgradable",
                            "risk": "medium"
                        })
                        results["summary"]["medium"] += 1
        except:
            pass
        
        # Check for known vulnerable services
        vulnerable_services = {
            "openssh": {"cve": "CVE-2024-XXXX", "risk": "high"},
            "apache": {"cve": "CVE-2024-XXXX", "risk": "medium"},
        }
        
        for service, info in vulnerable_services.items():
            try:
                version_result = subprocess.run(
                    [service, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if version_result.returncode == 0:
                    results["cve_database"].append({
                        "service": service,
                        "cve": info["cve"],
                        "risk": info["risk"]
                    })
                    if info["risk"] == "high":
                        results["summary"]["high"] += 1
            except:
                pass
        
    except Exception as e:
        return {"error": f"Vulnerability scan error: {e}"}
    
    return results

# ===== Web Application Security =====

def web_vulnerability_scan(url: str) -> Dict[str, Any]:
    """Advanced web vulnerability scanning"""
    results = {
        "url": url,
        "vulnerabilities": [],
        "headers": {},
        "technologies": [],
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0
        }
    }
    
    try:
        import requests
        
        # Check HTTP headers
        try:
            response = requests.get(url, timeout=10, verify=False, allow_redirects=True)
            results["headers"] = dict(response.headers)
            
            # Check for security headers
            security_headers = {
                "X-Frame-Options": "medium",
                "X-Content-Type-Options": "low",
                "Strict-Transport-Security": "high",
                "Content-Security-Policy": "medium",
            }
            
            for header, risk in security_headers.items():
                if header not in response.headers:
                    results["vulnerabilities"].append({
                        "type": f"missing_{header.lower().replace('-', '_')}",
                        "severity": risk,
                        "message": f"Missing security header: {header}"
                    })
                    if risk == "high":
                        results["summary"]["high"] += 1
                    elif risk == "medium":
                        results["summary"]["medium"] += 1
        except:
            pass
        
    except Exception as e:
        return {"error": f"Web scan error: {e}"}
    
    return results

# ===== Container Security (Advanced) =====

def advanced_container_scan() -> Dict[str, Any]:
    """Advanced container security scanning"""
    results = {
        "containers": [],
        "images": [],
        "runtime_issues": [],
        "compliance": {},
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0
        }
    }
    
    try:
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
                            container_info = {
                                "name": parts[0],
                                "image": parts[1],
                                "status": parts[2] if len(parts) > 2 else "Unknown"
                            }
                            
                            # Check for privileged mode
                            try:
                                inspect_result = subprocess.run(
                                    ["docker", "inspect", "--format", "{{.HostConfig.Privileged}}", parts[0]],
                                    capture_output=True,
                                    text=True,
                                    timeout=5
                                )
                                if "true" in inspect_result.stdout:
                                    results["runtime_issues"].append({
                                        "container": parts[0],
                                        "issue": "privileged_mode",
                                        "severity": "critical",
                                        "message": "Container running in privileged mode"
                                    })
                                    results["summary"]["critical"] += 1
                            except:
                                pass
                            
                            results["containers"].append(container_info)
        except:
            pass
        
        # Check images
        try:
            images_result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}\t{{.Tag}}\t{{.Size}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if images_result.returncode == 0:
                for line in images_result.stdout.split("\n"):
                    if line.strip():
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            results["images"].append({
                                "repository": parts[0],
                                "tag": parts[1],
                                "size": parts[2] if len(parts) > 2 else "Unknown"
                            })
        except:
            pass
        
    except Exception as e:
        return {"error": f"Container scan error: {e}"}
    
    return results

# ===== Kubernetes Security =====

def kubernetes_security_scan() -> Dict[str, Any]:
    """Kubernetes security scanning"""
    results = {
        "pods": [],
        "services": [],
        "rbac_issues": [],
        "network_policies": [],
        "secrets": [],
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0
        }
    }
    
    try:
        # Check if kubectl is available
        try:
            kubectl_result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if kubectl_result.returncode == 0:
                # Get pods
                try:
                    pods_result = subprocess.run(
                        ["kubectl", "get", "pods", "-o", "json"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if pods_result.returncode == 0:
                        pods_data = json.loads(pods_result.stdout)
                        results["pods"] = [pod["metadata"]["name"] for pod in pods_data.get("items", [])]
                except:
                    pass
                
                # Check for secrets
                try:
                    secrets_result = subprocess.run(
                        ["kubectl", "get", "secrets", "-o", "json"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if secrets_result.returncode == 0:
                        secrets_data = json.loads(secrets_result.stdout)
                        results["secrets"] = [s["metadata"]["name"] for s in secrets_data.get("items", [])]
                except:
                    pass
        except FileNotFoundError:
            results["error"] = "kubectl not available"
        except:
            pass
        
    except Exception as e:
        return {"error": f"K8s scan error: {e}"}
    
    return results

# ===== Cloud Security =====

def aws_security_scan() -> Dict[str, Any]:
    """AWS security scanning"""
    results = {
        "s3_buckets": [],
        "iam_issues": [],
        "security_groups": [],
        "compliance": {},
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0
        }
    }
    
    try:
        # Check if AWS CLI is available
        try:
            aws_result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if aws_result.returncode == 0:
                # Check S3 buckets
                try:
                    s3_result = subprocess.run(
                        ["aws", "s3", "ls"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if s3_result.returncode == 0:
                        for line in s3_result.stdout.split("\n"):
                            if line.strip():
                                bucket_name = line.split()[-1]
                                results["s3_buckets"].append(bucket_name)
                except:
                    pass
        except FileNotFoundError:
            results["error"] = "AWS CLI not available"
        except:
            pass
        
    except Exception as e:
        return {"error": f"AWS scan error: {e}"}
    
    return results

# ===== Digital Forensics =====

def memory_forensics() -> Dict[str, Any]:
    """Memory forensics analysis"""
    results = {
        "processes": [],
        "network_connections": [],
        "suspicious_activity": [],
        "summary": {
            "processes_found": 0,
            "suspicious_processes": 0
        }
    }
    
    try:
        # Get running processes
        try:
            ps_result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ps_result.returncode == 0:
                suspicious_keywords = ["nc ", "netcat", "nmap", "masscan", "hydra", "sqlmap", "backdoor"]
                for line in ps_result.stdout.split("\n")[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) > 10:
                            cmd = " ".join(parts[10:])
                            if any(keyword in cmd.lower() for keyword in suspicious_keywords):
                                results["suspicious_activity"].append({
                                    "pid": parts[1],
                                    "user": parts[0],
                                    "cmd": cmd,
                                    "risk": "high"
                                })
                                results["summary"]["suspicious_processes"] += 1
                            else:
                                results["processes"].append({
                                    "pid": parts[1],
                                    "user": parts[0],
                                    "cmd": cmd
                                })
                                results["summary"]["processes_found"] += 1
        except:
            pass
        
    except Exception as e:
        return {"error": f"Memory forensics error: {e}"}
    
    return results

def disk_forensics(path: str = "/") -> Dict[str, Any]:
    """Disk forensics analysis"""
    results = {
        "deleted_files": [],
        "hidden_files": [],
        "suspicious_files": [],
        "timeline": [],
        "summary": {
            "files_analyzed": 0,
            "suspicious_found": 0
        }
    }
    
    try:
        from pathlib import Path
        
        # Find hidden files
        base = Path(path)
        if base.exists():
            for file_path in base.rglob(".*"):
                if file_path.is_file():
                    results["hidden_files"].append(str(file_path))
                    results["summary"]["files_analyzed"] += 1
        
        # Find suspicious file patterns
        suspicious_patterns = [".exe", ".bat", ".scr", ".vbs", "miner", "crypto"]
        for file_path in base.rglob("*"):
            if file_path.is_file():
                file_name = file_path.name.lower()
                if any(pattern in file_name for pattern in suspicious_patterns):
                    results["suspicious_files"].append({
                        "file": str(file_path),
                        "reason": "Suspicious filename pattern",
                        "risk": "high"
                    })
                    results["summary"]["suspicious_found"] += 1
        
    except Exception as e:
        return {"error": f"Disk forensics error: {e}"}
    
    return results

# ===== Password Security =====

def password_audit() -> Dict[str, Any]:
    """Password security audit"""
    results = {
        "weak_passwords": [],
        "password_policies": {},
        "summary": {
            "weak_found": 0,
            "policy_violations": 0
        }
    }
    
    try:
        # Check password policy
        try:
            login_defs = Path("/etc/login.defs")
            if login_defs.exists():
                with open(login_defs, "r") as f:
                    content = f.read()
                    if "PASS_MIN_LEN" in content:
                        min_len = re.search(r"PASS_MIN_LEN\s+(\d+)", content)
                        if min_len:
                            results["password_policies"]["min_length"] = int(min_len.group(1))
        except:
            pass
        
    except Exception as e:
        return {"error": f"Password audit error: {e}"}
    
    return results

# ===== Compliance & Hardening =====

def compliance_check(standard: str = "CIS") -> Dict[str, Any]:
    """Compliance checking (CIS, STIG, etc.)"""
    results = {
        "standard": standard,
        "checks": [],
        "passed": 0,
        "failed": 0,
        "summary": {
            "compliance_score": 0
        }
    }
    
    try:
        # Basic CIS checks
        if standard == "CIS":
            # Check SSH configuration
            ssh_config = Path("/etc/ssh/sshd_config")
            if ssh_config.exists():
                with open(ssh_config, "r") as f:
                    content = f.read()
                    
                    checks = [
                        ("PermitRootLogin", "no", "high"),
                        ("PasswordAuthentication", "no", "medium"),
                        ("PubkeyAuthentication", "yes", "medium"),
                    ]
                    
                    for check_name, expected, severity in checks:
                        pattern = rf"{check_name}\s+(\S+)"
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            value = match.group(1).lower()
                            if value != expected.lower():
                                results["checks"].append({
                                    "check": check_name,
                                    "status": "failed",
                                    "expected": expected,
                                    "actual": value,
                                    "severity": severity
                                })
                                results["failed"] += 1
                            else:
                                results["checks"].append({
                                    "check": check_name,
                                    "status": "passed"
                                })
                                results["passed"] += 1
        
        if results["passed"] + results["failed"] > 0:
            results["summary"]["compliance_score"] = (results["passed"] / (results["passed"] + results["failed"])) * 100
        
    except Exception as e:
        return {"error": f"Compliance check error: {e}"}
    
    return results

# ===== Burp Suite Integration =====

def burp_suite_scan(url: str) -> Dict[str, Any]:
    """Burp Suite-like web vulnerability scanning"""
    results = {
        "url": url,
        "vulnerabilities": [],
        "endpoints": [],
        "security_headers": {},
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
    }
    
    try:
        import requests
        from urllib.parse import urljoin, urlparse
        
        # Test for common vulnerabilities
        test_urls = [
            url,
            urljoin(url, "/admin"),
            urljoin(url, "/api"),
            urljoin(url, "/.env"),
            urljoin(url, "/config.php"),
        ]
        
        for test_url in test_urls:
            try:
                response = requests.get(test_url, timeout=5, verify=False, allow_redirects=False)
                
                # Check for sensitive files
                if response.status_code == 200:
                    if ".env" in test_url or "config" in test_url:
                        results["vulnerabilities"].append({
                            "type": "sensitive_file_exposed",
                            "severity": "high",
                            "url": test_url,
                            "message": f"Sensitive file accessible: {test_url}"
                        })
                        results["summary"]["high"] += 1
                
                # Check security headers
                security_headers = {
                    "X-Frame-Options": "medium",
                    "X-Content-Type-Options": "low",
                    "Strict-Transport-Security": "high",
                    "Content-Security-Policy": "medium",
                    "X-XSS-Protection": "low",
                }
                
                for header, risk in security_headers.items():
                    if header not in response.headers:
                        results["vulnerabilities"].append({
                            "type": f"missing_{header.lower().replace('-', '_')}",
                            "severity": risk,
                            "url": test_url,
                            "message": f"Missing security header: {header}"
                        })
                        if risk == "high":
                            results["summary"]["high"] += 1
                        elif risk == "medium":
                            results["summary"]["medium"] += 1
                        else:
                            results["summary"]["low"] += 1
                
                results["endpoints"].append({
                    "url": test_url,
                    "status": response.status_code,
                    "headers": dict(response.headers)
                })
                
            except:
                pass
        
        # SQL Injection test
        sql_test_payloads = ["'", "1' OR '1'='1", "1' UNION SELECT NULL--"]
        for payload in sql_test_payloads:
            try:
                test_url = f"{url}?id={payload}"
                response = requests.get(test_url, timeout=5, verify=False)
                if any(keyword in response.text.lower() for keyword in ["sql", "mysql", "error", "syntax"]):
                    results["vulnerabilities"].append({
                        "type": "sql_injection",
                        "severity": "critical",
                        "url": test_url,
                        "message": "Potential SQL injection vulnerability detected"
                    })
                    results["summary"]["critical"] += 1
            except:
                pass
        
        # XSS test
        xss_payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]
        for payload in xss_payloads:
            try:
                test_url = f"{url}?q={payload}"
                response = requests.get(test_url, timeout=5, verify=False)
                if payload in response.text:
                    results["vulnerabilities"].append({
                        "type": "xss",
                        "severity": "high",
                        "url": test_url,
                        "message": "Potential XSS vulnerability detected"
                    })
                    results["summary"]["high"] += 1
            except:
                pass
        
    except Exception as e:
        return {"error": f"Burp Suite scan error: {e}"}
    
    return results

# ===== Metasploit Integration =====

def metasploit_scan(target: str, port: int = None) -> Dict[str, Any]:
    """Metasploit-like vulnerability and exploit scanning"""
    results = {
        "target": target,
        "ports": [],
        "services": [],
        "vulnerabilities": [],
        "exploits": [],
        "summary": {
            "exploitable": 0,
            "vulnerable_services": 0
        }
    }
    
    try:
        import socket
        
        # Port scanning
        common_ports = [22, 23, 25, 53, 80, 443, 3306, 5432, 6379, 8080, 9090] if not port else [port]
        
        for port_num in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port_num))
                sock.close()
                
                if result == 0:
                    service_name = _get_service_name(port_num)
                    results["ports"].append({
                        "port": port_num,
                        "status": "open",
                        "service": service_name
                    })
                    
                    # Check for known vulnerabilities
                    vulnerable_services = {
                        22: {"cve": "CVE-2024-XXXX", "risk": "high", "exploit": "SSH brute-force"},
                        3306: {"cve": "CVE-2024-XXXX", "risk": "critical", "exploit": "MySQL injection"},
                        5432: {"cve": "CVE-2024-XXXX", "risk": "high", "exploit": "PostgreSQL injection"},
                    }
                    
                    if port_num in vulnerable_services:
                        vuln_info = vulnerable_services[port_num]
                        results["vulnerabilities"].append({
                            "port": port_num,
                            "service": service_name,
                            "cve": vuln_info["cve"],
                            "risk": vuln_info["risk"],
                            "exploit": vuln_info["exploit"]
                        })
                        results["exploits"].append({
                            "target": f"{target}:{port_num}",
                            "service": service_name,
                            "exploit": vuln_info["exploit"],
                            "risk": vuln_info["risk"]
                        })
                        results["summary"]["exploitable"] += 1
                        results["summary"]["vulnerable_services"] += 1
            except:
                pass
        
    except Exception as e:
        return {"error": f"Metasploit scan error: {e}"}
    
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

# ===== Advanced Packet Analysis =====

def advanced_packet_analysis(file_path: str = None) -> Dict[str, Any]:
    """Advanced packet capture analysis (Wireshark-like)"""
    results = {
        "packets_analyzed": 0,
        "protocols": {},
        "connections": [],
        "suspicious_traffic": [],
        "dns_queries": [],
        "http_requests": [],
        "summary": {
            "total_packets": 0,
            "suspicious_packets": 0,
            "protocols_found": []
        }
    }
    
    try:
        import subprocess
        
        # If file provided, analyze it
        if file_path and Path(file_path).exists():
            try:
                tcpdump_result = subprocess.run(
                    ["tcpdump", "-r", file_path, "-c", "1000", "-n"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if tcpdump_result.returncode == 0:
                    lines = tcpdump_result.stdout.split("\n")
                    results["summary"]["total_packets"] = len([l for l in lines if l.strip()])
                    
                    # Analyze protocols
                    for line in lines:
                        if "IP" in line:
                            results["protocols"]["IP"] = results["protocols"].get("IP", 0) + 1
                        if "TCP" in line:
                            results["protocols"]["TCP"] = results["protocols"].get("TCP", 0) + 1
                        if "UDP" in line:
                            results["protocols"]["UDP"] = results["protocols"].get("UDP", 0) + 1
                        if "DNS" in line:
                            results["protocols"]["DNS"] = results["protocols"].get("DNS", 0) + 1
                    
                    results["summary"]["protocols_found"] = list(results["protocols"].keys())
            except:
                pass
        else:
            # Real-time network analysis
            try:
                # Get active connections
                ss_result = subprocess.run(
                    ["ss", "-tn"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if ss_result.returncode == 0:
                    connections = {}
                    for line in ss_result.stdout.split("\n")[1:]:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 4:
                                peer = parts[4] if len(parts) > 4 else ""
                                if ":" in peer:
                                    ip = peer.split(":")[0]
                                    port = peer.split(":")[1]
                                    connections[f"{ip}:{port}"] = connections.get(f"{ip}:{port}", 0) + 1
                    
                    results["connections"] = [
                        {"connection": conn, "count": count}
                        for conn, count in sorted(connections.items(), key=lambda x: x[1], reverse=True)[:20]
                    ]
            except:
                pass
            
            # Check for suspicious patterns
            try:
                netstat_result = subprocess.run(
                    ["ss", "-tn"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if netstat_result.returncode == 0:
                    suspicious_ips = {}
                    for line in netstat_result.stdout.split("\n")[1:]:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 4:
                                peer = parts[4] if len(parts) > 4 else ""
                                if ":" in peer:
                                    ip = peer.split(":")[0]
                                    if ip not in ["127.0.0.1", "::1"]:
                                        suspicious_ips[ip] = suspicious_ips.get(ip, 0) + 1
                    
                    for ip, count in suspicious_ips.items():
                        if count > 20:
                            results["suspicious_traffic"].append({
                                "ip": ip,
                                "connections": count,
                                "reason": "High connection count (potential scanning)",
                                "risk": "high"
                            })
                            results["summary"]["suspicious_packets"] += 1
            except:
                pass
        
    except Exception as e:
        return {"error": f"Packet analysis error: {e}"}
    
    return results

# ===== Main Entry Point =====

def run_advanced_scan(scan_type: str, **kwargs) -> Dict[str, Any]:
    """Main entry point for advanced security scans"""
    if scan_type == "threat_intelligence":
        ip = kwargs.get("ip", "127.0.0.1")
        return threat_intelligence_scan(ip)
    elif scan_type == "network_forensics":
        return network_traffic_analysis()
    elif scan_type == "packet_analysis":
        file_path = kwargs.get("file_path", "")
        return analyze_packet_capture(file_path)
    elif scan_type == "advanced_vulnerability":
        return advanced_vulnerability_scan()
    elif scan_type == "web_scan":
        url = kwargs.get("url", "")
        return web_vulnerability_scan(url)
    elif scan_type == "advanced_container":
        return advanced_container_scan()
    elif scan_type == "kubernetes":
        return kubernetes_security_scan()
    elif scan_type == "aws":
        return aws_security_scan()
    elif scan_type == "memory_forensics":
        return memory_forensics()
    elif scan_type == "disk_forensics":
        path = kwargs.get("path", "/")
        return disk_forensics(path)
    elif scan_type == "password_audit":
        return password_audit()
    elif scan_type == "compliance":
        standard = kwargs.get("standard", "CIS")
        return compliance_check(standard)
    elif scan_type == "burp_suite":
        url = kwargs.get("url", "")
        return burp_suite_scan(url)
    elif scan_type == "metasploit":
        target = kwargs.get("target", "localhost")
        port = kwargs.get("port", None)
        return metasploit_scan(target, port)
    elif scan_type == "packet_analysis":
        file_path = kwargs.get("file_path", None)
        return advanced_packet_analysis(file_path)
    else:
        return {"error": f"Unknown scan type: {scan_type}"}
