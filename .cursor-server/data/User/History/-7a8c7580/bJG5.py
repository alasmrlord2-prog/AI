"""
SIEM (Security Information and Event Management) Monitoring Tool
"""
import os
import json
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

def get_security_events() -> List[Dict[str, Any]]:
    """Collect security events from various sources"""
    events = []
    
    # Check auth logs
    try:
        auth_logs = Path("/var/log/auth.log")
        if not auth_logs.exists():
            auth_logs = Path("/var/log/secure")
        
        if auth_logs.exists():
            with open(auth_logs, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-500:]  # Last 500 lines for better coverage
                for line in lines:
                    line_lower = line.lower()
                    # Extract timestamp from log line if available
                    timestamp = _extract_timestamp(line) or datetime.now().isoformat()
                    
                    if any(keyword in line_lower for keyword in ["failed", "invalid", "unauthorized", "denied", "authentication failure"]):
                        # Determine severity based on context
                        if "failed" in line_lower and ("password" in line_lower or "authentication" in line_lower):
                            severity = "high"
                        elif "invalid" in line_lower or "unauthorized" in line_lower:
                            severity = "high"
                        elif "denied" in line_lower:
                            severity = "medium"
                        else:
                            severity = "medium"
                        
                        events.append({
                            "timestamp": timestamp,
                            "source": "auth",
                            "type": "authentication_failure",
                            "severity": severity,
                            "message": line.strip()[:300],
                            "ip": _extract_ip(line),
                        })
                    
                    # Check for sudo attempts
                    if "sudo" in line_lower and ("failed" in line_lower or "incorrect" in line_lower):
                        events.append({
                            "timestamp": timestamp,
                            "source": "auth",
                            "type": "sudo_failure",
                            "severity": "high",
                            "message": line.strip()[:300],
                            "ip": _extract_ip(line),
                        })
                    
                    # Check for SSH connection attempts
                    if "ssh" in line_lower and ("accepted" in line_lower or "disconnected" in line_lower):
                        events.append({
                            "timestamp": timestamp,
                            "source": "auth",
                            "type": "ssh_connection",
                            "severity": "low",
                            "message": line.strip()[:300],
                            "ip": _extract_ip(line),
                        })
    except Exception as e:
        # Log error but continue
        pass
    
    # Check system logs for errors
    try:
        syslog = Path("/var/log/syslog")
        if syslog.exists():
            with open(syslog, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-300:]  # Last 300 lines
                for line in lines:
                    line_lower = line.lower()
                    timestamp = _extract_timestamp(line) or datetime.now().isoformat()
                    
                    if any(keyword in line_lower for keyword in ["error", "critical", "alert", "emergency", "fatal"]):
                        severity = "critical" if "critical" in line_lower or "emergency" in line_lower or "fatal" in line_lower else "high"
                        
                        # Categorize system errors
                        error_type = "system_error"
                        if "kernel" in line_lower:
                            error_type = "kernel_error"
                        elif "oom" in line_lower or "out of memory" in line_lower:
                            error_type = "memory_error"
                        elif "disk" in line_lower or "filesystem" in line_lower:
                            error_type = "disk_error"
                        elif "network" in line_lower:
                            error_type = "network_error"
                        
                        events.append({
                            "timestamp": timestamp,
                            "source": "system",
                            "type": error_type,
                            "severity": severity,
                            "message": line.strip()[:300],
                            "ip": _extract_ip(line),
                        })
    except Exception as e:
        pass
    
    # Check application logs
    try:
        app_logs = Path("/app/logs/chat.log")
        if app_logs.exists():
            with open(app_logs, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-50:]
                for line in lines:
                    if "error" in line.lower():
                        try:
                            log_data = json.loads(line.strip())
                            if log_data.get("role") == "error":
                                events.append({
                                    "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
                                    "source": "application",
                                    "type": "application_error",
                                    "severity": "medium",
                                    "message": log_data.get("content", "")[:300],
                                })
                        except:
                            pass
    except:
        pass
    
    # Check for suspicious network activity
    try:
        import subprocess
        ss_result = subprocess.run(
            ["ss", "-tnp"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ss_result.returncode == 0:
            ip_counts = {}
            port_counts = {}
            for line in ss_result.stdout.split("\n")[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        state = parts[0] if len(parts) > 0 else ""
                        peer = parts[4] if len(parts) > 4 else ""
                        if ":" in peer:
                            ip = peer.split(":")[0]
                            port = peer.split(":")[1] if ":" in peer else ""
                            
                            if ip not in ["127.0.0.1", "::1", "0.0.0.0"]:
                                ip_counts[ip] = ip_counts.get(ip, 0) + 1
                                
                                # Track suspicious ports
                                if port:
                                    try:
                                        port_num = int(port)
                                        # Common suspicious ports
                                        suspicious_ports = [4444, 5555, 6666, 1234, 31337, 8080, 8888]
                                        if port_num in suspicious_ports or (port_num > 49152 and state == "ESTAB"):
                                            port_counts[ip] = port_counts.get(ip, []) + [port_num]
                                    except:
                                        pass
            
            # Flag IPs with high connection counts
            for ip, count in ip_counts.items():
                if count > 20:
                    severity = "critical" if count > 50 else "high"
                    events.append({
                        "timestamp": datetime.now().isoformat(),
                        "source": "network",
                        "type": "suspicious_network_activity",
                        "severity": severity,
                        "message": f"High connection count from {ip}: {count} active connections",
                        "ip": ip,
                    })
            
            # Flag suspicious port usage
            for ip, ports in port_counts.items():
                unique_ports = list(set(ports))
                if len(unique_ports) > 0:
                    events.append({
                        "timestamp": datetime.now().isoformat(),
                        "source": "network",
                        "type": "suspicious_port_activity",
                        "severity": "medium",
                        "message": f"Suspicious port activity from {ip}: ports {', '.join(map(str, unique_ports[:5]))}",
                        "ip": ip,
                    })
    except Exception as e:
        pass
    
    # Sort by timestamp (newest first)
    events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return events[:100]  # Return last 100 events

def _extract_ip(text: str) -> str:
    """Extract IP address from text"""
    import re
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    match = re.search(ip_pattern, text)
    return match.group(0) if match else "unknown"

def _extract_timestamp(text: str) -> str:
    """Extract timestamp from log line"""
    import re
    # Try to match common log formats: Jan 1 12:00:00 or 2024-01-01T12:00:00
    timestamp_patterns = [
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',  # ISO format
        r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',  # Standard syslog
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',  # Date time format
    ]
    
    for pattern in timestamp_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                # Try to parse and convert to ISO format
                ts_str = match.group(1)
                # Simple conversion for common formats
                if 'T' in ts_str:
                    return ts_str
                # For syslog format, we'll use current time as fallback
                return datetime.now().isoformat()
            except:
                pass
    
    return None

def get_threat_intelligence() -> Dict[str, Any]:
    """Get threat intelligence data from actual system events"""
    threat_intel = {
        "suspicious_ips": [],
        "known_malware_hashes": [],
        "threat_feed_updates": datetime.now().isoformat(),
        "threat_categories": {
            "malware": 0,
            "phishing": 0,
            "botnet": 0,
            "exploit": 0
        },
        "geolocation": {},
        "reputation_scores": {}
    }
    
    # Get events to analyze
    events = get_security_events()
    
    # Analyze IPs from events
    ip_analysis = {}
    for event in events:
        ip = event.get("ip")
        if ip and ip != "unknown":
            if ip not in ip_analysis:
                ip_analysis[ip] = {
                    "count": 0,
                    "severity": [],
                    "types": [],
                    "first_seen": event.get("timestamp"),
                    "last_seen": event.get("timestamp")
                }
            
            ip_analysis[ip]["count"] += 1
            ip_analysis[ip]["severity"].append(event.get("severity", "low"))
            ip_analysis[ip]["types"].append(event.get("type", "unknown"))
            
            if event.get("timestamp", "") > ip_analysis[ip]["last_seen"]:
                ip_analysis[ip]["last_seen"] = event.get("timestamp")
    
    # Identify suspicious IPs
    for ip, data in ip_analysis.items():
        # High connection count or multiple high severity events
        if data["count"] > 10 or data["severity"].count("high") + data["severity"].count("critical") >= 3:
            threat_intel["suspicious_ips"].append({
                "ip": ip,
                "risk_score": min(100, data["count"] * 5 + data["severity"].count("critical") * 20 + data["severity"].count("high") * 10),
                "event_count": data["count"],
                "severity_breakdown": {
                    "critical": data["severity"].count("critical"),
                    "high": data["severity"].count("high"),
                    "medium": data["severity"].count("medium"),
                    "low": data["severity"].count("low")
                },
                "threat_types": list(set(data["types"])),
                "first_seen": data["first_seen"],
                "last_seen": data["last_seen"]
            })
    
    # Sort by risk score
    threat_intel["suspicious_ips"].sort(key=lambda x: x["risk_score"], reverse=True)
    threat_intel["suspicious_ips"] = threat_intel["suspicious_ips"][:20]  # Top 20
    
    # Count threat categories from events
    for event in events:
        event_type = event.get("type", "").lower()
        message = event.get("message", "").lower()
        
        if "malware" in event_type or "malware" in message or "virus" in message:
            threat_intel["threat_categories"]["malware"] += 1
        if "phishing" in event_type or "phishing" in message:
            threat_intel["threat_categories"]["phishing"] += 1
        if "botnet" in event_type or "botnet" in message or "ddos" in message:
            threat_intel["threat_categories"]["botnet"] += 1
        if "exploit" in event_type or "exploit" in message or "vulnerability" in message:
            threat_intel["threat_categories"]["exploit"] += 1
    
    # Check for known suspicious processes/files
    try:
        suspicious_processes = []
        ps_result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ps_result.returncode == 0:
            suspicious_keywords = {
                "nc ": "exploit",
                "netcat": "exploit",
                "nmap": "exploit",
                "masscan": "exploit",
                "hydra": "exploit",
                "sqlmap": "exploit",
                "metasploit": "exploit",
                "john": "exploit"
            }
            
            for line in ps_result.stdout.split("\n")[1:]:
                if line.strip():
                    for keyword, category in suspicious_keywords.items():
                        if keyword in line.lower():
                            parts = line.split()
                            if len(parts) >= 11:
                                suspicious_processes.append({
                                    "pid": parts[1],
                                    "user": parts[0],
                                    "command": " ".join(parts[10:])[:100],
                                    "category": category
                                })
                            threat_intel["threat_categories"][category] += 1
                            break
    except:
        pass
    
    # Add reputation scores based on activity
    for ip_data in threat_intel["suspicious_ips"]:
        ip = ip_data["ip"]
        risk_score = ip_data["risk_score"]
        
        # Simple reputation scoring (0-100, lower is better)
        if risk_score >= 80:
            threat_intel["reputation_scores"][ip] = 10  # Very bad
        elif risk_score >= 60:
            threat_intel["reputation_scores"][ip] = 30  # Bad
        elif risk_score >= 40:
            threat_intel["reputation_scores"][ip] = 50  # Suspicious
        else:
            threat_intel["reputation_scores"][ip] = 70  # Moderate
    
    return threat_intel

def get_security_metrics() -> Dict[str, Any]:
    """Get security metrics"""
    metrics = {
        "total_events": 0,
        "high_severity": 0,
        "medium_severity": 0,
        "low_severity": 0,
        "critical_severity": 0,
        "failed_logins_24h": 0,
        "blocked_ips": 0,
        "active_threats": 0,
        "events_by_source": {},
        "events_by_type": {},
        "top_ips": [],
        "trend_24h": {
            "events": 0,
            "threats": 0
        }
    }
    
    events = get_security_events()
    metrics["total_events"] = len(events)
    
    # Count by severity
    for event in events:
        severity = event.get("severity", "low")
        if severity == "critical":
            metrics["critical_severity"] += 1
        elif severity == "high":
            metrics["high_severity"] += 1
        elif severity == "medium":
            metrics["medium_severity"] += 1
        else:
            metrics["low_severity"] += 1
        
        # Count by source
        source = event.get("source", "unknown")
        metrics["events_by_source"][source] = metrics["events_by_source"].get(source, 0) + 1
        
        # Count by type
        event_type = event.get("type", "unknown")
        metrics["events_by_type"][event_type] = metrics["events_by_type"].get(event_type, 0) + 1
        
        # Failed logins
        if "failed" in event.get("message", "").lower() or "invalid" in event.get("message", "").lower():
            metrics["failed_logins_24h"] += 1
        
        # Count threats
        if severity in ["high", "critical"]:
            metrics["active_threats"] += 1
    
    # Top IPs
    ip_counts = {}
    for event in events:
        ip = event.get("ip")
        if ip and ip != "unknown":
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    metrics["top_ips"] = sorted(
        [{"ip": ip, "count": count} for ip, count in ip_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]
    
    return metrics

def get_network_statistics() -> Dict[str, Any]:
    """Get network statistics"""
    stats = {
        "total_connections": 0,
        "active_connections": 0,
        "listening_ports": [],
        "bandwidth": {
            "rx_bytes": 0,
            "tx_bytes": 0,
            "rx_mbps": 0,
            "tx_mbps": 0
        },
        "top_connections": []
    }
    
    try:
        import subprocess
        
        # Get connections
        ss_result = subprocess.run(
            ["ss", "-tn"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ss_result.returncode == 0:
            connections = {}
            for line in ss_result.stdout.split("\n")[1:]:
                if line.strip():
                    stats["total_connections"] += 1
                    parts = line.split()
                    if len(parts) >= 4:
                        peer = parts[4] if len(parts) > 4 else ""
                        if ":" in peer:
                            ip = peer.split(":")[0]
                            connections[ip] = connections.get(ip, 0) + 1
            
            stats["active_connections"] = len(connections)
            stats["top_connections"] = sorted(
                [{"ip": ip, "count": count} for ip, count in connections.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:10]
        
        # Get network stats
        try:
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()
                for line in lines[2:]:
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            data = parts[1].strip().split()
                            if len(data) >= 10:
                                rx_bytes = int(data[0])
                                tx_bytes = int(data[8])
                                stats["bandwidth"]["rx_bytes"] += rx_bytes
                                stats["bandwidth"]["tx_bytes"] += tx_bytes
            
            stats["bandwidth"]["rx_mbps"] = (stats["bandwidth"]["rx_bytes"] * 8) / 1024 / 1024
            stats["bandwidth"]["tx_mbps"] = (stats["bandwidth"]["tx_bytes"] * 8) / 1024 / 1024
        except:
            pass
        
    except:
        pass
    
    return stats

def get_system_statistics() -> Dict[str, Any]:
    """Get system statistics"""
    stats = {
        "cpu": {
            "load_avg": {"1min": 0, "5min": 0, "15min": 0},
            "usage_percent": 0
        },
        "memory": {
            "total": 0,
            "used": 0,
            "available": 0,
            "usage_percent": 0
        },
        "disk": {
            "total": 0,
            "used": 0,
            "available": 0,
            "usage_percent": 0
        },
        "processes": {
            "total": 0,
            "running": 0,
            "suspicious": 0
        }
    }
    
    try:
        import subprocess
        
        # CPU load
        try:
            with open("/proc/loadavg", "r") as f:
                load = f.read().split()
                stats["cpu"]["load_avg"] = {
                    "1min": float(load[0]),
                    "5min": float(load[1]),
                    "15min": float(load[2])
                }
        except:
            pass
        
        # Memory
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = {}
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        meminfo[parts[0].rstrip(":")] = int(parts[1])
                
                total = meminfo.get("MemTotal", 0)
                available = meminfo.get("MemAvailable", 0)
                used = total - available
                
                stats["memory"]["total"] = total
                stats["memory"]["used"] = used
                stats["memory"]["available"] = available
                if total > 0:
                    stats["memory"]["usage_percent"] = (used / total) * 100
        except:
            pass
        
        # Processes
        try:
            ps_result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ps_result.returncode == 0:
                lines = ps_result.stdout.split("\n")
                stats["processes"]["total"] = len(lines) - 1
                
                suspicious_keywords = ["nc ", "netcat", "nmap", "masscan", "hydra"]
                for line in lines[1:]:
                    if line.strip():
                        stats["processes"]["running"] += 1
                        if any(keyword in line.lower() for keyword in suspicious_keywords):
                            stats["processes"]["suspicious"] += 1
        except:
            pass
        
    except:
        pass
    
    return stats

def run() -> Dict[str, Any]:
    """Main SIEM monitoring function"""
    events = get_security_events()
    metrics = get_security_metrics()
    threat_intel = get_threat_intelligence()
    network_stats = get_network_statistics()
    system_stats = get_system_statistics()
    
    return {
        "events": events,
        "metrics": metrics,
        "threat_intelligence": threat_intel,
        "network_statistics": network_stats,
        "system_statistics": system_stats,
        "timestamp": datetime.now().isoformat(),
        "dashboard": {
            "status": "operational",
            "last_update": datetime.now().isoformat(),
            "event_rate": len(events),
            "threat_level": "high" if metrics.get("critical_severity", 0) > 0 else "medium" if metrics.get("high_severity", 0) > 5 else "low"
        }
    }
