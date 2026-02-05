import os
import subprocess
import re
from typing import Dict, List, Any

def get_network_interfaces() -> List[str]:
    """Get list of network interfaces"""
    try:
        result = subprocess.run(
            ["ip", "link", "show"],
            capture_output=True,
            text=True,
            timeout=5
        )
        interfaces = []
        for line in result.stdout.split("\n"):
            if ": " in line and "lo:" not in line:
                parts = line.split(": ")
                if len(parts) > 1:
                    iface = parts[1].split("@")[0].strip()
                    if iface and iface not in interfaces:
                        interfaces.append(iface)
        return interfaces
    except Exception:
        return ["eth0", "ens3", "enp0s3"]  # Common defaults

def get_network_stats() -> Dict[str, Any]:
    """Get network statistics from /proc/net/dev"""
    stats = {
        "interfaces": {},
        "total": {
            "rx_bytes": 0,
            "tx_bytes": 0,
            "rx_packets": 0,
            "tx_packets": 0,
            "rx_errors": 0,
            "tx_errors": 0,
        }
    }
    
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()
        
        for line in lines[2:]:  # Skip header lines
            parts = line.split()
            if len(parts) < 10:
                continue
            
            iface = parts[0].replace(":", "")
            if iface == "lo":  # Skip loopback
                continue
            
            rx_bytes = int(parts[1])
            rx_packets = int(parts[2])
            rx_errors = int(parts[3])
            tx_bytes = int(parts[9])
            tx_packets = int(parts[10])
            tx_errors = int(parts[11])
            
            stats["interfaces"][iface] = {
                "rx_bytes": rx_bytes,
                "tx_bytes": tx_bytes,
                "rx_packets": rx_packets,
                "tx_packets": tx_packets,
                "rx_errors": rx_errors,
                "tx_errors": tx_errors,
                "rx_mbps": (rx_bytes * 8) / 1024 / 1024,  # Convert to Mbps
                "tx_mbps": (tx_bytes * 8) / 1024 / 1024,
            }
            
            stats["total"]["rx_bytes"] += rx_bytes
            stats["total"]["tx_bytes"] += tx_bytes
            stats["total"]["rx_packets"] += rx_packets
            stats["total"]["tx_packets"] += tx_packets
            stats["total"]["rx_errors"] += rx_errors
            stats["total"]["tx_errors"] += tx_errors
        
        # Convert total to Mbps
        stats["total"]["rx_mbps"] = (stats["total"]["rx_bytes"] * 8) / 1024 / 1024
        stats["total"]["tx_mbps"] = (stats["total"]["tx_bytes"] * 8) / 1024 / 1024
        
    except Exception as e:
        return {"error": f"Failed to read network stats: {e}"}
    
    return stats

def get_active_connections() -> Dict[str, Any]:
    """Get active network connections"""
    try:
        result = subprocess.run(
            ["ss", "-tun"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        connections = {
            "tcp": {"established": 0, "listening": 0, "time_wait": 0},
            "udp": {"listening": 0},
            "total": 0,
        }
        
        for line in result.stdout.split("\n")[1:]:  # Skip header
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 1:
                continue
            
            state = parts[0].lower()
            if "tcp" in state:
                if "estab" in state:
                    connections["tcp"]["established"] += 1
                elif "listen" in state:
                    connections["tcp"]["listening"] += 1
                elif "time-wait" in state:
                    connections["tcp"]["time_wait"] += 1
            elif "udp" in state:
                if "unconn" in state or "estab" in state:
                    connections["udp"]["listening"] += 1
            
            connections["total"] += 1
        
        return connections
    except Exception as e:
        return {"error": f"Failed to get connections: {e}"}

def detect_suspicious_traffic(stats: Dict, connections: Dict) -> List[Dict[str, Any]]:
    """Detect suspicious network activity"""
    alerts = []
    
    # Check for high error rates
    if stats.get("total", {}).get("rx_errors", 0) > 1000:
        alerts.append({
            "type": "high_rx_errors",
            "severity": "medium",
            "message": f"High RX errors: {stats['total']['rx_errors']}",
        })
    
    if stats.get("total", {}).get("tx_errors", 0) > 1000:
        alerts.append({
            "type": "high_tx_errors",
            "severity": "medium",
            "message": f"High TX errors: {stats['total']['tx_errors']}",
        })
    
    # Check for unusually high connection count
    if connections.get("total", 0) > 1000:
        alerts.append({
            "type": "high_connections",
            "severity": "high",
            "message": f"Unusually high connection count: {connections['total']}",
        })
    
    # Check for high traffic on any interface
    for iface, data in stats.get("interfaces", {}).items():
        if data.get("rx_mbps", 0) > 1000:  # > 1 Gbps
            alerts.append({
                "type": "high_traffic",
                "severity": "medium",
                "message": f"High traffic on {iface}: {data['rx_mbps']:.2f} Mbps RX",
                "interface": iface,
            })
    
    return alerts

def run() -> Dict[str, Any]:
    """Main entry point for network monitoring"""
    stats = get_network_stats()
    connections = get_active_connections()
    alerts = detect_suspicious_traffic(stats, connections)
    
    return {
        "stats": stats,
        "connections": connections,
        "alerts": alerts,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

