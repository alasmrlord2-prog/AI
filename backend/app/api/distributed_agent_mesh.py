"""
Distributed Agent Mesh API
واجهات API لشبكة agents
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any
from app.api.auth import get_current_user
from app.services.distributed_agent_mesh import get_agent_mesh
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/agents/mesh", tags=["agent-mesh"])


@router.post("/start")
async def start_mesh(current_user: dict = Depends(get_current_user)):
    """بدء شبكة agents"""
    try:
        check_action_permission("agents.mesh", current_user)
    except HTTPException:
        pass
    
    mesh = get_agent_mesh()
    mesh.start()
    
    return {"success": True, "message": "Agent mesh started"}


@router.post("/stop")
async def stop_mesh(current_user: dict = Depends(get_current_user)):
    """إيقاف شبكة agents"""
    try:
        check_action_permission("agents.mesh", current_user)
    except HTTPException:
        pass
    
    mesh = get_agent_mesh()
    mesh.stop()
    
    return {"success": True, "message": "Agent mesh stopped"}


@router.get("/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    """حالة الشبكة"""
    try:
        check_action_permission("agents.mesh", current_user)
    except HTTPException:
        pass
    
    mesh = get_agent_mesh()
    status = mesh.get_mesh_status()
    
    return status


@router.get("/nodes")
async def list_nodes(current_user: dict = Depends(get_current_user)):
    """قائمة nodes"""
    try:
        check_action_permission("agents.mesh", current_user)
    except HTTPException:
        pass
    
    mesh = get_agent_mesh()
    nodes = [node.to_dict() for node in mesh.nodes.values()]
    
    return {"nodes": nodes, "count": len(nodes)}


@router.post("/task")
async def send_task(
    target_node_id: str,
    task: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """إرسال task لـnode"""
    try:
        check_action_permission("agents.mesh", current_user)
    except HTTPException:
        pass
    
    mesh = get_agent_mesh()
    result = mesh.send_task(target_node_id, task)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/node/available")
async def get_available_node(
    capability: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على node متاح بقدرة معينة"""
    try:
        check_action_permission("agents.mesh", current_user)
    except HTTPException:
        pass
    
    mesh = get_agent_mesh()
    node = mesh.get_available_node(capability)
    
    if not node:
        raise HTTPException(status_code=404, detail=f"No available node with capability: {capability}")
    
    return {"node": node.to_dict()}

