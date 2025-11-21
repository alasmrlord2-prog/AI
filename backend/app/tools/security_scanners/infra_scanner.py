"""
Infrastructure Scanner - ماسح البنية التحتية
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
@cached(ttl=timedelta(minutes=30))
def scan_infra(path: str = "/app") -> Dict[str, Any]:
    """
    Scan infrastructure files (docker-compose, k8s) for security issues
    """
    try:
        resolved_path = resolve_path(path)
        log_info(f"Scanning infrastructure: {resolved_path}")
    except Exception as e:
        raise PathResolutionError(f"Failed to resolve path '{path}': {str(e)}")
    
    results = {
        "path": resolved_path,
        "issues": [],
        "summary": {
            "containers_as_root": 0,
            "exposed_ports": [],
            "missing_secrets": 0,
            "insecure_configs": 0,
        }
    }
    
    try:
        root = Path(resolved_path)
        if not root.exists():
            return {"error": f"Path does not exist: {resolved_path}. Original path: {path}"}
        
        # Find docker-compose files
        for compose_file in root.rglob("docker-compose*.yml"):
            try:
                with open(compose_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check for root user
                if re.search(r'user:\s*["\']?0["\']?', content, re.IGNORECASE):
                    results["issues"].append({
                        "file": str(compose_file.relative_to(root)),
                        "type": "container_as_root",
                        "severity": "high",
                        "message": "Container running as root user"
                    })
                    results["summary"]["containers_as_root"] += 1
                
                # Check for exposed ports
                port_matches = re.finditer(r'ports:\s*["\']?(\d+):', content)
                for match in port_matches:
                    port = match.group(1)
                    if port not in results["summary"]["exposed_ports"]:
                        results["summary"]["exposed_ports"].append(port)
                
                # Check for hardcoded secrets
                if re.search(r'password["\s:=]+[^\s"\']{6,}', content, re.IGNORECASE):
                    results["issues"].append({
                        "file": str(compose_file.relative_to(root)),
                        "type": "hardcoded_secret",
                        "severity": "high",
                        "message": "Hardcoded password found"
                    })
                    results["summary"]["missing_secrets"] += 1
                
                # Check for insecure configurations
                insecure_patterns = [
                    (r'privileged:\s*true', "privileged_container"),
                    (r'network_mode:\s*["\']?host["\']?', "host_network"),
                ]
                
                for pattern, issue_type in insecure_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        results["issues"].append({
                            "file": str(compose_file.relative_to(root)),
                            "type": issue_type,
                            "severity": "high",
                            "message": f"Insecure configuration: {issue_type}"
                        })
                        results["summary"]["insecure_configs"] += 1
            except Exception as e:
                log_error(e, context=f"scan_infra: {compose_file}")
                continue
        
        # Find Kubernetes files
        for k8s_file in root.rglob("*.yaml"):
            try:
                if "k8s" in str(k8s_file) or "kubernetes" in str(k8s_file):
                    with open(k8s_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Check for security issues
                    if re.search(r'runAsUser:\s*0', content):
                        results["issues"].append({
                            "file": str(k8s_file.relative_to(root)),
                            "type": "k8s_run_as_root",
                            "severity": "high",
                            "message": "Kubernetes pod running as root"
                        })
                        results["summary"]["insecure_configs"] += 1
            except Exception:
                continue
    
    except Exception as e:
        log_error(e, context="scan_infra")
        return {"error": f"Infra scan error: {e}"}
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score({
            "high_risk": results["summary"]["containers_as_root"] + results["summary"]["missing_secrets"] + results["summary"]["insecure_configs"],
            "medium_risk": len(results["summary"]["exposed_ports"]),
            "low_risk": 0
        })
    
    log_info(f"Infrastructure scan completed: {len(results['issues'])} issues found")
    return results

