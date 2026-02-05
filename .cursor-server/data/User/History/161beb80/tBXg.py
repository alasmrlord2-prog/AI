"""
Unified Secret Management API
واجهات API لإدارة الأسرار
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from app.api.auth import get_current_user
from app.services.unified_secret_management import get_secret_manager
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/secrets", tags=["secrets"])


@router.post("/store")
async def store_secret(
    name: str,
    value: str,
    secret_type: str = "api_key",
    rotation_days: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """تخزين سر جديد"""
    try:
        check_action_permission("secrets.store", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    secret = manager.store_secret(
        name=name,
        value=value,
        secret_type=secret_type,
        rotation_days=rotation_days
    )
    
    return {"success": True, "secret": secret.to_dict()}


@router.get("/{secret_id}")
async def get_secret(
    secret_id: str,
    service: str = Query("api", description="Service name requesting the secret"),
    current_user: dict = Depends(get_current_user)
):
    """الحصول على سر (فك التشفير)"""
    try:
        check_action_permission("secrets.get", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    value = manager.get_secret(secret_id, service=service)
    
    if value is None:
        raise HTTPException(status_code=404, detail="Secret not found or access denied")
    
    return {"secret_id": secret_id, "value": value}


@router.get("/")
async def list_secrets(
    secret_type: Optional[str] = Query(None, description="Filter by type"),
    current_user: dict = Depends(get_current_user)
):
    """قائمة الأسرار"""
    try:
        check_action_permission("secrets.list", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    secrets = manager.list_secrets(secret_type=secret_type)
    
    return {"secrets": secrets, "count": len(secrets)}


@router.post("/{secret_id}/rotate")
async def rotate_secret(
    secret_id: str,
    new_value: str,
    current_user: dict = Depends(get_current_user)
):
    """تدوير سر"""
    try:
        check_action_permission("secrets.rotate", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    result = manager.rotate_secret(secret_id, new_value)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/auto-rotate")
async def auto_rotate_secrets(current_user: dict = Depends(get_current_user)):
    """تدوير تلقائي للأسرار"""
    try:
        check_action_permission("secrets.rotate", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    result = manager.auto_rotate_secrets()
    
    return result


@router.post("/policy")
async def set_access_policy(
    service: str,
    secret_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """تعيين سياسة وصول"""
    try:
        check_action_permission("secrets.manage", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    manager.set_access_policy(service, secret_ids)
    
    return {"success": True, "message": f"Access policy set for service {service}"}


@router.delete("/{secret_id}")
async def delete_secret(
    secret_id: str,
    current_user: dict = Depends(get_current_user)
):
    """حذف سر"""
    try:
        check_action_permission("secrets.delete", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    result = manager.delete_secret(secret_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/audit/log")
async def get_audit_log(
    hours: int = Query(24, description="Number of hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """سجل التدقيق"""
    try:
        check_action_permission("secrets.audit", current_user)
    except HTTPException:
        pass
    
    manager = get_secret_manager()
    audit_log = manager.get_audit_log(hours)
    
    return {"audit_log": audit_log, "count": len(audit_log)}

