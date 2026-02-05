"""
Docker Scanner - ماسح Docker
"""
import os
import re
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, resolve_path
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from app.utils.env_adapter import env_adapter
from app.utils.capability_detector import capability_detector
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))
def scan_docker_security() -> Dict[str, Any]:
    """
    Scan Docker configuration for security issues
    """
    results = {
        "dockerfiles": [],
        "docker_compose_files": [],
        "containers": [],
        "images": [],
        "security_issues": [],
        "summary": {
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    try:
        log_info("Scanning Docker security")
        
        # Check if Docker is available
        if not capability_detector.is_feature_available("docker_scan"):
            return {
                "error": "Docker scanning not available. Install 'docker' CLI",
                "capabilities": capability_detector.get_scan_features(),
            }
        
        # Find Dockerfiles - use resolve_path for portable paths
        search_paths = []
        for path_str in ["/app", "app", "./app", "."]:
            try:
                resolved = resolve_path(path_str)
                if resolved not in search_paths:
                    search_paths.append(resolved)
            except:
                pass
        
        for system_path in ["/home", "/opt"]:
            if os.path.exists(system_path):
                search_paths.append(system_path)
        
        for base_path in search_paths:
            base = Path(base_path)
            if base.exists():
                for dockerfile in base.rglob("Dockerfile*"):
                    try:
                        with open(dockerfile, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        file_issues = []
                        # Check for root user
                        if re.search(r'USER\s+root|FROM.*root', content, re.IGNORECASE):
                            file_issues.append({
                                "type": "root_user",
                                "severity": "high",
                                "message": "Container running as root user",
                            })
                            results["summary"]["high_risk"] += 1
                        
                        # Check for latest tag
                        if re.search(r'FROM\s+.*:latest', content, re.IGNORECASE):
                            file_issues.append({
                                "type": "latest_tag",
                                "severity": "medium",
                                "message": "Using 'latest' tag",
                            })
                            results["summary"]["medium_risk"] += 1
                        
                        if file_issues:
                            results["dockerfiles"].append({
                                "file": str(dockerfile),
                                "issues": file_issues,
                            })
                    except:
                        continue
        
        # Check running containers - use EnvAdapter
        ps_result = env_adapter.exec(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
            timeout=5
        )
        if ps_result.success:
            for line in ps_result.stdout.split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        results["containers"].append({
                            "name": parts[0],
                            "image": parts[1],
                            "status": parts[2] if len(parts) > 2 else "Unknown",
                        })
                        
                        # Check for privileged mode - use EnvAdapter
                        priv_result = env_adapter.exec(
                            ["docker", "inspect", "--format", "{{.HostConfig.Privileged}}", parts[0]],
                            timeout=5
                        )
                        if priv_result.success and priv_result.stdout.strip().lower() == "true":
                            results["security_issues"].append({
                                "type": "privileged_container",
                                "severity": "high",
                                "message": f"Container {parts[0]} is running in privileged mode",
                            })
                            results["summary"]["high_risk"] += 1
        
    except Exception as e:
        log_error(e, context="scan_docker_security")
        raise ScanExecutionError(f"Docker scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"Docker scan completed: {len(results['security_issues'])} issues found")
    return results

