"""Visualization API endpoints."""
from fastapi import APIRouter, Depends
from typing import List, Dict
import subprocess
import docker
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/visualization", tags=["visualization"])


@router.get("/network-map")
async def get_network_map(current_user: dict = Depends(get_current_user)):
    """Get network map - allows guest access with timeout protection"""
    import asyncio
    
    def get_network_data():
        try:
            docker_client = docker.from_env()
            containers = docker_client.containers.list(all=True)
            
            services = []
            links = []
            
            for container in containers:
                try:
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
                except Exception as e:
                    # Skip problematic containers
                    print(f"Error processing container: {e}")
                    continue
            
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
    
    try:
        # Run with timeout (max 5 seconds)
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, get_network_data),
            timeout=5.0
        )
        return result
    except asyncio.TimeoutError:
        return {
            "error": "timeout",
            "services": [],
            "links": []
        }
    except Exception as e:
        return {
            "error": str(e),
            "services": [],
            "links": []
        }


@router.get("/architecture")
async def get_architecture(current_user: dict = Depends(get_current_user)):
    """Get architecture - allows guest access with real Docker data"""
    import asyncio
    
    def get_architecture_data():
        try:
            docker_client = docker.from_env()
            containers = docker_client.containers.list(all=True)
            
            services = []
            service_names = {}
            
            # Map container names to service info
            for container in containers:
                try:
                    attrs = container.attrs
                    name = container.name
                    image = attrs.get("Config", {}).get("Image", "")
                    status = attrs.get("State", {}).get("Status", "")
                    
                    # Determine service type from image/name
                    service_type = "service"
                    if "postgres" in image.lower() or "postgres" in name.lower():
                        service_type = "database"
                    elif "ollama" in image.lower() or "ollama" in name.lower():
                        service_type = "ai"
                    elif "frontend" in name.lower() or "next" in image.lower():
                        service_type = "web"
                    elif "backend" in name.lower() or "api" in name.lower() or "fastapi" in image.lower():
                        service_type = "api"
                    
                    # Get ports
                    ports = []
                    port_bindings = attrs.get("NetworkSettings", {}).get("Ports", {})
                    for port in port_bindings.keys():
                        if port:
                            port_num = port.split("/")[0]
                            try:
                                ports.append(int(port_num))
                            except:
                                pass
                    
                    # Get dependencies from depends_on
                    depends_on = []
                    host_config = attrs.get("HostConfig", {})
                    if host_config:
                        links = host_config.get("Links", [])
                        for link in links:
                            dep_name = link.split(":")[0] if ":" in link else link
                            depends_on.append(dep_name)
                    
                    service = {
                        "name": name,
                        "type": service_type,
                        "depends_on": depends_on,
                        "ports": ports[:5],  # Limit to first 5 ports
                        "status": status,
                        "image": image
                    }
                    
                    services.append(service)
                    service_names[name] = service
                except Exception as e:
                    print(f"Error processing container for architecture: {e}")
                    continue
            
            # If no containers found, return empty list, not default structure
            if not services:
                return {
                    "services": [],
                    "message": "No containers found"
                }
            
            return {"services": services}
        except Exception as e:
            print(f"Error getting architecture: {e}")
            # Return error, not default structure
            return {
                "error": str(e),
                "services": []
            }
    
    try:
        # Run with timeout (max 5 seconds)
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, get_architecture_data),
            timeout=5.0
        )
        return result
    except asyncio.TimeoutError:
        return {
            "error": "timeout - Docker endpoint not responding",
            "services": []
        }
    except Exception as e:
        return {
            "error": str(e),
            "services": []
        }


@router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """Get metrics - allows guest access with timeout protection"""
    import asyncio
    
    def get_metrics_data():
        try:
            import psutil
            
            # CPU - use interval=0.1 for faster response
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Get error count from logs endpoint
            error_count = None
            try:
                import requests
                from app.core.config import get_settings
                settings = get_settings()
                # Use BACKEND_URL if available, otherwise construct from HOST and PORT
                if hasattr(settings, 'BACKEND_URL') and settings.BACKEND_URL:
                    base_url = settings.BACKEND_URL
                else:
                    base_url = f"http://{settings.HOST}:{settings.PORT}"
                logs_response = requests.get(f"{base_url}/api/logs?limit=1000", timeout=2)
                if logs_response.status_code == 200:
                    logs = logs_response.json()
                    # Count errors in logs
                    error_count = sum(1 for log in logs if isinstance(log, dict) and (
                        log.get("level", "").lower() == "error" or 
                        log.get("severity", "").lower() == "error" or
                        "error" in str(log.get("message", "")).lower()
                    ))
            except:
                pass  # If logs endpoint fails, error_count remains None
            
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
                    "value": error_count if error_count is not None else None,
                    "status": "healthy" if error_count == 0 else "warning" if error_count and error_count < 10 else "critical" if error_count else "unknown"
                }
            }
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return {
                "error": str(e),
                "cpu": {"value": None, "status": "error"},
                "memory": {"value": None, "status": "error"},
                "disk": {"value": None, "status": "error"},
                "errors": {"value": None, "status": "error"}
            }
    
    try:
        # Run with timeout (max 3 seconds)
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, get_metrics_data),
            timeout=3.0
        )
        return result
    except asyncio.TimeoutError:
        return {
            "error": "timeout - metrics endpoint not responding",
            "cpu": {"value": None, "status": "timeout"},
            "memory": {"value": None, "status": "timeout"},
            "disk": {"value": None, "status": "timeout"},
            "errors": {"value": None, "status": "timeout"}
        }
    except Exception as e:
        return {
            "error": str(e),
            "cpu": {"value": None, "status": "error"},
            "memory": {"value": None, "status": "error"},
            "disk": {"value": None, "status": "error"},
            "errors": {"value": None, "status": "error"}
        }

