"""
AI Workflow Builder API
واجهات API لباني workflows
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from app.api.auth import get_current_user
from app.services.ai_workflow_builder import get_workflow_builder
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/workflows/builder", tags=["workflow-builder"])


@router.post("/create")
async def create_workflow(
    name: str,
    description: str,
    current_user: dict = Depends(get_current_user)
):
    """إنشاء workflow جديد"""
    try:
        check_action_permission("workflows.create", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    workflow = builder.create_workflow(name, description)
    
    return {"success": True, "workflow": workflow.to_dict()}


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على workflow"""
    try:
        check_action_permission("workflows.view", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    workflow = builder.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow


@router.get("/")
async def list_workflows(current_user: dict = Depends(get_current_user)):
    """قائمة workflows"""
    try:
        check_action_permission("workflows.view", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    workflows = builder.list_workflows()
    
    return {"workflows": workflows, "count": len(workflows)}


@router.post("/{workflow_id}/step")
async def add_step(
    workflow_id: str,
    step_type: str,
    action: str,
    parameters: Optional[Dict[str, Any]] = None,
    condition: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """إضافة خطوة للـworkflow"""
    try:
        check_action_permission("workflows.edit", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    result = builder.add_step(
        workflow_id=workflow_id,
        step_type=step_type,
        action=action,
        parameters=parameters,
        condition=condition
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/{workflow_id}/suggest")
async def suggest_next_step(
    workflow_id: str,
    current_step: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """اقتراح الخطوة التالية"""
    try:
        check_action_permission("workflows.view", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    suggestions = builder.suggest_next_step(workflow_id, current_step)
    
    return {"suggestions": suggestions}


@router.post("/{workflow_id}/autocomplete")
async def auto_complete_step(
    workflow_id: str,
    partial_action: str,
    current_user: dict = Depends(get_current_user)
):
    """Auto-complete للخطوة"""
    try:
        check_action_permission("workflows.edit", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    completions = builder.auto_complete_step(workflow_id, partial_action)
    
    return {"completions": completions}


@router.get("/{workflow_id}/debug")
async def debug_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Debug workflow"""
    try:
        check_action_permission("workflows.view", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    result = builder.debug_workflow(workflow_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/{workflow_id}/execution-map")
async def get_execution_map(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على execution map"""
    try:
        check_action_permission("workflows.view", current_user)
    except HTTPException:
        pass
    
    builder = get_workflow_builder()
    result = builder.get_execution_map(workflow_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

