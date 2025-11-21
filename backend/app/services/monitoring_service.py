"""Monitoring Service - Health Checks, Auto Repair, and Alerting."""
import subprocess
import psutil
import docker
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import requests
import json


class MonitoringService:
    """Monitoring service with health checks and auto-repair."""
    
    def __init__(self):
        """Initialize monitoring service."""
        self.docker_client = None
        try:
            self.docker_client = docker.from_env()
        except Exception:
            pass  # Docker not available
    
    def check_service_status(self, service_name: str) -> Dict:
        """Check systemd service status."""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            is_active = result.stdout.strip() == "active"
            
            # Get detailed status
            status_result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "service": service_name,
                "active": is_active,
                "status": "healthy" if is_active else "unhealthy",
                "details": status_result.stdout
            }
        except Exception as e:
            return {
                "service": service_name,
                "active": False,
                "status": "error",
                "error": str(e)
            }
    
    def check_container_status(self, container_name: str) -> Dict:
        """Check Docker container status."""
        if not self.docker_client:
            return {
                "container": container_name,
                "status": "error",
                "error": "Docker client not available"
            }
        
        try:
            container = self.docker_client.containers.get(container_name)
            
            stats = container.stats(stream=False)
            state = container.attrs.get("State", {})
            
            return {
                "container": container_name,
                "status": state.get("Status", "unknown"),
                "running": state.get("Running", False),
                "restart_count": container.attrs.get("RestartCount", 0),
                "health": state.get("Health", {}).get("Status", "unknown"),
                "cpu_usage": self._calculate_cpu_percent(stats),
                "memory_usage": stats.get("memory_stats", {}).get("usage", 0),
                "memory_limit": stats.get("memory_stats", {}).get("limit", 0)
            }
        except docker.errors.NotFound:
            return {
                "container": container_name,
                "status": "not_found",
                "running": False
            }
        except Exception as e:
            return {
                "container": container_name,
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Calculate CPU usage percentage."""
        try:
            cpu_delta = stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)
            system_delta = stats.get("cpu_stats", {}).get("system_cpu_usage", 0)
            
            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
                return round(cpu_percent, 2)
            return 0.0
        except Exception:
            return 0.0
    
    def get_server_metrics(self) -> Dict:
        """Get server metrics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "status": "healthy" if cpu_percent < 90 else "warning" if cpu_percent < 95 else "critical"
                },
                "memory": {
                    "total": memory.total,
                    "used": memory.used,
                    "available": memory.available,
                    "percent": memory.percent,
                    "status": "healthy" if memory.percent < 85 else "warning" if memory.percent < 95 else "critical"
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                    "status": "healthy" if (disk.used / disk.total) * 100 < 85 else "warning" if (disk.used / disk.total) * 100 < 95 else "critical"
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def auto_repair_service(self, service_name: str) -> Dict:
        """Auto repair a failed service."""
        try:
            # Check if service is failed
            status = self.check_service_status(service_name)
            
            if status.get("active"):
                return {
                    "success": True,
                    "message": "Service is already running",
                    "action": "none"
                }
            
            # Try to restart
            result = subprocess.run(
                ["systemctl", "restart", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Wait a bit and check
                import time
                time.sleep(2)
                
                new_status = self.check_service_status(service_name)
                
                return {
                    "success": new_status.get("active", False),
                    "message": "Service restarted" if new_status.get("active") else "Service restart failed",
                    "action": "restart",
                    "status": new_status
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to restart service: {result.stderr}",
                    "action": "restart_failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    def auto_repair_container(self, container_name: str) -> Dict:
        """Auto repair a stopped container."""
        if not self.docker_client:
            return {
                "success": False,
                "error": "Docker client not available"
            }
        
        try:
            container = self.docker_client.containers.get(container_name)
            state = container.attrs.get("State", {})
            
            if state.get("Running", False):
                return {
                    "success": True,
                    "message": "Container is already running",
                    "action": "none"
                }
            
            # Start container
            container.start()
            
            # Wait and check
            import time
            time.sleep(2)
            
            new_state = container.attrs.get("State", {})
            
            return {
                "success": new_state.get("Running", False),
                "message": "Container started" if new_state.get("Running") else "Container start failed",
                "action": "start",
                "status": new_state.get("Status", "unknown")
            }
            
        except docker.errors.NotFound:
            return {
                "success": False,
                "error": "Container not found"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_all_services(self, service_names: List[str]) -> Dict:
        """Check multiple services."""
        results = {}
        
        for service_name in service_names:
            results[service_name] = self.check_service_status(service_name)
        
        return {
            "services": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_all_containers(self) -> Dict:
        """Check all Docker containers."""
        if not self.docker_client:
            return {
                "error": "Docker client not available"
            }
        
        try:
            containers = self.docker_client.containers.list(all=True)
            results = {}
            
            for container in containers:
                results[container.name] = self.check_container_status(container.name)
            
            return {
                "containers": results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e)
            }


# Global instance
monitoring_service = MonitoringService()

