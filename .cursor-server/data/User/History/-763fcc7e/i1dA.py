"""Workflow Builder API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.workflow_service import workflow_service
from app.auth import get_current_user

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


class CreateWorkflowRequest(BaseModel):
    """Create workflow request."""
    name: str
    nodes: List[Dict]
    edges: List[Dict]


class ExecuteWorkflowRequest(BaseModel):
    """Execute workflow request."""
    trigger_data: Optional[Dict] = None


@router.post("")
async def create_workflow(
    req: CreateWorkflowRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new workflow."""
    workflow = workflow_service.create_workflow(
        name=req.name,
        nodes=req.nodes,
        edges=req.edges
    )
    
    return workflow


@router.get("")
async def list_workflows(current_user: dict = Depends(get_current_user)):
    """List all workflows."""
    return {
        "workflows": workflow_service.list_workflows()
    }


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workflow by ID."""
    workflow = workflow_service.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a workflow."""
    result = workflow_service.delete_workflow(workflow_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Workflow not found"))
    
    return result


@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    req: ExecuteWorkflowRequest,
    current_user: dict = Depends(get_current_user)
):
    """Execute a workflow."""
    execution = await workflow_service.execute_workflow(
        workflow_id=workflow_id,
        trigger_data=req.trigger_data
    )
    
    if not execution.get("success") and execution.get("status") == "failed":
        raise HTTPException(status_code=400, detail=execution.get("error", "Execution failed"))
    
    return execution


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get execution by ID."""
    execution = workflow_service.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution


@router.get("/executions")
async def list_executions(
    workflow_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List executions."""
    return {
        "executions": workflow_service.list_executions(workflow_id=workflow_id, limit=limit)
    }

