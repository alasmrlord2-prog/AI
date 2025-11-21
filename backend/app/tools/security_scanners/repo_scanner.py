"""
Repository Scanner - ماسح المستودع
"""
import os
import re
from typing import Dict, Any
from pathlib import Path
from .base import calculate_risk_score, SECRET_PATTERNS, resolve_path
from app.utils.error_handler import handle_scan_errors, PathResolutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(minutes=30))  # Cache for 30 minutes
def scan_repo(path: str = "/app", max_files: int = 1000) -> Dict[str, Any]:
    """
    Scan repository for secrets and security issues
    """
    try:
        # Resolve path
        resolved_path = resolve_path(path)
        log_info(f"Scanning repository: {resolved_path}")
    except Exception as e:
        raise PathResolutionError(f"Failed to resolve path '{path}': {str(e)}")
    
    results = {
        "path": resolved_path,
        "secrets_found": [],
        "risky_files": [],
        "summary": {
            "total_files": 0,
            "scanned_files": 0,
            "secrets_count": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    # Smart exclude patterns - optimized for large projects
    excluded = [
        ".git", "__pycache__", "node_modules", ".next",
        "venv", "env", ".env", ".pyc", ".log",
        "migrations", "tests", "test_", "spec",
        "coverage", "dist", "build", "target",
        ".pytest_cache", ".mypy_cache"
    ]
    
    try:
        root = Path(resolved_path)
        if not root.exists():
            return {"error": f"Path does not exist: {resolved_path}. Original path: {path}"}
        
        file_count = 0
        for file_path in root.rglob("*"):
            if file_count >= max_files:
                break
            
            # Skip excluded patterns (smart matching)
            file_str = str(file_path)
            if any(exc in file_str for exc in excluded):
                continue
            # Additional checks for specific patterns
            if "/migrations/" in file_str or "/tests/" in file_str or "/test/" in file_str:
                continue
            
            if not file_path.is_file():
                continue
            
            file_count += 1
            results["summary"]["total_files"] = file_count
            
            # Skip large files
            try:
                if file_path.stat().st_size > 100000:  # 100KB
                    continue
            except:
                continue
            
            # Read file
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                continue
            
            results["summary"]["scanned_files"] += 1
            
            # Scan for secrets
            file_secrets = []
            for secret_type, patterns in SECRET_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count("\n") + 1
                        secret_value = match.group(1) if match.groups() else match.group(0)
                        
                        # Don't show full secret
                        if len(secret_value) > 20:
                            secret_preview = secret_value[:10] + "..." + secret_value[-5:]
                        else:
                            secret_preview = "***"
                        
                        file_secrets.append({
                            "type": secret_type,
                            "line": line_num,
                            "preview": secret_preview,
                            "pattern": pattern,
                        })
            
            if file_secrets:
                results["secrets_found"].append({
                    "file": str(file_path.relative_to(root)),
                    "secrets": file_secrets,
                    "count": len(file_secrets),
                })
                results["summary"]["secrets_count"] += len(file_secrets)
                
                # Risk assessment
                high_risk_types = ["private_key", "aws_key", "password"]
                if any(s["type"] in high_risk_types for s in file_secrets):
                    results["summary"]["high_risk"] += 1
                    results["risky_files"].append({
                        "file": str(file_path.relative_to(root)),
                        "risk": "high",
                        "reason": "Contains high-risk secrets"
                    })
                elif len(file_secrets) > 3:
                    results["summary"]["medium_risk"] += 1
                    results["risky_files"].append({
                        "file": str(file_path.relative_to(root)),
                        "risk": "medium",
                        "reason": "Multiple secrets found"
                    })
                else:
                    results["summary"]["low_risk"] += 1
    
    except Exception as e:
        log_error(e, context="scan_repo")
        return {"error": f"Scan error: {e}"}
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"Repository scan completed: {results['summary']['secrets_count']} secrets found")
    return results

