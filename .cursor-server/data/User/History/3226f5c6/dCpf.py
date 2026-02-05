"""
Penetration Test Scanner - ماسح اختبار الاختراق
"""
import subprocess
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(hours=1))
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
        log_info("Running penetration test")
        
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
        log_error(e, context="scan_penetration_test")
        raise ScanExecutionError(f"Penetration test failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"Penetration test completed: {len(results['findings'])} findings")
    return results

