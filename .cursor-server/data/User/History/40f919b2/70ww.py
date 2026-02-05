"""
Behavior-Based Alerting API
واجهات API للتنبيهات الذكية
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.api.auth import get_current_user
from app.services.behavior_based_alerting import get_behavior_alerter
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/alerts/behavior", tags=["behavior-alerts"])


@router.post("/event")
async def record_event(
    event_type: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """تسجيل حدث"""
    try:
        check_action_permission("alerts.record", current_user)
    except HTTPException:
        pass
    
    alerter = get_behavior_alerter()
    alerter.record_event(event_type, data)
    
    return {"success": True, "message": "Event recorded"}


@router.get("/")
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    hours: Optional[int] = Query(None, description="Filter by hours"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    current_user: dict = Depends(get_current_user)
):
    """الحصول على التنبيهات - allows guest access - optimized for speed"""
    try:
        check_action_permission("alerts.view", current_user)
    except HTTPException:
        pass
    
    try:
        import asyncio
        
        # Use timeout to prevent hanging (max 5 seconds) - OPTIMIZED
        loop = asyncio.get_event_loop()
        alerter = get_behavior_alerter()
        alerts = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: alerter.get_alerts(severity=severity, hours=hours, resolved=resolved)),
            timeout=5.0  # Reduced to 5 seconds for faster response
        )
        return {"alerts": alerts, "count": len(alerts)}
    except asyncio.TimeoutError:
        # Return error on timeout, not empty response
        return {
            "error": "timeout - behavior alerts endpoint not responding",
            "alerts": [],
            "count": None
        }
    except Exception as e:
        # Return actual error, not default response
        return {
            "error": str(e),
            "alerts": [],
            "count": None
        }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """الاعتراف بتنبيه"""
    try:
        check_action_permission("alerts.manage", current_user)
    except HTTPException:
        pass
    
    alerter = get_behavior_alerter()
    result = alerter.acknowledge_alert(alert_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """حل تنبيه"""
    try:
        check_action_permission("alerts.manage", current_user)
    except HTTPException:
        pass
    
    alerter = get_behavior_alerter()
    result = alerter.resolve_alert(alert_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/statistics/summary")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """إحصائيات التنبيهات"""
    try:
        check_action_permission("alerts.view", current_user)
    except HTTPException:
        pass
    
    alerter = get_behavior_alerter()
    stats = alerter.get_statistics()
    
    return stats

