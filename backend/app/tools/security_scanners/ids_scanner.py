"""
Intrusion Detection Scanner - ماسح اكتشاف التسلل
"""
import subprocess
import os
from typing import Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from .base import calculate_risk_score
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta as td

@handle_scan_errors
@cached(ttl=td(minutes=15))
def scan_intrusion_detection() -> Dict[str, Any]:
    """
    Enhanced Intrusion Detection System (IDS) scan
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
        log_info("Scanning for intrusions")
        
        # Check auth.log for sudo failures
        try:
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
        except:
            pass
        
        # Check for new cron jobs
        try:
            cron_result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if cron_result.returncode == 0:
                # Check for suspicious cron jobs
                suspicious_patterns = ["curl", "wget", "bash", "sh", "python", "perl"]
                for line in cron_result.stdout.split("\n"):
                    if any(pattern in line.lower() for pattern in suspicious_patterns):
                        results["anomalies"].append({
                            "type": "suspicious_cron_job",
                            "severity": "medium",
                            "message": f"Suspicious cron job: {line.strip()[:100]}",
                        })
                        results["summary"]["anomalies_detected"] += 1
        except:
            pass
        
        # Check for SSH key modifications
        if os.path.exists("/home"):
            ssh_dir = Path("/home")
            for user_dir in ssh_dir.iterdir():
                if user_dir.is_dir():
                    authorized_keys = user_dir / ".ssh" / "authorized_keys"
                    if authorized_keys.exists():
                        mtime = datetime.fromtimestamp(authorized_keys.stat().st_mtime)
                        if datetime.now() - mtime < timedelta(days=1):
                            results["anomalies"].append({
                                "type": "recent_ssh_key_change",
                                "severity": "medium",
                                "message": f"SSH keys modified recently for {user_dir.name}",
                                "user": user_dir.name,
                                "modified": mtime.isoformat(),
                            })
                            results["summary"]["anomalies_detected"] += 1
        
        # Check for unusual network connections
        try:
            netstat_result = subprocess.run(
                ["ss", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if netstat_result.returncode == 0:
                # Check for connections to suspicious ports
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
        except:
            pass
    
    except Exception as e:
        log_error(e, context="scan_intrusion_detection")
        raise ScanExecutionError(f"IDS scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score({
            "high_risk": results["summary"]["intrusions_detected"],
            "medium_risk": results["summary"]["anomalies_detected"],
            "low_risk": 0
        })
    
    log_info(f"IDS scan completed: {results['summary']['intrusions_detected']} intrusions, {results['summary']['anomalies_detected']} anomalies")
    return results

