"""
Digital Twin API
واجهات API للـdigital twin
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from app.api.auth import get_current_user
from app.services.digital_twin import get_digital_twin
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/digital-twin", tags=["digital-twin"])


@router.post("/create")
async def create_twin(
    name: str,
    infrastructure_config: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """إنشاء digital twin"""
    try:
        check_action_permission("digital_twin.create", current_user)
    except HTTPException:
        pass
    
    twin_service = get_digital_twin()
    result = twin_service.create_twin(name, infrastructure_config)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/{twin_id}")
async def get_twin(
    twin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على twin"""
    try:
        check_action_permission("digital_twin.view", current_user)
    except HTTPException:
        pass
    
    twin_service = get_digital_twin()
    twin = twin_service.get_twin(twin_id)
    
    if not twin:
        raise HTTPException(status_code=404, detail="Twin not found")
    
    return twin


@router.get("/")
async def list_twins(current_user: dict = Depends(get_current_user)):
    """قائمة twins"""
    try:
        check_action_permission("digital_twin.view", current_user)
    except HTTPException:
        pass
    
    twin_service = get_digital_twin()
    twins = twin_service.list_twins()
    
    return {"twins": twins, "count": len(twins)}


@router.post("/{twin_id}/simulate/deploy")
async def simulate_deploy(
    twin_id: str,
    deploy_config: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """محاكاة deploy على الـtwin"""
    try:
        check_action_permission("digital_twin.simulate", current_user)
    except HTTPException:
        pass
    
    twin_service = get_digital_twin()
    result = twin_service.simulate_deploy(twin_id, deploy_config)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{twin_id}/simulate/failure")
async def simulate_failure(
    twin_id: str,
    failure_type: str,
    target_service: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """محاكاة فشل على الـtwin"""
    try:
        check_action_permission("digital_twin.simulate", current_user)
    except HTTPException:
        pass
    
    twin_service = get_digital_twin()
    result = twin_service.simulate_failure(twin_id, failure_type, target_service)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/{twin_id}/compare")
async def compare_with_production(
    twin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """مقارنة الـtwin مع الإنتاج"""
    try:
        check_action_permission("digital_twin.view", current_user)
    except HTTPException:
        pass
    
    twin_service = get_digital_twin()
    result = twin_service.compare_with_production(twin_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.delete("/{twin_id}")
async def delete_twin(
    twin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """حذف twin"""
    try:
        check_action_permission("digital_twin.delete", current_user)
    except HTTPException:
        pass
    
    twin_service = get_digital_twin()
    result = twin_service.delete_twin(twin_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

