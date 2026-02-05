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
        get_pending_actions, get_action_by_id, get_all_actions
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
    def get_all_actions():
        return []

# Import tools for execution
try:
    from app.tools.run_shell import run as run_shell_run
    from app.tools.read_file import run as read_file_run
    from app.tools.check_service import run as check_service_run
    from app.tools.security_scan import (
        scan_repo, scan_infra, scan_logs_auth, scan_network_security,
        scan_system_security, scan_docker_security
    )
except ImportError:
    def run_shell_run(cmd):
        return "Shell not available"
    def read_file_run(path):
        return "File read not available"
    def check_service_run(name):
        return "Service check not available"
    def scan_repo(*args, **kwargs):
        return {"error": "Security scan not available"}
    def scan_infra(*args, **kwargs):
        return {"error": "Security scan not available"}
    def scan_logs_auth(*args, **kwargs):
        return {"error": "Security scan not available"}
    def scan_network_security(*args, **kwargs):
        return {"error": "Security scan not available"}
    def scan_system_security(*args, **kwargs):
        return {"error": "Security scan not available"}
    def scan_docker_security(*args, **kwargs):
        return {"error": "Security scan not available"}


class RejectRequest(BaseModel):
    """Reject action request model."""
    reason: str = ""


@router.get("")
async def get_pending_actions_list(current_user: dict = Depends(require_role(["admin", "devops"]))):
    """Get all pending actions (admin/devops only)."""
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    # Return all actions (pending, approved, rejected) so frontend can show completed ones
    return {"actions": get_all_actions()}


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
        elif isinstance(tool_args, dict) and "action" in tool_args:
            # Security scan or other action-based requests
            action_name = tool_args.get("action", "")
            resource = tool_args.get("resource")
            
            # Execute security scans
            if action_name == "security.repo_scan":
                result = scan_repo(resource or "/app", 1000)
                action["execution_result"] = result
                action["executed_at"] = datetime.utcnow().isoformat()
            elif action_name == "security.infra_scan":
                result = scan_infra(resource or "/app")
                action["execution_result"] = result
                action["executed_at"] = datetime.utcnow().isoformat()
            elif action_name == "logs.read":
                result = scan_logs_auth(resource or "/app/logs", 1000)
                action["execution_result"] = result
                action["executed_at"] = datetime.utcnow().isoformat()
            elif action_name == "security.network_scan":
                result = scan_network_security()
                action["execution_result"] = result
                action["executed_at"] = datetime.utcnow().isoformat()
            elif action_name == "security.scan":
                result = scan_system_security()
                action["execution_result"] = result
                action["executed_at"] = datetime.utcnow().isoformat()
            elif action_name == "security.docker_scan":
                result = scan_docker_security()
                action["execution_result"] = result
                action["executed_at"] = datetime.utcnow().isoformat()
            else:
                # Generic action - mark as approved
                action["execution_result"] = f"Action '{action_name}' approved and ready for execution"
                action["executed_at"] = datetime.utcnow().isoformat()
        else:
            action["execution_error"] = f"Unknown tool/action: {tool_name}"
    except Exception as e:
        action["execution_error"] = str(e)
        action["executed_at"] = datetime.utcnow().isoformat()
    
    # Save the updated action with execution result
    from app.pending_actions import load_pending_actions, save_pending_actions
    all_actions = load_pending_actions()
    for idx, a in enumerate(all_actions):
        if a["id"] == action_id:
            all_actions[idx] = action
            break
    save_pending_actions(all_actions)
    
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

