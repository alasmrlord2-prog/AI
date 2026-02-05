"""
Security Scanners Module - وحدات فحص الأمان
"""
from .base import calculate_risk_score, SECRET_PATTERNS
from .repo_scanner import scan_repo
from .infra_scanner import scan_infra

# Import other scanners (will be created)
try:
    from .network_scanner import scan_network_security, scan_network_security_detailed
except ImportError:
    # Fallback - will be created
    def scan_network_security(*args, **kwargs):
        return {"error": "Network scanner not yet implemented"}
    scan_network_security_detailed = scan_network_security

try:
    from .log_scanner import scan_logs_auth
except ImportError:
    def scan_logs_auth(*args, **kwargs):
        return {"error": "Log scanner not yet implemented"}

try:
    from .system_scanner import scan_system_security
except ImportError:
    def scan_system_security(*args, **kwargs):
        return {"error": "System scanner not yet implemented"}

try:
    from .docker_scanner import scan_docker_security
except ImportError:
    def scan_docker_security(*args, **kwargs):
        return {"error": "Docker scanner not yet implemented"}

try:
    from .vulnerability_scanner import scan_vulnerabilities
except ImportError:
    def scan_vulnerabilities(*args, **kwargs):
        return {"error": "Vulnerability scanner not yet implemented"}

try:
    from .file_integrity_scanner import scan_file_integrity
except ImportError:
    def scan_file_integrity(*args, **kwargs):
        return {"error": "File integrity scanner not yet implemented"}

try:
    from .malware_scanner import scan_malware
except ImportError:
    def scan_malware(*args, **kwargs):
        return {"error": "Malware scanner not yet implemented"}

try:
    from .ids_scanner import scan_intrusion_detection
except ImportError:
    def scan_intrusion_detection(*args, **kwargs):
        return {"error": "IDS scanner not yet implemented"}

try:
    from .port_scanner import scan_port_scan
except ImportError:
    def scan_port_scan(*args, **kwargs):
        return {"error": "Port scanner not yet implemented"}

try:
    from .penetration_scanner import scan_penetration_test
except ImportError:
    def scan_penetration_test(*args, **kwargs):
        return {"error": "Penetration scanner not yet implemented"}

__all__ = [
    "calculate_risk_score",
    "SECRET_PATTERNS",
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
]

