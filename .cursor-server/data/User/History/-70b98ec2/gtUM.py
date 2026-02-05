"""
Cost Analyzer API
واجهات API لمحلل التكاليف
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any
from app.api.auth import get_current_user
from app.services.cost_analyzer import get_cost_analyzer
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/cost", tags=["cost"])


@router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user)):
    """الحصول على مقاييس التكلفة الحالية"""
    try:
        check_action_permission("cost.view", current_user)
    except HTTPException:
        pass
    
    analyzer = get_cost_analyzer()
    metrics = analyzer.get_system_metrics()
    
    return metrics


@router.get("/summary")
async def get_summary(
    hours: int = Query(24, description="Number of hours to analyze"),
    current_user: dict = Depends(get_current_user)
):
    """ملخص التكاليف"""
    try:
        check_action_permission("cost.view", current_user)
    except HTTPException:
        pass
    
    analyzer = get_cost_analyzer()
    summary = analyzer.get_cost_summary(hours)
    
    return summary


@router.get("/anomalies")
async def get_anomalies(current_user: dict = Depends(get_current_user)):
    """كشف الشذوذات في التكاليف"""
    try:
        check_action_permission("cost.view", current_user)
    except HTTPException:
        pass
    
    analyzer = get_cost_analyzer()
    anomalies = analyzer.detect_cost_anomalies()
    
    return {"anomalies": anomalies}


@router.get("/recommendations")
async def get_recommendations(current_user: dict = Depends(get_current_user)):
    """الحصول على توصيات لتقليل التكاليف"""
    try:
        check_action_permission("cost.view", current_user)
    except HTTPException:
        pass
    
    analyzer = get_cost_analyzer()
    recommendations = analyzer.get_recommendations()
    
    return {"recommendations": recommendations}


@router.post("/service/analyze")
async def analyze_service(
    service_name: str,
    cpu_usage: float,
    memory_usage_gb: float,
    current_user: dict = Depends(get_current_user)
):
    """تحليل تكلفة خدمة محددة"""
    try:
        check_action_permission("cost.view", current_user)
    except HTTPException:
        pass
    
    analyzer = get_cost_analyzer()
    result = analyzer.analyze_service_cost(service_name, cpu_usage, memory_usage_gb)
    
    return result


@router.post("/pricing/update")
async def update_pricing(
    resource_type: str,
    pricing_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """تحديث الأسعار"""
    try:
        check_action_permission("cost.configure", current_user)
    except HTTPException:
        pass
    
    analyzer = get_cost_analyzer()
    analyzer.update_pricing(resource_type, pricing_data)
    
    return {"success": True, "message": f"Updated pricing for {resource_type}"}

