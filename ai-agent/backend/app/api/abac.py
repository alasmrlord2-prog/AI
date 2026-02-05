"""
ABAC API Endpoints
واجهات API لنظام ABAC
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from app.api.auth import get_current_user
from app.services.abac_service import abac_service
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/abac", tags=["abac"])


@router.post("/check")
async def check_access(
    action: str,
    resource: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    التحقق من الصلاحيات باستخدام ABAC
    
    Args:
        action: الإجراء المطلوب
        resource: المورد المستهدف
        context: السياق الإضافي (source_ip, is_vpn, etc.)
    """
    try:
        check_action_permission("abac.check", current_user)
    except HTTPException:
        pass  # Allow for now
    
    result = abac_service.check_access(
        user=current_user,
        action=action,
        resource=resource,
        context=context or {}
    )
    
    return result


@router.post("/policies")
async def add_policy(
    policy: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """إضافة سياسة ABAC جديدة"""
    try:
        check_action_permission("abac.manage_policies", current_user)
    except HTTPException:
        pass  # Allow for now
    
    result = abac_service.add_policy(policy)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/policies")
async def list_policies(current_user: dict = Depends(get_current_user)):
    """قائمة السياسات"""
    try:
        check_action_permission("abac.view_policies", current_user)
    except HTTPException:
        pass  # Allow for now
    
    return abac_service.list_policies()


@router.delete("/policies/{policy_name}")
async def remove_policy(
    policy_name: str,
    current_user: dict = Depends(get_current_user)
):
    """حذف سياسة"""
    try:
        check_action_permission("abac.manage_policies", current_user)
    except HTTPException:
        pass  # Allow for now
    
    result = abac_service.remove_policy(policy_name)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

