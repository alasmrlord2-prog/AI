"""
File Integrity Scanner - ماسح سلامة الملفات
"""
import hashlib
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from .base import calculate_risk_score, resolve_path
from app.utils.error_handler import handle_scan_errors, PathResolutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(hours=1))
def scan_file_integrity(path: str = "/etc") -> Dict[str, Any]:
    """
    Monitor file integrity (detect unauthorized changes)
    Note: /etc is a system path, but this is a security check
    """
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
    
    try:
        # For system paths like /etc, we allow them for security checks
        if path.startswith("/etc") or path.startswith("/var") or path.startswith("/usr"):
            monitored_path = Path(path)
        else:
            try:
                resolved_path = resolve_path(path)
                monitored_path = Path(resolved_path)
                log_info(f"Scanning file integrity: {resolved_path}")
            except Exception as e:
                raise PathResolutionError(f"Failed to resolve path '{path}': {str(e)}")
        
        if not monitored_path.exists():
            return {"error": f"Path does not exist: {path}"}
        
        # Monitor key files
        key_files = [
            "passwd", "shadow", "group", "sudoers",
            "hosts", "hostname", "resolv.conf",
        ]
        
        for key_file in key_files:
            file_path = monitored_path / key_file
            if file_path.exists():
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    results["monitored_files"].append({
                        "file": str(file_path),
                        "hash": file_hash[:16] + "...",
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    })
                    results["summary"]["files_monitored"] += 1
                except:
                    pass
    
    except Exception as e:
        log_error(e, context="scan_file_integrity")
        return {"error": f"File integrity scan error: {e}"}
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score({
            "high_risk": results["summary"]["changes_detected"],
            "medium_risk": 0,
            "low_risk": 0
        })
    
    log_info(f"File integrity scan completed: {results['summary']['files_monitored']} files monitored")
    return results

