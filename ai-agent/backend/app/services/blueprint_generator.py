"""
Blueprint Generator - 100% Local
مولد blueprints تلقائي
"""
import os
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class BlueprintGenerator:
    """
    مولد blueprints تلقائي
    يولد: Docker Compose, Kubernetes manifest, Nginx config, Systemd unit, CI/CD YAML
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.templates_dir = Path("templates/blueprints")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_docker_compose(
        self,
        service_name: str,
        image: str,
        ports: List[int],
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """توليد Docker Compose"""
        compose = {
            "version": "3.8",
            "services": {
                service_name: {
                    "image": image,
                    "ports": [f"{port}:{port}" for port in ports],
                    "restart": "unless-stopped"
                }
            }
        }
        
        if environment:
            compose["services"][service_name]["environment"] = environment
        
        if volumes:
            compose["services"][service_name]["volumes"] = volumes
        
        return {
            "type": "docker-compose",
            "service": service_name,
            "content": yaml.dump(compose, default_flow_style=False),
            "filename": f"docker-compose.{service_name}.yml"
        }
    
    def generate_kubernetes_manifest(
        self,
        service_name: str,
        image: str,
        replicas: int = 1,
        ports: List[int] = None,
        environment: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """توليد Kubernetes manifest"""
        ports = ports or [80]
        
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_name,
                "labels": {
                    "app": service_name
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": service_name,
                            "image": image,
                            "ports": [{"containerPort": port} for port in ports]
                        }]
                    }
                }
            }
        }
        
        if environment:
            manifest["spec"]["template"]["spec"]["containers"][0]["env"] = [
                {"name": k, "value": v} for k, v in environment.items()
            ]
        
        # Service manifest
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{service_name}-service"
            },
            "spec": {
                "selector": {
                    "app": service_name
                },
                "ports": [{"port": port, "targetPort": port} for port in ports],
                "type": "LoadBalancer"
            }
        }
        
        return {
            "type": "kubernetes",
            "service": service_name,
            "deployment": yaml.dump(manifest, default_flow_style=False),
            "service_manifest": yaml.dump(service_manifest, default_flow_style=False),
            "filename": f"{service_name}-k8s.yaml"
        }
    
    def generate_nginx_config(
        self,
        service_name: str,
        upstream_servers: List[str],
        domain: str = "example.com",
        ssl: bool = False
    ) -> Dict[str, Any]:
        """توليد Nginx config"""
        upstream_block = "\n".join([f"    server {server};" for server in upstream_servers])
        
        server_block = f"""
server {{
    listen 80;
    server_name {domain};
    
    location / {{
        proxy_pass http://{service_name}_upstream;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        if ssl:
            server_block += f"""
server {{
    listen 443 ssl;
    server_name {domain};
    
    ssl_certificate /etc/ssl/certs/{domain}.crt;
    ssl_certificate_key /etc/ssl/private/{domain}.key;
    
    location / {{
        proxy_pass http://{service_name}_upstream;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        config = f"upstream {service_name}_upstream {{\n{upstream_block}\n}}\n{server_block}"
        
        return {
            "type": "nginx",
            "service": service_name,
            "content": config,
            "filename": f"{service_name}.nginx.conf"
        }
    
    def generate_systemd_unit(
        self,
        service_name: str,
        command: str,
        working_directory: str = "/opt/app",
        user: str = "app"
    ) -> Dict[str, Any]:
        """توليد systemd unit"""
        unit_content = f"""[Unit]
Description={service_name} Service
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={working_directory}
ExecStart={command}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        return {
            "type": "systemd",
            "service": service_name,
            "content": unit_content,
            "filename": f"{service_name}.service"
        }
    
    def generate_cicd_yaml(
        self,
        service_name: str,
        build_command: str = "docker build -t $IMAGE .",
        deploy_command: str = "kubectl apply -f k8s/"
    ) -> Dict[str, Any]:
        """توليد CI/CD YAML (GitHub Actions مثال)"""
        yaml_content = f"""name: Deploy {service_name}

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build
        run: {build_command}
      
      - name: Deploy
        run: {deploy_command}
"""
        
        return {
            "type": "cicd",
            "service": service_name,
            "content": yaml_content,
            "filename": f".github/workflows/{service_name}.yml"
        }
    
    def generate_all_blueprints(
        self,
        service_name: str,
        image: str,
        ports: List[int],
        **kwargs
    ) -> Dict[str, Any]:
        """توليد جميع blueprints"""
        blueprints = {}
        
        # Docker Compose
        blueprints["docker-compose"] = self.generate_docker_compose(
            service_name=service_name,
            image=image,
            ports=ports,
            environment=kwargs.get("environment"),
            volumes=kwargs.get("volumes")
        )
        
        # Kubernetes
        blueprints["kubernetes"] = self.generate_kubernetes_manifest(
            service_name=service_name,
            image=image,
            replicas=kwargs.get("replicas", 1),
            ports=ports,
            environment=kwargs.get("environment")
        )
        
        # Nginx
        if kwargs.get("nginx"):
            blueprints["nginx"] = self.generate_nginx_config(
                service_name=service_name,
                upstream_servers=kwargs.get("upstream_servers", [f"localhost:{ports[0]}"]) if ports else [],
                domain=kwargs.get("domain", "example.com"),
                ssl=kwargs.get("ssl", False)
            )
        
        # Systemd
        if kwargs.get("systemd"):
            blueprints["systemd"] = self.generate_systemd_unit(
                service_name=service_name,
                command=kwargs.get("command", f"docker run {image}"),
                working_directory=kwargs.get("working_directory", "/opt/app"),
                user=kwargs.get("user", "app")
            )
        
        # CI/CD
        if kwargs.get("cicd"):
            blueprints["cicd"] = self.generate_cicd_yaml(
                service_name=service_name,
                build_command=kwargs.get("build_command"),
                deploy_command=kwargs.get("deploy_command")
            )
        
        return {
            "service": service_name,
            "blueprints": blueprints,
            "generated_at": datetime.now().isoformat()
        }


# Global instance
_blueprint_generator: Optional[BlueprintGenerator] = None


def get_blueprint_generator() -> BlueprintGenerator:
    """الحصول على مثيل مولد blueprints"""
    global _blueprint_generator
    if _blueprint_generator is None:
        _blueprint_generator = BlueprintGenerator()
    return _blueprint_generator

