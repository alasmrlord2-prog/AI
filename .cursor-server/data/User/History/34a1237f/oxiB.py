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
        
        # Check running containers
        try:
            ps_result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ps_result.returncode == 0:
                for line in ps_result.stdout.split("\n"):
                    if line.strip():
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            results["containers"].append({
                                "name": parts[0],
                                "image": parts[1],
                                "status": parts[2] if len(parts) > 2 else "Unknown",
                            })
                            
                            # Check for privileged mode
                            try:
                                priv_result = subprocess.run(
                                    ["docker", "inspect", "--format", "{{.HostConfig.Privileged}}", parts[0]],
                                    capture_output=True,
                                    text=True,
                                    timeout=5
                                )
                                if priv_result.returncode == 0 and priv_result.stdout.strip().lower() == "true":
                                    results["security_issues"].append({
                                        "type": "privileged_container",
                                        "severity": "high",
                                        "message": f"Container {parts[0]} is running in privileged mode",
                                    })
                                    results["summary"]["high_risk"] += 1
                            except:
                                continue
        except:
            pass
        
    except Exception as e:
        log_error(e, context="scan_docker_security")
        raise ScanExecutionError(f"Docker scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"Docker scan completed: {len(results['security_issues'])} issues found")
    return results

