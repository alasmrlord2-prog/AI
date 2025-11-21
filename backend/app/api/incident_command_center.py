"""
Incident Command Center API
واجهات API لمركز إدارة الحوادث
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from app.api.auth import get_current_user
from app.services.incident_command_center import get_incident_center
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/incidents/command-center", tags=["incident-command-center"])


@router.post("/create")
async def create_incident(
    title: str,
    severity: str,
    incident_type: str,
    description: str,
    current_user: dict = Depends(get_current_user)
):
    """إنشاء حادث جديد"""
    try:
        check_action_permission("incidents.create", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    user_email = current_user.get("email", "unknown")
    
    incident = center.create_incident(
        title=title,
        severity=severity,
        incident_type=incident_type,
        description=description,
        created_by=user_email
    )
    
    return {"success": True, "incident": incident.to_dict()}


@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على حادث"""
    try:
        check_action_permission("incidents.view", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    incident = center.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident.to_dict()


@router.get("/")
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    hours: Optional[int] = Query(None, description="Filter by hours"),
    current_user: dict = Depends(get_current_user)
):
    """قائمة الحوادث"""
    try:
        check_action_permission("incidents.view", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    incidents = center.list_incidents(status=status, severity=severity, hours=hours)
    
    return {"incidents": incidents, "count": len(incidents)}


@router.post("/{incident_id}/status")
async def update_status(
    incident_id: str,
    status: str,
    current_user: dict = Depends(get_current_user)
):
    """تحديث حالة الحادث"""
    try:
        check_action_permission("incidents.update", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    user_email = current_user.get("email", "unknown")
    
    result = center.update_incident_status(incident_id, status, user_email)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{incident_id}/root-cause")
async def set_root_cause(
    incident_id: str,
    root_cause: str,
    current_user: dict = Depends(get_current_user)
):
    """تعيين السبب الجذري"""
    try:
        check_action_permission("incidents.update", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    user_email = current_user.get("email", "unknown")
    
    result = center.set_root_cause(incident_id, root_cause, user_email)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{incident_id}/fix")
async def apply_fix(
    incident_id: str,
    fix: str,
    current_user: dict = Depends(get_current_user)
):
    """تطبيق إصلاح"""
    try:
        check_action_permission("incidents.resolve", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    user_email = current_user.get("email", "unknown")
    
    result = center.apply_fix(incident_id, fix, user_email)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{incident_id}/chat")
async def add_chat_message(
    incident_id: str,
    message: str,
    current_user: dict = Depends(get_current_user)
):
    """إضافة رسالة في chat الفريق"""
    try:
        check_action_permission("incidents.chat", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    user_email = current_user.get("email", "unknown")
    
    result = center.add_chat_message(incident_id, user_email, message)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/statistics/summary")
async def get_statistics(current_user: dict = Depends(get_current_user)):
    """إحصائيات الحوادث"""
    try:
        check_action_permission("incidents.view", current_user)
    except HTTPException:
        pass
    
    center = get_incident_center()
    stats = center.get_statistics()
    
    return stats

