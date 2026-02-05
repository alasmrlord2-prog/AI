"""
Plugin Store API
واجهات API لمتجر plugins
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from app.api.auth import get_current_user
from app.services.plugin_store import get_plugin_store
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/plugins", tags=["plugin-store"])


@router.get("/")
async def list_plugins(
    plugin_type: Optional[str] = Query(None, description="Filter by type"),
    current_user: dict = Depends(get_current_user)
):
    """قائمة plugins المتاحة"""
    try:
        check_action_permission("plugins.view", current_user)
    except HTTPException:
        pass
    
    store = get_plugin_store()
    plugins = store.list_plugins(plugin_type=plugin_type)
    
    return {"plugins": plugins, "count": len(plugins)}


@router.get("/installed")
async def list_installed(current_user: dict = Depends(get_current_user)):
    """قائمة plugins المثبتة"""
    try:
        check_action_permission("plugins.view", current_user)
    except HTTPException:
        pass
    
    store = get_plugin_store()
    plugins = store.list_installed()
    
    return {"plugins": plugins, "count": len(plugins)}


@router.get("/{plugin_id}")
async def get_plugin_info(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """معلومات plugin"""
    try:
        check_action_permission("plugins.view", current_user)
    except HTTPException:
        pass
    
    store = get_plugin_store()
    info = store.get_plugin_info(plugin_id)
    
    if not info:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return info


@router.post("/{plugin_id}/install")
async def install_plugin(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """تثبيت plugin"""
    try:
        check_action_permission("plugins.install", current_user)
    except HTTPException:
        pass
    
    store = get_plugin_store()
    result = store.install_plugin(plugin_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.delete("/{plugin_id}")
async def uninstall_plugin(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """إلغاء تثبيت plugin"""
    try:
        check_action_permission("plugins.uninstall", current_user)
    except HTTPException:
        pass
    
    store = get_plugin_store()
    result = store.uninstall_plugin(plugin_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/register")
async def register_plugin(
    name: str,
    version: str,
    description: str,
    plugin_type: str,
    author: str,
    current_user: dict = Depends(get_current_user)
):
    """تسجيل plugin جديد"""
    try:
        check_action_permission("plugins.manage", current_user)
    except HTTPException:
        pass
    
    store = get_plugin_store()
    plugin = store.register_plugin(
        name=name,
        version=version,
        description=description,
        plugin_type=plugin_type,
        author=author
    )
    
    return {"success": True, "plugin": plugin.to_dict()}

