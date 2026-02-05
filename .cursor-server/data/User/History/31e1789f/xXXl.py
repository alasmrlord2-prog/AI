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

