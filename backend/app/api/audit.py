"""Audit Trail API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from app.services.audit_service import audit_service, ActionType
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/audit", tags=["audit"])


class LogActionRequest(BaseModel):
    """Log action request."""
    action: str
    payload: Optional[dict] = None
    status: str = "success"


@router.post("/log")
async def log_action(
    req: LogActionRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Log an action."""
    try:
        action_type = ActionType(req.action)
    except ValueError:
        action_type = ActionType.OTHER
    
    # Get client IP
    client_ip = request.client.host if request.client else None
    
    log_id = audit_service.log_action(
        user=current_user.get("email", "unknown"),
        action=action_type,
        payload=req.payload,
        ip=client_ip,
        status=req.status
    )
    
    return {
        "success": True,
        "log_id": log_id
    }


@router.get("/logs")
async def get_logs(
    user: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get audit logs."""
    action_type = None
    if action:
        try:
            action_type = ActionType(action)
        except ValueError:
            pass
    
    logs = audit_service.get_logs(
        user=user,
        action=action_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    total = audit_service.get_log_count(
        user=user,
        action=action_type,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "logs": logs,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/export")
async def export_logs(
    output_file: str = "audit_export.json",
    user: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Export audit logs."""
    action_type = None
    if action:
        try:
            action_type = ActionType(action)
        except ValueError:
            pass
    
    result = audit_service.export_logs(
        output_file=output_file,
        user=user,
        action=action_type,
        start_date=start_date,
        end_date=end_date
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Export failed"))
    
    return result


@router.get("/actions")
async def get_action_types(current_user: dict = Depends(get_current_user)):
    """Get available action types."""
    return {
        "actions": [action.value for action in ActionType]
    }

