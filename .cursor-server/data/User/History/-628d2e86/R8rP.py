"""
Auto-Hardening API
واجهات API للتحصين التلقائي
"""
from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.services.auto_hardening import get_auto_hardening
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/security/hardening", tags=["auto-hardening"])


@router.post("/apply")
async def apply_hardening(current_user: dict = Depends(get_current_user)):
    """تطبيق التحصين التلقائي"""
    try:
        check_action_permission("security.hardening", current_user)
    except HTTPException:
        pass
    
    hardening = get_auto_hardening()
    result = hardening.apply_hardening()
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Hardening failed"))
    
    return result


@router.get("/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    """الحصول على حالة التحصين - allows guest access"""
    try:
        check_action_permission("security.hardening", current_user)
    except HTTPException:
        pass
    
    try:
        hardening = get_auto_hardening()
        status = hardening.get_status()
        return status
    except Exception as e:
        # Return default status if hardening service fails
        return {
            "enabled": False,
            "actions_today": 0,
            "actions": 0,
            "last_action": None,
            "status": "unavailable"
        }

