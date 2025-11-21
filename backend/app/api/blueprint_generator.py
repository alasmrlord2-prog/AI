"""
Blueprint Generator API
واجهات API لمولد blueprints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.api.auth import get_current_user
from app.services.blueprint_generator import get_blueprint_generator
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/blueprints", tags=["blueprints"])


@router.post("/generate")
async def generate_blueprints(
    service_name: str,
    image: str,
    ports: List[int],
    nginx: bool = Query(False, description="Generate Nginx config"),
    systemd: bool = Query(False, description="Generate systemd unit"),
    cicd: bool = Query(False, description="Generate CI/CD YAML"),
    current_user: dict = Depends(get_current_user)
):
    """توليد جميع blueprints"""
    try:
        check_action_permission("blueprints.generate", current_user)
    except HTTPException:
        pass
    
    generator = get_blueprint_generator()
    
    # جمع المعاملات الإضافية
    kwargs = {
        "nginx": nginx,
        "systemd": systemd,
        "cicd": cicd
    }
    
    result = generator.generate_all_blueprints(
        service_name=service_name,
        image=image,
        ports=ports,
        **kwargs
    )
    
    return result


@router.post("/docker-compose")
async def generate_docker_compose(
    service_name: str,
    image: str,
    ports: List[int],
    current_user: dict = Depends(get_current_user)
):
    """توليد Docker Compose"""
    try:
        check_action_permission("blueprints.generate", current_user)
    except HTTPException:
        pass
    
    generator = get_blueprint_generator()
    result = generator.generate_docker_compose(
        service_name=service_name,
        image=image,
        ports=ports
    )
    
    return result


@router.post("/kubernetes")
async def generate_kubernetes(
    service_name: str,
    image: str,
    ports: List[int],
    replicas: int = Query(1, description="Number of replicas"),
    current_user: dict = Depends(get_current_user)
):
    """توليد Kubernetes manifest"""
    try:
        check_action_permission("blueprints.generate", current_user)
    except HTTPException:
        pass
    
    generator = get_blueprint_generator()
    result = generator.generate_kubernetes_manifest(
        service_name=service_name,
        image=image,
        ports=ports,
        replicas=replicas
    )
    
    return result


@router.post("/nginx")
async def generate_nginx(
    service_name: str,
    upstream_servers: List[str],
    domain: str = Query("example.com", description="Domain name"),
    ssl: bool = Query(False, description="Enable SSL"),
    current_user: dict = Depends(get_current_user)
):
    """توليد Nginx config"""
    try:
        check_action_permission("blueprints.generate", current_user)
    except HTTPException:
        pass
    
    generator = get_blueprint_generator()
    result = generator.generate_nginx_config(
        service_name=service_name,
        upstream_servers=upstream_servers,
        domain=domain,
        ssl=ssl
    )
    
    return result

