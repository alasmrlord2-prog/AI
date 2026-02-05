"""Monitoring API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.services.monitoring_service import monitoring_service
from app.services.alert_manager import alert_manager, AlertLevel
from app.auth import get_current_user

router = APIRouter(prefix="/api/monitor", tags=["monitoring"])


@router.get("/service-status/{service_name}")
async def get_service_status(
    service_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get service status."""
    return monitoring_service.check_service_status(service_name)


@router.get("/container-status/{container_name}")
async def get_container_status(
    container_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get container status."""
    return monitoring_service.check_container_status(container_name)


@router.get("/server-metrics")
async def get_server_metrics(current_user: dict = Depends(get_current_user)):
    """Get server metrics."""
    return monitoring_service.get_server_metrics()


@router.post("/auto-repair/service/{service_name}")
async def auto_repair_service(
    service_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Auto repair a service."""
    result = monitoring_service.auto_repair_service(service_name)
    
    # Send alert
    if result.get("success"):
        alert_manager.send_alert(
            title=f"Service Repaired: {service_name}",
            message=f"Service {service_name} was automatically repaired",
            level=AlertLevel.INFO,
            source="auto_repair"
        )
    else:
        alert_manager.send_alert(
            title=f"Service Repair Failed: {service_name}",
            message=f"Failed to repair service {service_name}: {result.get('message', 'Unknown error')}",
            level=AlertLevel.ERROR,
            source="auto_repair"
        )
    
    return result


@router.post("/auto-repair/container/{container_name}")
async def auto_repair_container(
    container_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Auto repair a container."""
    result = monitoring_service.auto_repair_container(container_name)
    
    # Send alert
    if result.get("success"):
        alert_manager.send_alert(
            title=f"Container Repaired: {container_name}",
            message=f"Container {container_name} was automatically repaired",
            level=AlertLevel.INFO,
            source="auto_repair"
        )
    else:
        alert_manager.send_alert(
            title=f"Container Repair Failed: {container_name}",
            message=f"Failed to repair container {container_name}: {result.get('error', 'Unknown error')}",
            level=AlertLevel.ERROR,
            source="auto_repair"
        )
    
    return result


@router.get("/services")
async def check_all_services(
    services: str,  # Comma-separated list
    current_user: dict = Depends(get_current_user)
):
    """Check multiple services."""
    service_list = [s.strip() for s in services.split(",")]
    return monitoring_service.check_all_services(service_list)


@router.get("/containers")
async def check_all_containers(current_user: dict = Depends(get_current_user)):
    """Check all containers."""
    return monitoring_service.check_all_containers()


# ===== Alert Endpoints =====

@router.get("/alerts")
async def get_alerts(
    level: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard alerts."""
    alert_level = None
    if level:
        try:
            alert_level = AlertLevel(level)
        except ValueError:
            pass
    
    return {
        "alerts": alert_manager.get_dashboard_alerts(
            level=alert_level,
            unread_only=unread_only,
            limit=limit
        )
    }


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark alert as read."""
    result = alert_manager.mark_alert_read(alert_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Alert not found"))
    
    return result


@router.post("/alerts/clear")
async def clear_alerts(
    level: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Clear alerts."""
    alert_level = None
    if level:
        try:
            alert_level = AlertLevel(level)
        except ValueError:
            pass
    
    return alert_manager.clear_alerts(level=alert_level)

