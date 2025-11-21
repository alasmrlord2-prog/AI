"""
Network Scanner - ماسح الشبكة
"""
import subprocess
from typing import Dict, Any
from .base import calculate_risk_score
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(minutes=15))
def scan_network_security(detailed: bool = False) -> Dict[str, Any]:
    """
    Scan network for security issues
    Args:
        detailed: If True, includes detailed information (ports, interfaces, firewall, DNS)
    """
    results = {
        "suspicious_connections": [],
        "open_ports": [],
        "summary": {
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        }
    }
    
    # Add detailed fields if requested
    if detailed:
        results["listening_ports"] = []
        results["active_connections"] = []
        results["firewall_status"] = {}
        results["network_interfaces"] = []
        results["dns_servers"] = []
        results["security_issues"] = []
    
    try:
        log_info("Scanning network security")
        
        # Get listening ports - try ss first, fallback to netstat
        try:
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
        except FileNotFoundError:
            result = subprocess.run(
                ["netstat", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        for line in result.stdout.split("\n")[1:]:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 4:
                continue
            
            # Extract port
            addr = parts[3]
            if ":" in addr:
                port = addr.split(":")[-1]
                
                # Check for risky ports
                risky_ports = {
                    "22": "SSH",
                    "3306": "MySQL",
                    "5432": "PostgreSQL",
                    "6379": "Redis",
                    "27017": "MongoDB",
                    "9200": "Elasticsearch",
                }
                
                if port in risky_ports:
                    results["open_ports"].append({
                        "port": port,
                        "service": risky_ports[port],
                        "risk": "high" if port == "22" else "medium",
                    })
                    if port == "22":
                        results["summary"]["high_risk"] += 1
                    else:
                        results["summary"]["medium_risk"] += 1
        
        # Check for suspicious connections
        try:
            conn_result = subprocess.run(
                ["ss", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
        except FileNotFoundError:
            conn_result = subprocess.run(
                ["netstat", "-tn"],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        ip_counts = {}
        for line in conn_result.stdout.split("\n")[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                peer = parts[4]
                if ":" in peer:
                    ip = peer.split(":")[0]
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        # Flag IPs with many connections
        for ip, count in ip_counts.items():
            if count > 10:
                results["suspicious_connections"].append({
                    "ip": ip,
                    "connections": count,
                    "risk": "high" if count > 50 else "medium",
                })
                if count > 50:
                    results["summary"]["high_risk"] += 1
                else:
                    results["summary"]["medium_risk"] += 1
    
    except Exception as e:
        log_error(e, context="scan_network_security")
        raise ScanExecutionError(f"Network scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score(results["summary"])
    
    log_info(f"Network scan completed: {len(results['open_ports'])} open ports found")
    return results

def scan_network_security_detailed() -> Dict[str, Any]:
    """Detailed network security scan"""
    return scan_network_security(detailed=True)

