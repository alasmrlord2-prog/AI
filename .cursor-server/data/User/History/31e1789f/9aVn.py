"""
AI Threat Detection API - 100% Local/Offline
واجهات API لكشف التهديدات - محلي بالكامل
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from app.api.auth import get_current_user
from app.services.ai_threat_detection import get_threat_detector
from app.services.security_ai.orchestrator import get_security_ai_orchestrator
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/security/threat-detection", tags=["threat-detection"])


@router.post("/analyze")
async def analyze_logs(
    log_lines: List[str],
    source: str = "logs",
    current_user: dict = Depends(get_current_user)
):
    """
    تحليل logs للكشف عن التهديدات
    
    Args:
        log_lines: قائمة أسطر الـlogs
        source: مصدر الـlogs
    """
    try:
        check_action_permission("security.threat_detection", current_user)
    except HTTPException:
        pass
    
    detector = get_threat_detector()
    result = detector.analyze_realtime(log_lines, source)
    
    return result


@router.get("/summary")
async def get_threat_summary(
    hours: int = 24,
    current_user: dict = Depends(get_current_user)
):
    """ملخص التهديدات"""
    try:
        check_action_permission("security.threat_detection", current_user)
    except HTTPException:
        pass
    
    detector = get_threat_detector()
    summary = detector.get_threat_summary(hours)
    
    return summary


@router.post("/baseline/update")
async def update_baseline(
    metrics: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """تحديث الخط الأساسي للمقاييس"""
    try:
        check_action_permission("security.threat_detection.configure", current_user)
    except HTTPException:
        pass
    
    detector = get_threat_detector()
    detector.update_baseline(metrics)
    
    return {"success": True, "message": "Baseline updated"}


@router.get("/incidents")
async def get_incidents(
    hours: int = 24,
    severity: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على الحوادث الأمنية"""
    try:
        check_action_permission("security.threat_detection", current_user)
    except HTTPException:
        pass
    
    orchestrator = get_security_ai_orchestrator()
    incidents = orchestrator.get_incidents(hours=hours, severity=severity)
    
    return {"incidents": incidents, "count": len(incidents)}


@router.get("/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    """الحصول على حالة النظام الأمني"""
    try:
        check_action_permission("security.threat_detection", current_user)
    except HTTPException:
        pass
    
    orchestrator = get_security_ai_orchestrator()
    status = orchestrator.get_status()
    
    return status


@router.post("/start")
async def start_security_ai(current_user: dict = Depends(get_current_user)):
    """بدء النظام الأمني"""
    try:
        check_action_permission("security.threat_detection.configure", current_user)
    except HTTPException:
        pass
    
    orchestrator = get_security_ai_orchestrator()
    orchestrator.start()
    
    return {"success": True, "message": "Security AI started"}


@router.post("/stop")
async def stop_security_ai(current_user: dict = Depends(get_current_user)):
    """إيقاف النظام الأمني"""
    try:
        check_action_permission("security.threat_detection.configure", current_user)
    except HTTPException:
        pass
    
    orchestrator = get_security_ai_orchestrator()
    orchestrator.stop()
    
    return {"success": True, "message": "Security AI stopped"}

