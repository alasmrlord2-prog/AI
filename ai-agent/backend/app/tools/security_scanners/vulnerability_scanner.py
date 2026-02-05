"""
Vulnerability Scanner - ماسح الثغرات
"""
import subprocess
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, resolve_path
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(hours=2))
def scan_vulnerabilities() -> Dict[str, Any]:
    """
    Enhanced vulnerability scan with pip/npm audit support
    """
    results = {
        "vulnerabilities": [],
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
    }
    
    try:
        log_info("Scanning vulnerabilities")
        
        # Try pip-audit first (if installed)
        try:
            pip_audit_result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if pip_audit_result.returncode == 0:
                import json
                audit_data = json.loads(pip_audit_result.stdout)
                for vuln in audit_data.get("vulnerabilities", []):
                    severity = vuln.get("severity", "medium").lower()
                    results["vulnerabilities"].append({
                        "package": vuln.get("name", "unknown"),
                        "version": vuln.get("version", "unknown"),
                        "cve": vuln.get("id", "unknown"),
                        "severity": severity,
                        "description": vuln.get("description", ""),
                    })
                    if severity == "critical":
                        results["summary"]["critical"] += 1
                    elif severity == "high":
                        results["summary"]["high"] += 1
                    elif severity == "medium":
                        results["summary"]["medium"] += 1
                    else:
                        results["summary"]["low"] += 1
        except FileNotFoundError:
            # Fallback: check requirements.txt
            try:
                project_root = resolve_path(".")
                for req_file in Path(project_root).rglob("requirements.txt"):
                    if req_file.exists():
                        with open(req_file, "r") as f:
                            for line in f:
                                if "==" in line:
                                    pkg = line.split("==")[0].strip()
                                    results["vulnerabilities"].append({
                                        "package": pkg,
                                        "severity": "medium",
                                        "message": "Package found (pip-audit not available)",
                                    })
                                    results["summary"]["medium"] += 1
            except:
                pass
        
        # Check Node.js packages (npm audit)
        try:
            project_root = resolve_path(".")
            for pkg_json in Path(project_root).rglob("package.json"):
                if pkg_json.exists():
                    pkg_dir = pkg_json.parent
                    # Try npm audit
                    npm_audit_result = subprocess.run(
                        ["npm", "audit", "--json"],
                        cwd=str(pkg_dir),
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if npm_audit_result.returncode == 0:
                        import json
                        audit_data = json.loads(npm_audit_result.stdout)
                        for vuln_id, vuln_info in audit_data.get("vulnerabilities", {}).items():
                            severity = vuln_info.get("severity", "medium").lower()
                            results["vulnerabilities"].append({
                                "package": vuln_id,
                                "severity": severity,
                                "cve": vuln_info.get("cves", [""])[0] if vuln_info.get("cves") else "",
                                "description": vuln_info.get("title", ""),
                            })
                            if severity == "critical":
                                results["summary"]["critical"] += 1
                            elif severity == "high":
                                results["summary"]["high"] += 1
                            elif severity == "medium":
                                results["summary"]["medium"] += 1
                            else:
                                results["summary"]["low"] += 1
        except:
            pass
        
    except Exception as e:
        log_error(e, context="scan_vulnerabilities")
        raise ScanExecutionError(f"Vulnerability scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"Vulnerability scan completed: {len(results['vulnerabilities'])} vulnerabilities found")
    return results

