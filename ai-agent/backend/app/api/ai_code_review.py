"""
AI Code Review + Auto-Fix API
واجهات API لمراجعة وإصلاح الكود
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.services.ai_code_review import get_code_reviewer
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/code/review", tags=["code-review"])


@router.post("/review")
async def review_file(
    file_path: str,
    current_user: dict = Depends(get_current_user)
):
    """مراجعة ملف"""
    try:
        check_action_permission("code.review", current_user)
    except HTTPException:
        pass
    
    reviewer = get_code_reviewer()
    result = reviewer.review_file(file_path)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/auto-fix")
async def auto_fix_file(
    file_path: str,
    apply: bool = Query(False, description="Apply fixes automatically"),
    current_user: dict = Depends(get_current_user)
):
    """إصلاح تلقائي للملف"""
    try:
        check_action_permission("code.auto_fix", current_user)
    except HTTPException:
        pass
    
    reviewer = get_code_reviewer()
    result = reviewer.auto_fix_file(file_path, apply_fixes=apply)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

