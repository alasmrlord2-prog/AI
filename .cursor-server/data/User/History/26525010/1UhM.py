"""
System Scanner - ماسح النظام
"""
import pwd
from typing import Dict, Any
from .base import calculate_risk_score
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from app.utils.env_adapter import env_adapter
from app.utils.capability_detector import capability_detector
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
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
        log_info("Scanning system security")
        
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
        log_error(e, context="scan_system_security")
        raise ScanExecutionError(f"System scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"System scan completed: {len(results['security_issues'])} issues found")
    return results

