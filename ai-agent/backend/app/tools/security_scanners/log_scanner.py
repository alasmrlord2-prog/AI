"""
Log Scanner - ماسح السجلات
"""
import re
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, resolve_path
from app.utils.error_handler import handle_scan_errors, PathResolutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(minutes=10))
def scan_logs_auth(path: str = "/app/logs", lines: int = 1000) -> Dict[str, Any]:
    """
    Scan logs for authentication issues (brute-force, failed logins)
    """
    try:
        resolved_path = resolve_path(path)
        log_info(f"Scanning logs: {resolved_path}")
    except Exception as e:
        raise PathResolutionError(f"Failed to resolve path '{path}': {str(e)}")
    
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
                                "line": line.strip()[:200],
                                "file": log_file.name,
                            })
            except Exception as e:
                log_error(e, context=f"scan_logs_auth: {log_file}")
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
        log_error(e, context="scan_logs_auth")
        return {"error": f"Log scan error: {e}"}
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score({
            "high_risk": 1 if results["summary"]["brute_force_detected"] else 0,
            "medium_risk": results["summary"]["unique_ips"],
            "low_risk": 0
        })
    
    log_info(f"Log scan completed: {results['summary']['total_failed']} failed logins found")
    return results

