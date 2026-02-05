"""
Port Scanner - ماسح المنافذ
"""
import socket
from typing import Dict, Any
from .base import calculate_risk_score
from app.utils.error_handler import handle_scan_errors, ScanExecutionError
from app.utils.logger import log_info, log_error
from app.utils.cache import cached
from datetime import timedelta

@handle_scan_errors
@cached(ttl=timedelta(minutes=10))
def scan_port_scan(target: str = "localhost") -> Dict[str, Any]:
    """
    Port scanning tool
    """
    results = {
        "open_ports": [],
        "closed_ports": [],
        "filtered_ports": [],
        "summary": {
            "total_scanned": 0,
            "open": 0,
            "closed": 0,
        }
    }
    
    try:
        log_info(f"Scanning ports on {target}")
        
        # Common ports to scan
        common_ports = [22, 23, 25, 53, 80, 443, 3306, 5432, 6379, 8080, 9090]
        
        for port in common_ports:
            results["summary"]["total_scanned"] += 1
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                sock.close()
                
                if result == 0:
                    results["open_ports"].append({
                        "port": port,
                        "service": _get_service_name(port),
                        "status": "open",
                    })
                    results["summary"]["open"] += 1
                else:
                    results["closed_ports"].append(port)
                    results["summary"]["closed"] += 1
            except:
                results["filtered_ports"].append(port)
    
    except Exception as e:
        log_error(e, context="scan_port_scan")
        raise ScanExecutionError(f"Port scan failed: {str(e)}")
    
    # Add risk scoring
    if "summary" in results:
        results["risk_score"] = calculate_risk_score({
            "high_risk": len([p for p in results["open_ports"] if p["port"] in [22, 3306, 5432]]),
            "medium_risk": len([p for p in results["open_ports"] if p["port"] not in [22, 3306, 5432]]),
            "low_risk": 0
        })
    
    log_info(f"Port scan completed: {results['summary']['open']} open ports found")
    return results

def _get_service_name(port: int) -> str:
    """Get service name for port"""
    services = {
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        443: "HTTPS",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        8080: "HTTP-Alt",
        9090: "Prometheus",
    }
    return services.get(port, "Unknown")

