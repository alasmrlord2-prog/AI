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
        
        # System info - use EnvAdapter
        uname_result = env_adapter.exec(["uname", "-a"], timeout=5)
        results["system_info"]["os"] = uname_result.stdout.strip() if uname_result.success else "Unknown"
        results["system_info"]["platform"] = env_adapter.get_system_info()
        
        # Check for root login - use EnvAdapter
        if env_adapter.tool_installed("grep"):
            passwd_result = env_adapter.exec(
                ["grep", "^root:", "/etc/passwd"],
                timeout=5
            )
            if passwd_result.success and passwd_result.stdout:
                shell = passwd_result.stdout.split(":")[-1].strip()
                if shell not in ["/sbin/nologin", "/bin/false"]:
                    results["security_issues"].append({
                        "type": "root_login_enabled",
                        "severity": "high",
                        "message": "Root login may be enabled",
                    })
                    results["summary"]["high_risk"] += 1
        
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
        except Exception as e:
            log_error(e, context="scan_system_security: get_users")
            pass
        
        # Check for sudo users - use EnvAdapter
        if env_adapter.tool_installed("grep"):
            sudo_result = env_adapter.exec(
                ["grep", "-E", "^[^#].*ALL.*NOPASSWD", "/etc/sudoers"],
                timeout=5
            )
            if sudo_result.success and sudo_result.stdout.strip():
                results["security_issues"].append({
                    "type": "passwordless_sudo",
                    "severity": "high",
                    "message": "Passwordless sudo detected",
                    "details": sudo_result.stdout.strip(),
                })
                results["summary"]["high_risk"] += 1
        
        # Check running services - use capability detection
        if capability_detector.is_feature_available("service_scan"):
            systemctl_result = env_adapter.exec(
                ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"],
                timeout=10
            )
            if systemctl_result.success:
                services = []
                for line in systemctl_result.stdout.split("\n")[1:]:
                    if line.strip() and ".service" in line:
                        service_name = line.split()[0]
                        services.append(service_name)
                results["services"] = services[:20]  # Limit to 20
        
        # Check for suspicious processes - use EnvAdapter
        if capability_detector.is_feature_available("process_scan"):
            ps_result = env_adapter.exec(
                ["ps", "aux"],
                timeout=5
            )
            if ps_result.success:
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
        
        # Check file permissions - use EnvAdapter
        if env_adapter.tool_installed("find"):
            find_result = env_adapter.exec(
                ["find", "/tmp", "/var/tmp", "-type", "f", "-perm", "-002"],
                timeout=5
            )
            if find_result.success and find_result.stdout.strip():
                results["security_issues"].append({
                    "type": "world_writable_files",
                    "severity": "medium",
                    "message": "World-writable files found in /tmp",
                })
                results["summary"]["medium_risk"] += 1
        
    except Exception as e:
        log_error(e, context="scan_system_security")
        raise ScanExecutionError(f"System scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"System scan completed: {len(results['security_issues'])} issues found")
    return results

