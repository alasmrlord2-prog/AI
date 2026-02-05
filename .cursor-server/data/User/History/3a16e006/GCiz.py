"""Approvals API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.auth import require_role
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/pending-actions", tags=["approvals"])

# Import pending actions
try:
    from app.pending_actions import (
        add_pending_action, approve_action, reject_action,
        get_pending_actions, get_action_by_id
    )
    PENDING_ACTIONS_AVAILABLE = True
except ImportError:
    PENDING_ACTIONS_AVAILABLE = False
    def add_pending_action(*args, **kwargs):
        return {}
    def approve_action(*args, **kwargs):
        return None
    def reject_action(*args, **kwargs):
        return None
    def get_pending_actions():
        return []
    def get_action_by_id(*args, **kwargs):
        return None

# Import tools for execution
try:
    from app.tools.run_shell import run as run_shell_run
    from app.tools.read_file import run as read_file_run
    from app.tools.check_service import run as check_service_run
except ImportError:
    def run_shell_run(cmd):
        return "Shell not available"
    def read_file_run(path):
        return "File read not available"
    def check_service_run(name):
        return "Service check not available"


class RejectRequest(BaseModel):
    """Reject action request model."""
    reason: str = ""


@router.get("")
async def get_pending_actions_list(current_user: dict = Depends(require_role(["admin", "devops"]))):
    """Get all pending actions (admin/devops only)."""
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    return {"actions": get_pending_actions()}


@router.post("/{action_id}/approve")
async def approve_pending_action(
    action_id: str,
    current_user: dict = Depends(require_role(["admin", "devops"]))
):
    """Approve a pending action."""
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    
    from datetime import datetime
    action = approve_action(action_id, current_user.get("email", "unknown"))
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Execute the action if approved
    # Note: Approval bypasses permission check, but we still validate the action exists
    tool_name = action.get("tool_name", "")
    tool_args = action.get("tool_args", {})
    
    try:
        if tool_name == "run_shell" or (isinstance(tool_args, dict) and "cmd" in tool_args):
            cmd = tool_args.get("cmd", "")
            output = run_shell_run(cmd)
            action["execution_result"] = output
            action["executed_at"] = datetime.utcnow().isoformat()
        elif tool_name == "read_file" or (isinstance(tool_args, dict) and "path" in tool_args):
            path = tool_args.get("path", "")
            output = read_file_run(path)
            action["execution_result"] = output
            action["executed_at"] = datetime.utcnow().isoformat()
        elif tool_name == "check_service" or (isinstance(tool_args, dict) and "name" in tool_args):
            name = tool_args.get("name", "")
            output = check_service_run(name)
            action["execution_result"] = output
            action["executed_at"] = datetime.utcnow().isoformat()
        else:
            # Check if it's an action-based request
            action_name = tool_args.get("action", "")
            if action_name:
                # Action was approved, mark as executed
                action["execution_result"] = "Action approved and ready for execution"
                action["executed_at"] = datetime.utcnow().isoformat()
            else:
                action["execution_error"] = f"Unknown tool/action: {tool_name}"
    except Exception as e:
        action["execution_error"] = str(e)
    
    return {"status": "approved", "action": action}


@router.post("/{action_id}/reject")
async def reject_pending_action(
    action_id: str,
    req: RejectRequest = RejectRequest(reason=""),
    current_user: dict = Depends(require_role(["admin", "devops"]))
):
    """Reject a pending action."""
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    
    action = reject_action(action_id, current_user.get("email", "unknown"), req.reason)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return {"status": "rejected", "action": action}

