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
        try:
            compose_path = Path(compose_file)
            
            if not compose_path.exists():
                return {
                    "success": False,
                    "error": f"Docker Compose file not found: {compose_file}"
                }
            
            # Build command
            cmd = ["docker", "compose", "-f", str(compose_path)]
            
            if project_name:
                cmd.extend(["-p", project_name])
            
            # Pull images
            pull_result = subprocess.run(
                cmd + ["pull"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if pull_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to pull images: {pull_result.stderr}"
                }
            
            # Start services
            up_cmd = cmd + ["up", "-d"]
            if services:
                up_cmd.extend(services)
            
            up_result = subprocess.run(
                up_cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if up_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to start services: {up_result.stderr}"
                }
            
            return {
                "success": True,
                "message": "Deployment successful",
                "output": up_result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Deployment timed out"
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
            
            if apply:
                # Apply manifest
                result = subprocess.run(
                    ["kubectl", "apply", "-f", str(manifest_path), "-n", namespace],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
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
                # Just validate
                result = subprocess.run(
                    ["kubectl", "apply", "--dry-run=client", "-f", str(manifest_path)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                return {
                    "success": result.returncode == 0,
                    "message": "Validation successful" if result.returncode == 0 else "Validation failed",
                    "output": result.stdout if result.returncode == 0 else result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Kubernetes operation timed out"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "kubectl not found. Please install Kubernetes CLI."
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
            
            # Execute rsync
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"RSync failed: {result.stderr}"
                }
            
            return {
                "success": True,
                "message": "RSync deployment successful",
                "output": result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "RSync operation timed out"
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
                # Check docker compose services
                result = subprocess.run(
                    ["docker", "compose", "-f", identifier, "ps"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
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
                # Check kubernetes deployment
                result = subprocess.run(
                    ["kubectl", "get", "deployment", identifier, "-o", "json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
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

