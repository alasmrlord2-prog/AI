"""
User Behavior API
واجهات API لمراقبة سلوك المستخدمين
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.api.auth import get_current_user
from app.services.user_behavior_engine import get_user_behavior_engine
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/user-behavior", tags=["user-behavior"])


@router.post("/record")
async def record_action(
    action: str,
    resource: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """تسجيل إجراء مستخدم"""
    try:
        check_action_permission("user_behavior.record", current_user)
    except HTTPException:
        pass
    
    engine = get_user_behavior_engine()
    user_email = current_user.get("email", "unknown")
    
    engine.record_action(
        user=user_email,
        action=action,
        resource=resource,
        metadata={"ip": current_user.get("ip"), "role": current_user.get("role")}
    )
    
    return {"success": True, "message": "Action recorded"}


@router.get("/profile/{user}")
async def get_user_profile(
    user: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على ملف مستخدم"""
    try:
        check_action_permission("user_behavior.view", current_user)
    except HTTPException:
        pass
    
    engine = get_user_behavior_engine()
    profile = engine.get_user_profile(user)
    
    return profile


@router.get("/suspicious")
async def get_suspicious_activities(
    hours: int = Query(24, description="Number of hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """الحصول على الأنشطة المشبوهة"""
    try:
        check_action_permission("user_behavior.view", current_user)
    except HTTPException:
        pass
    
    engine = get_user_behavior_engine()
    activities = engine.get_suspicious_activities(hours)
    
    return {"activities": activities, "count": len(activities)}


@router.get("/safe-mode/{user}")
async def check_safe_mode(
    user: str,
    current_user: dict = Depends(get_current_user)
):
    """التحقق من الحاجة لتفعيل Safe Mode"""
    try:
        check_action_permission("user_behavior.view", current_user)
    except HTTPException:
        pass
    
    engine = get_user_behavior_engine()
    recommendation = engine.suggest_safe_mode(user)
    
    return recommendation

