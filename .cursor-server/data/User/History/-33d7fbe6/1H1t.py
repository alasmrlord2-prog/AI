"""
Security Service Layer - طبقة خدمة الأمان
Abstraction layer between API and security scanners
"""
from typing import Dict, Any, Optional
from app.tools.security_scanners import (
    scan_repo, scan_infra, scan_network_security, scan_network_security_detailed,
    scan_logs_auth, scan_system_security, scan_docker_security,
    scan_vulnerabilities, scan_file_integrity, scan_malware,
    scan_intrusion_detection, scan_port_scan, scan_penetration_test
)
from app.tools.siem_monitor import run as siem_monitor
from app.tools.advanced_security_tools import (
    threat_intelligence_scan, network_traffic_analysis,
    advanced_vulnerability_scan, web_vulnerability_scan,
    advanced_container_scan, kubernetes_security_scan,
    aws_security_scan, memory_forensics, disk_forensics,
    password_audit, compliance_check, burp_suite_scan,
    metasploit_scan, advanced_packet_analysis
)
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.tools.siem_monitor import add_scan_event

class SecurityService:
    """
    Security Service - Unified interface for all security operations
    """
    
    @staticmethod
    @handle_scan_errors
    def scan_repository(path: str = "/app", max_files: int = 1000) -> Dict[str, Any]:
        """Scan repository for secrets"""
        log_info(f"SecurityService: Scanning repository at {path}")
        result = scan_repo(path, max_files)
        add_scan_event({
            "type": "repo_scan",
            "path": path,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_infrastructure(path: str = "/app") -> Dict[str, Any]:
        """Scan infrastructure files"""
        log_info(f"SecurityService: Scanning infrastructure at {path}")
        result = scan_infra(path)
        add_scan_event({
            "type": "infra_scan",
            "path": path,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_network(detailed: bool = False) -> Dict[str, Any]:
        """Scan network security"""
        log_info(f"SecurityService: Scanning network (detailed={detailed})")
        if detailed:
            result = scan_network_security_detailed()
        else:
            result = scan_network_security(detailed=False)
        add_scan_event({
            "type": "network_scan",
            "detailed": detailed,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_logs(path: str = "/app/logs", lines: int = 1000) -> Dict[str, Any]:
        """Scan logs for authentication issues"""
        log_info(f"SecurityService: Scanning logs at {path}")
        result = scan_logs_auth(path, lines)
        add_scan_event({
            "type": "log_scan",
            "path": path,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_system() -> Dict[str, Any]:
        """Scan system security"""
        log_info("SecurityService: Scanning system")
        result = scan_system_security()
        add_scan_event({
            "type": "system_scan",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_docker() -> Dict[str, Any]:
        """Scan Docker security"""
        log_info("SecurityService: Scanning Docker")
        result = scan_docker_security()
        add_scan_event({
            "type": "docker_scan",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_vulnerabilities() -> Dict[str, Any]:
        """Scan for vulnerabilities"""
        log_info("SecurityService: Scanning vulnerabilities")
        result = scan_vulnerabilities()
        add_scan_event({
            "type": "vulnerability_scan",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_file_integrity(path: str = "/etc") -> Dict[str, Any]:
        """Scan file integrity"""
        log_info(f"SecurityService: Scanning file integrity at {path}")
        result = scan_file_integrity(path)
        add_scan_event({
            "type": "file_integrity_scan",
            "path": path,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_malware(path: str = "/tmp") -> Dict[str, Any]:
        """Scan for malware"""
        log_info(f"SecurityService: Scanning for malware at {path}")
        result = scan_malware(path)
        add_scan_event({
            "type": "malware_scan",
            "path": path,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_intrusion_detection() -> Dict[str, Any]:
        """Scan for intrusions"""
        log_info("SecurityService: Scanning for intrusions")
        result = scan_intrusion_detection()
        add_scan_event({
            "type": "ids_scan",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_ports(target: str = "localhost") -> Dict[str, Any]:
        """Scan ports"""
        log_info(f"SecurityService: Scanning ports on {target}")
        result = scan_port_scan(target)
        add_scan_event({
            "type": "port_scan",
            "target": target,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    @handle_scan_errors
    def scan_penetration() -> Dict[str, Any]:
        """Run penetration test"""
        log_info("SecurityService: Running penetration test")
        result = scan_penetration_test()
        add_scan_event({
            "type": "penetration_test",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "result": result
        })
        return result
    
    @staticmethod
    def get_siem_data() -> Dict[str, Any]:
        """Get SIEM monitoring data"""
        log_info("SecurityService: Getting SIEM data")
        return siem_monitor()
    
    @staticmethod
    @handle_scan_errors
    def threat_intelligence(ip: str) -> Dict[str, Any]:
        """Threat intelligence scan"""
        log_info(f"SecurityService: Threat intelligence for {ip}")
        return threat_intelligence_scan(ip)
    
    @staticmethod
    @handle_scan_errors
    def network_forensics(file_path: str) -> Dict[str, Any]:
        """Network forensics analysis"""
        log_info(f"SecurityService: Network forensics for {file_path}")
        return advanced_packet_analysis(file_path)
    
    @staticmethod
    @handle_scan_errors
    def advanced_vulnerability_scan() -> Dict[str, Any]:
        """Advanced vulnerability scan"""
        log_info("SecurityService: Advanced vulnerability scan")
        return advanced_vulnerability_scan()
    
    @staticmethod
    @handle_scan_errors
    def web_vulnerability_scan(url: str) -> Dict[str, Any]:
        """Web vulnerability scan"""
        log_info(f"SecurityService: Web vulnerability scan for {url}")
        return web_vulnerability_scan(url)
    
    @staticmethod
    @handle_scan_errors
    def advanced_container_scan() -> Dict[str, Any]:
        """Advanced container scan"""
        log_info("SecurityService: Advanced container scan")
        return advanced_container_scan()
    
    @staticmethod
    @handle_scan_errors
    def kubernetes_scan() -> Dict[str, Any]:
        """Kubernetes security scan"""
        log_info("SecurityService: Kubernetes scan")
        return kubernetes_security_scan()
    
    @staticmethod
    @handle_scan_errors
    def aws_scan() -> Dict[str, Any]:
        """AWS security scan"""
        log_info("SecurityService: AWS scan")
        return aws_security_scan()
    
    @staticmethod
    @handle_scan_errors
    def memory_forensics() -> Dict[str, Any]:
        """Memory forensics"""
        log_info("SecurityService: Memory forensics")
        return memory_forensics()
    
    @staticmethod
    @handle_scan_errors
    def disk_forensics(path: str = "/") -> Dict[str, Any]:
        """Disk forensics"""
        log_info(f"SecurityService: Disk forensics at {path}")
        return disk_forensics(path)
    
    @staticmethod
    @handle_scan_errors
    def password_audit() -> Dict[str, Any]:
        """Password audit"""
        log_info("SecurityService: Password audit")
        return password_audit()
    
    @staticmethod
    @handle_scan_errors
    def compliance_check(standard: str = "CIS") -> Dict[str, Any]:
        """Compliance check"""
        log_info(f"SecurityService: Compliance check ({standard})")
        return compliance_check(standard)
    
    @staticmethod
    @handle_scan_errors
    def burp_scan(url: str) -> Dict[str, Any]:
        """Burp Suite scan"""
        log_info(f"SecurityService: Burp Suite scan for {url}")
        return burp_suite_scan(url)
    
    @staticmethod
    @handle_scan_errors
    def metasploit_scan(target: str, port: Optional[int] = None) -> Dict[str, Any]:
        """Metasploit scan"""
        log_info(f"SecurityService: Metasploit scan for {target}")
        return metasploit_scan(target, port)

# Global service instance
security_service = SecurityService()

