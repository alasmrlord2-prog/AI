"""Deploy Engine - Docker Compose, Kubernetes, and RSync deployment."""
import os
import json
from typing import Dict, Optional, List
from pathlib import Path
import yaml
from app.utils.env_adapter import env_adapter
from app.utils.capability_detector import capability_detector


class DeployEngine:
    """Deployment engine for various deployment methods."""
    
    def __init__(self):
        """Initialize deploy engine."""
        pass
    
    def deploy_docker_compose(
        self,
        compose_file: str,
        project_name: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> Dict:
        """Deploy using Docker Compose."""
        # Check if Docker Compose is available
        if not capability_detector.is_feature_available("container_runtime"):
            return {
                "success": False,
                "error": "Docker Compose not available. Install 'docker' or 'docker-compose'",
                "capabilities": capability_detector.get_scan_features(),
            }
        
        try:
            compose_path = Path(compose_file)
            
            if not compose_path.exists():
                return {
                    "success": False,
                    "error": f"Docker Compose file not found: {compose_file}"
                }
            
            # Build command - try docker compose first, fallback to docker-compose
            docker_compose_cmd = env_adapter.find_tool("docker", "docker-compose")
            if not docker_compose_cmd:
                return {
                    "success": False,
                    "error": "Docker Compose not found"
                }
            
            # Use docker compose (new) or docker-compose (old)
            if "docker-compose" in docker_compose_cmd:
                cmd = ["docker-compose", "-f", str(compose_path)]
            else:
                cmd = ["docker", "compose", "-f", str(compose_path)]
            
            if project_name:
                cmd.extend(["-p", project_name])
            
            # Pull images - use EnvAdapter
            pull_result = env_adapter.exec(
                cmd + ["pull"],
                timeout=600
            )
            
            if not pull_result.success:
                return {
                    "success": False,
                    "error": f"Failed to pull images: {pull_result.stderr}"
                }
            
            # Start services - use EnvAdapter
            up_cmd = cmd + ["up", "-d"]
            if services:
                up_cmd.extend(services)
            
            up_result = env_adapter.exec(
                up_cmd,
                timeout=600
            )
            
            if not up_result.success:
                return {
                    "success": False,
                    "error": f"Failed to start services: {up_result.stderr}"
                }
            
            return {
                "success": True,
                "message": "Deployment successful",
                "output": up_result.stdout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def deploy_kubernetes(
        self,
        manifest_file: str,
        namespace: str = "default",
        apply: bool = True
    ) -> Dict:
        """Deploy to Kubernetes."""
        try:
            manifest_path = Path(manifest_file)
            
            if not manifest_path.exists():
                return {
                    "success": False,
                    "error": f"Kubernetes manifest not found: {manifest_file}"
                }
            
            # Check if kubectl is available
            if not capability_detector.is_feature_available("kubernetes_scan"):
                return {
                    "success": False,
                    "error": "Kubernetes deployment not available. Install 'kubectl' CLI",
                    "capabilities": capability_detector.get_scan_features(),
                }
            
            if apply:
                # Apply manifest - use EnvAdapter
                result = env_adapter.exec(
                    ["kubectl", "apply", "-f", str(manifest_path), "-n", namespace],
                    timeout=300
                )
                
                if not result.success:
                    return {
                        "success": False,
                        "error": f"Failed to apply manifest: {result.stderr}"
                    }
                
                return {
                    "success": True,
                    "message": "Kubernetes deployment successful",
                    "output": result.stdout
                }
            else:
                # Just validate - use EnvAdapter
                result = env_adapter.exec(
                    ["kubectl", "apply", "--dry-run=client", "-f", str(manifest_path)],
                    timeout=60
                )
                
                return {
                    "success": result.success,
                    "message": "Validation successful" if result.success else "Validation failed",
                    "output": result.stdout if result.success else result.stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def deploy_rsync(
        self,
        source: str,
        destination: str,
        host: Optional[str] = None,
        user: Optional[str] = None,
        exclude: Optional[List[str]] = None,
        delete: bool = False
    ) -> Dict:
        """Deploy using RSync."""
        # Check if rsync is available
        if not capability_detector.is_feature_available("file_sync"):
            return {
                "success": False,
                "error": "RSync deployment not available. Install 'rsync'",
                "capabilities": capability_detector.get_scan_features(),
            }
        
        try:
            # Build rsync command
            cmd = ["rsync", "-avz"]
            
            if delete:
                cmd.append("--delete")
            
            if exclude:
                for pattern in exclude:
                    cmd.extend(["--exclude", pattern])
            
            # Add source
            cmd.append(source.rstrip("/") + "/")
            
            # Add destination
            if host:
                if user:
                    dest = f"{user}@{host}:{destination}"
                else:
                    dest = f"{host}:{destination}"
            else:
                dest = destination
            
            cmd.append(dest)
            
            # Execute rsync - use EnvAdapter
            result = env_adapter.exec(
                cmd,
                timeout=600
            )
            
            if not result.success:
                return {
                    "success": False,
                    "error": f"RSync failed: {result.stderr}"
                }
            
            return {
                "success": True,
                "message": "RSync deployment successful",
                "output": result.stdout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_deployment_status(
        self,
        deployment_type: str,
        identifier: str
    ) -> Dict:
        """Get deployment status."""
        try:
            if deployment_type == "docker-compose":
                # Check docker compose services - use EnvAdapter
                docker_compose_cmd = env_adapter.find_tool("docker", "docker-compose")
                if "docker-compose" in docker_compose_cmd:
                    cmd = ["docker-compose", "-f", identifier, "ps"]
                else:
                    cmd = ["docker", "compose", "-f", identifier, "ps"]
                
                result = env_adapter.exec(cmd, timeout=30)
                
                if not result.success:
                    return {
                        "success": False,
                        "error": result.stderr
                    }
                
                return {
                    "success": True,
                    "status": "running",
                    "output": result.stdout
                }
            
            elif deployment_type == "kubernetes":
                # Check kubernetes deployment - use EnvAdapter
                result = env_adapter.exec(
                    ["kubectl", "get", "deployment", identifier, "-o", "json"],
                    timeout=30
                )
                
                if not result.success:
                    return {
                        "success": False,
                        "error": result.stderr
                    }
                
                data = json.loads(result.stdout)
                status = data.get("status", {})
                
                return {
                    "success": True,
                    "status": "running" if status.get("readyReplicas", 0) > 0 else "pending",
                    "replicas": status.get("replicas", 0),
                    "ready_replicas": status.get("readyReplicas", 0)
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown deployment type: {deployment_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
deploy_engine = DeployEngine()

