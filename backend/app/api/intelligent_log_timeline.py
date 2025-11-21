"""
Intelligent Log Timeline API
واجهات API للـtimeline الذكي
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.api.auth import get_current_user
from app.services.intelligent_log_timeline import get_timeline
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/logs/timeline", tags=["timeline"])


@router.post("/add")
async def add_logs(
    log_lines: List[str],
    source: str = "logs",
    current_user: dict = Depends(get_current_user)
):
    """إضافة logs جديدة للـtimeline"""
    try:
        check_action_permission("logs.read", current_user)
    except HTTPException:
        pass
    
    timeline = get_timeline()
    timeline.add_logs(log_lines, source)
    
    return {"success": True, "message": f"Added {len(log_lines)} log lines"}


@router.get("/view")
async def get_timeline_view(
    hours: int = Query(24, description="Number of hours to look back"),
    level: Optional[str] = Query(None, description="Filter by level (error, warning, etc.)"),
    source: Optional[str] = Query(None, description="Filter by source"),
    current_user: dict = Depends(get_current_user)
):
    """عرض timeline"""
    try:
        check_action_permission("logs.read", current_user)
    except HTTPException:
        pass
    
    timeline = get_timeline()
    start_time = datetime.now() - timedelta(hours=hours)
    
    level_filter = [level] if level else None
    source_filter = [source] if source else None
    
    result = timeline.get_timeline(
        start_time=start_time,
        level_filter=level_filter,
        source_filter=source_filter
    )
    
    return result


@router.get("/root-cause")
async def find_root_cause(
    event_index: int = Query(..., description="Index of the error event"),
    current_user: dict = Depends(get_current_user)
):
    """العثور على السبب الجذري لخطأ"""
    try:
        check_action_permission("logs.read", current_user)
    except HTTPException:
        pass
    
    timeline = get_timeline()
    
    if event_index < 0 or event_index >= len(timeline.events):
        raise HTTPException(status_code=404, detail="Event not found")
    
    error_event = timeline.events[event_index]
    if error_event.level not in ["error", "critical"]:
        raise HTTPException(status_code=400, detail="Event is not an error")
    
    result = timeline.find_root_cause(error_event)
    return result


@router.get("/summary")
async def get_error_summary(
    hours: int = Query(24, description="Number of hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """ملخص الأخطاء"""
    try:
        check_action_permission("logs.read", current_user)
    except HTTPException:
        pass
    
    timeline = get_timeline()
    summary = timeline.get_error_summary(hours)
    
    return summary

