"""
Snapshot + Rollback API
واجهات API للـsnapshots وrollback
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from app.api.auth import get_current_user
from app.services.snapshot_rollback import get_snapshot_engine
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


@router.post("/create")
async def create_snapshot(
    snapshot_type: str,
    target: str,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """إنشاء snapshot"""
    try:
        check_action_permission("snapshots.create", current_user)
    except HTTPException:
        pass
    
    engine = get_snapshot_engine()
    
    snapshot = engine.create_snapshot(
        snapshot_type=snapshot_type,
        target=target,
        metadata=metadata
    )
    
    return {"success": True, "snapshot": snapshot.to_dict()}


@router.post("/rollback/{snapshot_id}")
async def rollback_snapshot(
    snapshot_id: str,
    force: bool = Query(False, description="Force rollback even if changes exist"),
    current_user: dict = Depends(get_current_user)
):
    """استعادة من snapshot"""
    try:
        check_action_permission("snapshots.rollback", current_user)
    except HTTPException:
        pass
    
    engine = get_snapshot_engine()
    result = engine.rollback(snapshot_id, force=force)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/list")
async def list_snapshots(
    snapshot_type: Optional[str] = Query(None, description="Filter by type"),
    current_user: dict = Depends(get_current_user)
):
    """قائمة الـsnapshots"""
    try:
        check_action_permission("snapshots.view", current_user)
    except HTTPException:
        pass
    
    engine = get_snapshot_engine()
    snapshots = engine.list_snapshots(snapshot_type=snapshot_type)
    
    return {"snapshots": snapshots, "count": len(snapshots)}


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """حذف snapshot"""
    try:
        check_action_permission("snapshots.delete", current_user)
    except HTTPException:
        pass
    
    engine = get_snapshot_engine()
    result = engine.delete_snapshot(snapshot_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

