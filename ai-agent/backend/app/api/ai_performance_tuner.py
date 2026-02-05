"""
AI Performance Tuner API
واجهات API لضبط الأداء
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.services.ai_performance_tuner import get_performance_tuner
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/performance/tuner", tags=["performance-tuner"])


@router.get("/analyze")
async def analyze_performance(current_user: dict = Depends(get_current_user)):
    """تحليل الأداء وإعطاء توصيات"""
    try:
        check_action_permission("performance.analyze", current_user)
    except HTTPException:
        pass
    
    tuner = get_performance_tuner()
    result = tuner.analyze_and_recommend()
    
    return result


@router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """الحصول على المقاييس الحالية"""
    try:
        check_action_permission("performance.view", current_user)
    except HTTPException:
        pass
    
    tuner = get_performance_tuner()
    metrics = tuner.collect_metrics()
    
    return metrics


@router.get("/recommendations/summary")
async def get_recommendations_summary(
    hours: int = Query(24, description="Number of hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """ملخص التوصيات"""
    try:
        check_action_permission("performance.view", current_user)
    except HTTPException:
        pass
    
    tuner = get_performance_tuner()
    summary = tuner.get_recommendations_summary(hours)
    
    return summary

