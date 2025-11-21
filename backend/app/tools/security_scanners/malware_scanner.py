"""
Malware Scanner - ماسح البرمجيات الخبيثة
"""
import hashlib
import os
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, resolve_path
from app.utils.error_handler import handle_scan_errors, PathResolutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
def scan_malware(path: str = "/tmp") -> Dict[str, Any]:
    """
    Scan for malware indicators with enhanced detection
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
        # For /tmp, we allow it for security checks
        if path.startswith("/tmp") or path.startswith("/var/tmp"):
            scan_path = Path(path)
        else:
            try:
                resolved_path = resolve_path(path)
                scan_path = Path(resolved_path)
                log_info(f"Scanning for malware: {resolved_path}")
            except Exception as e:
                raise PathResolutionError(f"Failed to resolve path '{path}': {str(e)}")
        
        if not scan_path.exists():
            return {"error": f"Path does not exist: {path}"}
        
        # Suspicious filename patterns
        suspicious_patterns = [
            ".exe", ".bat", ".scr", ".vbs", ".sh", ".py",
            "miner", "crypto", "backdoor", "trojan", "virus",
        ]
        
        # Malware signatures (placeholder - in production, use real signatures)
        malware_signatures = {
            # Example: "abc123...": "Trojan.Generic"
        }
        
        try:
            for file_path in scan_path.rglob("*"):
                if not file_path.is_file():
                    continue
                
                results["summary"]["files_scanned"] += 1
                
                # Check filename
                file_name = file_path.name.lower()
                if any(pattern in file_name for pattern in suspicious_patterns):
                    # Calculate hash
                    try:
                        with open(file_path, "rb") as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                        
                        # Check against signatures
                        is_malware = file_hash in malware_signatures
                        
                        # Check binary headers (ELF vs PE)
                        try:
                            with open(file_path, "rb") as f:
                                header = f.read(4)
                                is_binary = header.startswith(b'\x7fELF') or header.startswith(b'MZ')
                                if is_binary and not file_name.endswith(('.so', '.dll', '.exe')):
                                    is_malware = True
                        except:
                            pass
                        
                        if is_malware or any(pattern in file_name for pattern in ["miner", "backdoor", "trojan"]):
                            results["suspicious_files"].append({
                                "file": str(file_path),
                                "hash": file_hash[:16] + "...",
                                "reason": "Suspicious filename or signature match",
                                "risk": "high",
                            })
                            results["summary"]["suspicious_found"] += 1
                    except:
                        continue
        except:
            pass
    
    except Exception as e:
        log_error(e, context="scan_malware")
        return {"error": f"Malware scan error: {e}"}
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score({
            "high_risk": results["summary"]["suspicious_found"],
            "medium_risk": 0,
            "low_risk": 0
        })
    
    log_info(f"Malware scan completed: {results['summary']['suspicious_found']} suspicious files found")
    return results

