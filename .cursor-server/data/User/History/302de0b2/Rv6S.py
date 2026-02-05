"""
Capability Detector - Dynamic detection of available tools and features
يكتشف الأدوات المتاحة ديناميكياً قبل تشغيل أي Scanner
"""
from typing import Dict, List, Optional
from app.utils.env_adapter import env_adapter


class CapabilityDetector:
    """
    Detects available tools and capabilities in the environment
    """
    
    def __init__(self):
        """Initialize capability detector"""
        self._capabilities: Optional[Dict[str, bool]] = None
        self._scan_features: Optional[Dict[str, bool]] = None
    
    def detect_all(self) -> Dict[str, bool]:
        """
        Detect all available tools and capabilities
        
        Returns:
            Dictionary mapping tool names to availability
        """
        if self._capabilities is not None:
            return self._capabilities.copy()
        
        self._capabilities = {
            # Network tools
            "ss": env_adapter.tool_installed("ss"),
            "netstat": env_adapter.tool_installed("netstat"),
            "tcpdump": env_adapter.tool_installed("tcpdump"),
            "wireshark": env_adapter.tool_installed("wireshark"),
            "nmap": env_adapter.tool_installed("nmap"),
            "nc": env_adapter.tool_installed("nc"),
            "netcat": env_adapter.tool_installed("netcat"),
            
            # System tools
            "ps": env_adapter.tool_installed("ps"),
            "lsof": env_adapter.tool_installed("lsof"),
            "df": env_adapter.tool_installed("df"),
            "who": env_adapter.tool_installed("who"),
            "w": env_adapter.tool_installed("w"),
            "grep": env_adapter.tool_installed("grep"),
            "find": env_adapter.tool_installed("find"),
            "systemctl": env_adapter.tool_installed("systemctl"),
            "iptables": env_adapter.tool_installed("iptables"),
            "ufw": env_adapter.tool_installed("ufw"),
            
            # Security tools
            "md5sum": env_adapter.tool_installed("md5sum"),
            "sha256sum": env_adapter.tool_installed("sha256sum"),
            "clamav": env_adapter.tool_installed("clamscan"),
            "rkhunter": env_adapter.tool_installed("rkhunter"),
            "chkrootkit": env_adapter.tool_installed("chkrootkit"),
            
            # Container tools
            "docker": env_adapter.tool_installed("docker"),
            "docker_compose": env_adapter.tool_installed("docker-compose") or env_adapter.tool_installed("docker"),
            "podman": env_adapter.tool_installed("podman"),
            "kubectl": env_adapter.tool_installed("kubectl"),
            "helm": env_adapter.tool_installed("helm"),
            
            # DevOps tools
            "git": env_adapter.tool_installed("git"),
            "rsync": env_adapter.tool_installed("rsync"),
            "ssh": env_adapter.tool_installed("ssh"),
            "scp": env_adapter.tool_installed("scp"),
            
            # Cloud tools
            "aws": env_adapter.tool_installed("aws"),
            "gcloud": env_adapter.tool_installed("gcloud"),
            "az": env_adapter.tool_installed("az"),
            "terraform": env_adapter.tool_installed("terraform"),
            
            # Advanced security tools
            "metasploit": env_adapter.tool_installed("msfconsole"),
            "burp": env_adapter.tool_installed("burpsuite"),
            "sqlmap": env_adapter.tool_installed("sqlmap"),
            "nikto": env_adapter.tool_installed("nikto"),
        }
        
        return self._capabilities.copy()
    
    def get_scan_features(self) -> Dict[str, bool]:
        """
        Get available features for scanning
        
        Returns:
            Dictionary mapping feature names to availability
        """
        if self._scan_features is not None:
            return self._scan_features.copy()
        
        caps = self.detect_all()
        
        self._scan_features = {
            # Network scanning
            "network_scan_basic": caps.get("ss") or caps.get("netstat"),
            "network_scan_advanced": caps.get("nmap"),
            "packet_capture": caps.get("tcpdump") or caps.get("wireshark"),
            "port_scan": caps.get("nmap") or caps.get("nc") or caps.get("netcat"),
            
            # System scanning
            "process_scan": caps.get("ps"),
            "file_scan": caps.get("find") and caps.get("grep"),
            "service_scan": caps.get("systemctl"),
            "firewall_scan": caps.get("iptables") or caps.get("ufw"),
            
            # Security scanning
            "integrity_check": caps.get("md5sum") or caps.get("sha256sum"),
            "malware_scan": caps.get("clamav"),
            "rootkit_scan": caps.get("rkhunter") or caps.get("chkrootkit"),
            
            # Container scanning
            "docker_scan": caps.get("docker"),
            "kubernetes_scan": caps.get("kubectl"),
            "container_runtime": caps.get("docker") or caps.get("podman"),
            
            # DevOps
            "git_operations": caps.get("git"),
            "file_sync": caps.get("rsync"),
            "remote_deploy": caps.get("ssh") and caps.get("rsync"),
            
            # Cloud
            "aws_scan": caps.get("aws"),
            "gcp_scan": caps.get("gcloud"),
            "azure_scan": caps.get("az"),
            "infra_as_code": caps.get("terraform"),
            
            # Advanced
            "penetration_test": caps.get("metasploit") or caps.get("nmap"),
            "web_scan": caps.get("burp") or caps.get("nikto"),
            "sql_injection_scan": caps.get("sqlmap"),
        }
        
        return self._scan_features.copy()
    
    def get_available_tools(self, category: Optional[str] = None) -> List[str]:
        """
        Get list of available tools
        
        Args:
            category: Optional category filter (network, system, container, etc.)
            
        Returns:
            List of available tool names
        """
        caps = self.detect_all()
        
        if category:
            category_map = {
                "network": ["ss", "netstat", "tcpdump", "nmap", "nc", "netcat"],
                "system": ["ps", "lsof", "df", "who", "w", "grep", "find", "systemctl"],
                "security": ["md5sum", "sha256sum", "clamav", "rkhunter", "chkrootkit"],
                "container": ["docker", "docker_compose", "podman", "kubectl", "helm"],
                "devops": ["git", "rsync", "ssh", "scp"],
                "cloud": ["aws", "gcloud", "az", "terraform"],
            }
            
            tools = category_map.get(category, [])
            return [tool for tool in tools if caps.get(tool, False)]
        
        return [tool for tool, available in caps.items() if available]
    
    def is_feature_available(self, feature: str) -> bool:
        """
        Check if a specific feature is available
        
        Args:
            feature: Feature name to check
            
        Returns:
            True if feature is available
        """
        features = self.get_scan_features()
        return features.get(feature, False)
    
    def get_recommended_tools(self) -> Dict[str, List[str]]:
        """
        Get recommended tools to install for full functionality
        
        Returns:
            Dictionary mapping categories to missing tools
        """
        caps = self.detect_all()
        features = self.get_scan_features()
        
        recommendations = {
            "network": [],
            "system": [],
            "security": [],
            "container": [],
            "devops": [],
        }
        
        # Network tools
        if not features.get("network_scan_basic"):
            recommendations["network"].append("ss or netstat")
        if not features.get("network_scan_advanced"):
            recommendations["network"].append("nmap")
        if not features.get("packet_capture"):
            recommendations["network"].append("tcpdump")
        
        # System tools
        if not caps.get("ps"):
            recommendations["system"].append("ps")
        if not caps.get("systemctl"):
            recommendations["system"].append("systemctl")
        
        # Security tools
        if not features.get("integrity_check"):
            recommendations["security"].append("md5sum or sha256sum")
        if not features.get("malware_scan"):
            recommendations["security"].append("clamav")
        
        # Container tools
        if not features.get("docker_scan"):
            recommendations["container"].append("docker")
        if not features.get("kubernetes_scan"):
            recommendations["container"].append("kubectl")
        
        # DevOps tools
        if not features.get("git_operations"):
            recommendations["devops"].append("git")
        if not features.get("file_sync"):
            recommendations["devops"].append("rsync")
        
        # Remove empty categories
        return {k: v for k, v in recommendations.items() if v}


# Global instance
capability_detector = CapabilityDetector()

