"""
Shadow Deployment API
واجهات API للـshadow deployment
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.api.auth import get_current_user
from app.services.shadow_deployment import get_shadow_deployment
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/deployment/shadow", tags=["shadow-deployment"])


@router.post("/create")
async def create_shadow(
    service_name: str,
    image: str,
    traffic_percentage: float = Query(10.0, description="Traffic percentage for shadow"),
    current_user: dict = Depends(get_current_user)
):
    """إنشاء shadow deployment"""
    try:
        check_action_permission("deployment.shadow", current_user)
    except HTTPException:
        pass
    
    deployment = get_shadow_deployment()
    result = deployment.create_shadow(
        service_name=service_name,
        image=image,
        traffic_percentage=traffic_percentage
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{shadow_id}/route")
async def route_traffic(
    shadow_id: str,
    traffic_percentage: float = Query(..., description="Traffic percentage"),
    current_user: dict = Depends(get_current_user)
):
    """توجيه traffic للـshadow"""
    try:
        check_action_permission("deployment.shadow", current_user)
    except HTTPException:
        pass
    
    deployment = get_shadow_deployment()
    result = deployment.route_traffic(shadow_id, traffic_percentage)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/{shadow_id}/compare")
async def compare_results(
    shadow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """مقارنة نتائج shadow"""
    try:
        check_action_permission("deployment.shadow", current_user)
    except HTTPException:
        pass
    
    deployment = get_shadow_deployment()
    result = deployment.compare_results(shadow_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{shadow_id}/promote")
async def promote_shadow(
    shadow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """ترقية shadow إلى production"""
    try:
        check_action_permission("deployment.promote", current_user)
    except HTTPException:
        pass
    
    deployment = get_shadow_deployment()
    result = deployment.promote_shadow(shadow_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.delete("/{shadow_id}")
async def destroy_shadow(
    shadow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """تدمير shadow deployment"""
    try:
        check_action_permission("deployment.shadow", current_user)
    except HTTPException:
        pass
    
    deployment = get_shadow_deployment()
    result = deployment.destroy_shadow(shadow_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/")
async def list_shadows(current_user: dict = Depends(get_current_user)):
    """قائمة shadow deployments"""
    try:
        check_action_permission("deployment.shadow", current_user)
    except HTTPException:
        pass
    
    deployment = get_shadow_deployment()
    shadows = deployment.list_shadows()
    
    return {"shadows": shadows, "count": len(shadows)}

