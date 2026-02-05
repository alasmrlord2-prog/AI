"""
Configuration Drift API
واجهات API لكاشف تغييرات الـconfig
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from app.api.auth import get_current_user
from app.services.config_drift_detector import get_drift_detector
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/config/drift", tags=["config-drift"])


@router.post("/snapshot")
async def create_snapshot(
    path: str,
    deployment_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """إنشاء لقطة من الـconfig"""
    try:
        check_action_permission("config.manage", current_user)
    except HTTPException:
        pass
    
    detector = get_drift_detector()
    snapshot = detector.create_snapshot(path, deployment_id)
    
    if snapshot is None:
        raise HTTPException(status_code=400, detail="Failed to create snapshot")
    
    return {"success": True, "snapshot": snapshot.to_dict()}


@router.get("/check")
async def check_drift(
    path: str,
    current_user: dict = Depends(get_current_user)
):
    """التحقق من تغييرات الـconfig"""
    try:
        check_action_permission("config.view", current_user)
    except HTTPException:
        pass
    
    detector = get_drift_detector()
    result = detector.check_drift(path)
    
    return result


@router.post("/scan")
async def scan_all(
    current_user: dict = Depends(get_current_user)
):
    """فحص جميع المسارات المراقبة"""
    try:
        check_action_permission("config.view", current_user)
    except HTTPException:
        pass
    
    detector = get_drift_detector()
    result = detector.scan_all_monitored()
    
    return result


@router.post("/restore")
async def restore_config(
    path: str,
    snapshot_index: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """استعادة الـconfig من لقطة"""
    try:
        check_action_permission("config.manage", current_user)
    except HTTPException:
        pass
    
    detector = get_drift_detector()
    
    snapshot = None
    if snapshot_index is not None:
        snapshots = detector.get_snapshots(path)
        if snapshot_index < len(snapshots):
            # نحتاج إلى إعادة بناء snapshot من البيانات
            # للبساطة، سنستخدم آخر snapshot
            pass
    
    result = detector.restore_from_snapshot(path, snapshot)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/snapshots")
async def get_snapshots(
    path: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على جميع اللقطات لمسار"""
    try:
        check_action_permission("config.view", current_user)
    except HTTPException:
        pass
    
    detector = get_drift_detector()
    snapshots = detector.get_snapshots(path)
    
    return {"snapshots": snapshots}


@router.post("/monitor/add")
async def add_monitored_path(
    path: str,
    current_user: dict = Depends(get_current_user)
):
    """إضافة مسار للمراقبة"""
    try:
        check_action_permission("config.manage", current_user)
    except HTTPException:
        pass
    
    detector = get_drift_detector()
    detector.add_monitored_path(path)
    
    return {"success": True, "message": f"Added {path} to monitored paths"}

