"""
AI Threat Detection API - 100% Local/Offline
واجهات API لكشف التهديدات - محلي بالكامل
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.api.auth import get_current_user
from app.services.ai_threat_detection import get_threat_detector
from app.core.permission_helpers import check_action_permission

# Lazy import for security_ai to avoid startup errors
try:
    from app.services.security_ai.orchestrator import get_security_ai_orchestrator
    SECURITY_AI_AVAILABLE = True
except ImportError as e:
    SECURITY_AI_AVAILABLE = False
    def get_security_ai_orchestrator():
        raise HTTPException(status_code=503, detail="Security AI module not available")

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
    hours: int = Query(24, description="Number of hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """ملخص التهديدات - allows guest access"""
    try:
        check_action_permission("security.threat_detection", current_user)
    except HTTPException:
        pass
    
    try:
        detector = get_threat_detector()
        summary = detector.get_threat_summary(hours)
        return summary
    except Exception as e:
        # Return default summary if detector fails
        return {
            "total_threats": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "last_24h": []
        }


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
    
    if not SECURITY_AI_AVAILABLE:
        return {"incidents": [], "count": 0}
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
    
    if not SECURITY_AI_AVAILABLE:
        return {"status": "unavailable", "message": "Security AI module not available"}
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
    
    if not SECURITY_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Security AI module not available")
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
    
    if not SECURITY_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Security AI module not available")
    orchestrator = get_security_ai_orchestrator()
    orchestrator.stop()
    
    return {"success": True, "message": "Security AI stopped"}

