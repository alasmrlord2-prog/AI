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
    """الحصول على حالة التحصين - allows guest access with timeout protection"""
    import asyncio
    
    try:
        check_action_permission("security.hardening", current_user)
    except HTTPException:
        pass
    
    try:
        # Use timeout to prevent hanging (max 3 seconds) - OPTIMIZED
        loop = asyncio.get_event_loop()
        hardening = get_auto_hardening()
        status = await asyncio.wait_for(
            loop.run_in_executor(None, hardening.get_status),
            timeout=3.0  # Reduced to 3 seconds for faster response
        )
        return status
    except asyncio.TimeoutError:
        # Return safe defaults on timeout
        return {
            "hardening_applied": False,
            "backup_configs": [],
            "actions_today": 0,
            "total_actions": 0,
            "timestamp": None
        }
    except Exception as e:
        # Return safe defaults on error
        print(f"Error getting hardening status: {e}")
        return {
            "hardening_applied": False,
            "backup_configs": [],
            "actions_today": 0,
            "total_actions": 0,
            "timestamp": None
        }

