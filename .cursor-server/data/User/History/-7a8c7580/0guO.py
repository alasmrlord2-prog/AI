"""
SIEM (Security Information and Event Management) Monitoring Tool
"""
import os
import json
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

def get_security_events() -> List[Dict[str, Any]]:
    """Collect security events from various sources"""
    events = []
    
    # Check auth logs
    try:
        auth_logs = Path("/var/log/auth.log")
        if not auth_logs.exists():
            auth_logs = Path("/var/log/secure")
        
        if auth_logs.exists():
            with open(auth_logs, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-200:]  # Last 200 lines
                for line in lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ["failed", "invalid", "unauthorized", "denied"]):
                        severity = "high" if "failed" in line_lower and "password" in line_lower else "medium"
                        events.append({
                            "timestamp": datetime.now().isoformat(),
                            "source": "auth",
                            "type": "authentication_failure",
                            "severity": severity,
                            "message": line.strip()[:300],
                            "ip": _extract_ip(line),
                        })
    except:
        pass
    
    # Check system logs for errors
    try:
        syslog = Path("/var/log/syslog")
        if syslog.exists():
            with open(syslog, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-100:]
                for line in lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ["error", "critical", "alert", "emergency"]):
                        severity = "critical" if "critical" in line_lower or "emergency" in line_lower else "high"
                        events.append({
                            "timestamp": datetime.now().isoformat(),
                            "source": "system",
                            "type": "system_error",
                            "severity": severity,
                            "message": line.strip()[:300],
                        })
    except:
        pass
    
    # Check application logs
    try:
        app_logs = Path("/app/logs/chat.log")
        if app_logs.exists():
            with open(app_logs, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-50:]
                for line in lines:
                    if "error" in line.lower():
                        try:
                            log_data = json.loads(line.strip())
                            if log_data.get("role") == "error":
                                events.append({
                                    "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
                                    "source": "application",
                                    "type": "application_error",
                                    "severity": "medium",
                                    "message": log_data.get("content", "")[:300],
                                })
                        except:
                            pass
    except:
        pass
    
    # Check for suspicious network activity
    try:
        import subprocess
        ss_result = subprocess.run(
            ["ss", "-tn"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ss_result.returncode == 0:
            ip_counts = {}
            for line in ss_result.stdout.split("\n")[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        peer = parts[4] if len(parts) > 4 else ""
                        if ":" in peer:
                            ip = peer.split(":")[0]
                            if ip not in ["127.0.0.1", "::1"]:
                                ip_counts[ip] = ip_counts.get(ip, 0) + 1
            
            for ip, count in ip_counts.items():
                if count > 20:
                    events.append({
                        "timestamp": datetime.now().isoformat(),
                        "source": "network",
                        "type": "suspicious_network_activity",
                        "severity": "high",
                        "message": f"High connection count from {ip}: {count} connections",
                        "ip": ip,
                    })
    except:
        pass
    
    # Sort by timestamp (newest first)
    events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return events[:100]  # Return last 100 events

def _extract_ip(text: str) -> str:
    """Extract IP address from text"""
    import re
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    match = re.search(ip_pattern, text)
    return match.group(0) if match else "unknown"

def get_threat_intelligence() -> Dict[str, Any]:
    """Get threat intelligence data"""
    return {
        "suspicious_ips": [],
        "known_malware_hashes": [],
        "threat_feed_updates": datetime.now().isoformat(),
    }

def get_security_metrics() -> Dict[str, Any]:
    """Get security metrics"""
    metrics = {
        "total_events": 0,
        "high_severity": 0,
        "medium_severity": 0,
        "low_severity": 0,
        "failed_logins_24h": 0,
        "blocked_ips": 0,
        "active_threats": 0,
    }
    
    events = get_security_events()
    metrics["total_events"] = len(events)
    
    for event in events:
        if event["severity"] == "high":
            metrics["high_severity"] += 1
        elif event["severity"] == "medium":
            metrics["medium_severity"] += 1
        else:
            metrics["low_severity"] += 1
        
        if "failed" in event["message"].lower() or "invalid" in event["message"].lower():
            metrics["failed_logins_24h"] += 1
    
    return metrics

def run() -> Dict[str, Any]:
    """Main SIEM monitoring function"""
    return {
        "events": get_security_events(),
        "metrics": get_security_metrics(),
        "threat_intelligence": get_threat_intelligence(),
        "timestamp": datetime.now().isoformat(),
    }
