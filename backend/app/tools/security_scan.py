"""
Security Scan Tool - Main Entry Point
This file now acts as a compatibility layer, importing from the modular scanners.
"""
# Import all scanners from the modular structure
from app.tools.security_scanners import (
    scan_repo,
    scan_infra,
    scan_network_security,
    scan_network_security_detailed,
    scan_logs_auth,
    scan_system_security,
    scan_docker_security,
    scan_vulnerabilities,
    scan_file_integrity,
    scan_malware,
    scan_intrusion_detection,
    scan_port_scan,
    scan_penetration_test,
    calculate_risk_score,
    SECRET_PATTERNS,
)

# Main entry point for backward compatibility
def run(action: str = "scan_repo", **kwargs) -> dict:
    """
    Main entry point for security scan tool (backward compatibility)
    """
    if action == "scan_repo":
        path = kwargs.get("path", "/app")
        max_files = kwargs.get("max_files", 1000)
        return scan_repo(path, max_files)
    elif action == "scan_infra":
        path = kwargs.get("path", "/app")
        return scan_infra(path)
    elif action == "scan_logs_auth":
        path = kwargs.get("path", "/app/logs")
        lines = kwargs.get("lines", 1000)
        return scan_logs_auth(path, lines)
    elif action == "scan_system":
        return scan_system_security()
    elif action == "scan_docker":
        return scan_docker_security()
    elif action == "scan_network_detailed":
        return scan_network_security_detailed()
    elif action == "scan_vulnerabilities":
        return scan_vulnerabilities()
    elif action == "scan_file_integrity":
        path = kwargs.get("path", "/etc")
        return scan_file_integrity(path)
    elif action == "scan_malware":
        path = kwargs.get("path", "/tmp")
        return scan_malware(path)
    elif action == "scan_intrusion_detection":
        return scan_intrusion_detection()
    elif action == "scan_port_scan":
        target = kwargs.get("target", "localhost")
        return scan_port_scan(target)
    elif action == "scan_penetration_test":
        return scan_penetration_test()
    else:
        return {"error": f"Unknown action: {action}"}

# Export all functions for backward compatibility
__all__ = [
    "scan_repo",
    "scan_infra",
    "scan_network_security",
    "scan_network_security_detailed",
    "scan_logs_auth",
    "scan_system_security",
    "scan_docker_security",
    "scan_vulnerabilities",
    "scan_file_integrity",
    "scan_malware",
    "scan_intrusion_detection",
    "scan_port_scan",
    "scan_penetration_test",
    "calculate_risk_score",
    "SECRET_PATTERNS",
    "run",
]
