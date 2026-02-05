"""Visualization API endpoints."""
from fastapi import APIRouter, Depends
from typing import List, Dict
import subprocess
import docker
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/visualization", tags=["visualization"])


@router.get("/network-map")
async def get_network_map(current_user: dict = Depends(get_current_user)):
    """Get network map - allows guest access"""
    """Get network map of services."""
    try:
        docker_client = docker.from_env()
        containers = docker_client.containers.list(all=True)
        
        services = []
        links = []
        
        for container in containers:
            # Get container info
            attrs = container.attrs
            ports = attrs.get("NetworkSettings", {}).get("Ports", {})
            
            service_ports = []
            for port, host_ports in ports.items():
                if host_ports:
                    for host_port in host_ports:
                        service_ports.append({
                            "container_port": port,
                            "host_port": host_port.get("HostPort"),
                            "protocol": port.split("/")[1] if "/" in port else "tcp"
                        })
            
            service = {
                "id": container.id[:12],
                "name": container.name,
                "image": attrs.get("Config", {}).get("Image", ""),
                "status": attrs.get("State", {}).get("Status", ""),
                "ports": service_ports
            }
            
            services.append(service)
            
            # Get dependencies
            depends_on = attrs.get("Config", {}).get("HostConfig", {}).get("Links", [])
            for dep in depends_on:
                dep_name = dep.split(":")[0]
                links.append({
                    "source": container.name,
                    "target": dep_name,
                    "type": "depends_on"
                })
        
        return {
            "services": services,
            "links": links
        }
    except Exception as e:
        return {
            "error": str(e),
            "services": [],
            "links": []
        }


@router.get("/architecture")
async def get_architecture(current_user: dict = Depends(get_current_user)):
    """Get architecture - allows guest access"""
    """Get architecture graph."""
    # This would typically read from a JSON file
    # For now, return a sample structure
    
    architecture = {
        "services": [
            {
                "name": "backend",
                "type": "api",
                "depends_on": ["db", "ollama"],
                "ports": [8000]
            },
            {
                "name": "frontend",
                "type": "web",
                "depends_on": ["backend"],
                "ports": [3000]
            },
            {
                "name": "db",
                "type": "database",
                "depends_on": [],
                "ports": [5432]
            },
            {
                "name": "ollama",
                "type": "ai",
                "depends_on": [],
                "ports": [11434]
            }
        ]
    }
    
    return architecture


@router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """Get metrics - allows guest access"""
    """Get metrics for heatmap."""
    try:
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Get error count (placeholder)
        error_count = 0  # Would come from logs/monitoring
        
        return {
            "cpu": {
                "value": cpu_percent,
                "status": "healthy" if cpu_percent < 70 else "warning" if cpu_percent < 90 else "critical"
            },
            "memory": {
                "value": memory.percent,
                "status": "healthy" if memory.percent < 70 else "warning" if memory.percent < 90 else "critical"
            },
            "disk": {
                "value": (disk.used / disk.total) * 100,
                "status": "healthy" if (disk.used / disk.total) * 100 < 70 else "warning" if (disk.used / disk.total) * 100 < 90 else "critical"
            },
            "errors": {
                "value": error_count,
                "status": "healthy" if error_count == 0 else "warning" if error_count < 10 else "critical"
            }
        }
    except Exception as e:
        return {
            "error": str(e)
        }

