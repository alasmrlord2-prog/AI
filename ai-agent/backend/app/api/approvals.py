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
    """Approve a pending action and execute it."""
    import logging
    logger = logging.getLogger(__name__)
    
    if not PENDING_ACTIONS_AVAILABLE:
        return {"error": "Pending actions not available"}
    
    from datetime import datetime
    import json
    
    # Load and approve the action
    action = approve_action(action_id, current_user.get("email", "unknown"))
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    logger.info(f"Approving action {action_id}: tool_name={action.get('tool_name')}, tool_args={action.get('tool_args')}")
    
    # Execute the action if approved
    tool_name = action.get("tool_name", "")
    tool_args = action.get("tool_args", {})
    
    # Handle case where tool_args might be a string
    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
        except (json.JSONDecodeError, TypeError):
            tool_args = {}
    
    # Ensure tool_args is a dict
    if not isinstance(tool_args, dict):
        tool_args = {}
    
    execution_success = False
    execution_output = None
    execution_error = None
    
    try:
        # Handle tool-based actions
        if tool_name == "run_shell":
            cmd = tool_args.get("cmd", "")
            if not cmd:
                raise ValueError("No command provided in tool_args")
            logger.info(f"Executing shell command: {cmd}")
            execution_output = run_shell_run(cmd)
            execution_success = True
            logger.info(f"Shell command executed successfully")
            
        elif tool_name == "read_file":
            path = tool_args.get("path", "")
            if not path:
                raise ValueError("No path provided in tool_args")
            logger.info(f"Reading file: {path}")
            execution_output = read_file_run(path)
            execution_success = True
            logger.info(f"File read successfully")
            
        elif tool_name == "check_service":
            name = tool_args.get("name", "")
            if not name:
                raise ValueError("No service name provided in tool_args")
            logger.info(f"Checking service: {name}")
            execution_output = check_service_run(name)
            execution_success = True
            logger.info(f"Service check completed")
            
        # Handle action-based requests (security.scan, cicd.deploy, etc.)
        elif tool_name.startswith("security."):
            action_name = tool_name
            resource = tool_args.get("resource")
            logger.info(f"🔒 Executing security action: {action_name}, resource: {resource}")
            
            # Execute the actual security scan
            try:
                if action_name == "security.repo_scan":
                    path = resource or "/home/ai/ai-agent/backend"
                    max_files = tool_args.get("max_files", 1000)
                    logger.info(f"📁 Starting repo scan on path: {path}, max_files: {max_files}")
                    result = scan_repo(path, max_files)
                    if isinstance(result, dict) and "error" in result:
                        raise Exception(result.get("error", "Scan failed"))
                    execution_output = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    execution_success = True
                    logger.info(f"✅ Repo scan completed successfully. Found {len(result.get('secrets_found', []))} secrets")
                    
                elif action_name == "security.infra_scan":
                    path = resource or "/home/ai/ai-agent/backend"
                    logger.info(f"🏗️ Starting infra scan on path: {path}")
                    result = scan_infra(path)
                    if isinstance(result, dict) and "error" in result:
                        raise Exception(result.get("error", "Scan failed"))
                    execution_output = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    execution_success = True
                    logger.info(f"✅ Infra scan completed successfully. Found {len(result.get('issues', []))} issues")
                    
                elif action_name == "security.scan" or action_name == "security.system_scan":
                    logger.info(f"🖥️ Starting system security scan")
                    result = scan_system_security()
                    if isinstance(result, dict) and "error" in result:
                        raise Exception(result.get("error", "Scan failed"))
                    execution_output = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    execution_success = True
                    summary = result.get("summary", {})
                    logger.info(f"✅ System scan completed. High: {summary.get('high_risk', 0)}, Medium: {summary.get('medium_risk', 0)}, Low: {summary.get('low_risk', 0)}")
                    
                elif action_name == "security.network_scan":
                    logger.info(f"🌐 Starting network security scan")
                    result = scan_network_security()
                    if isinstance(result, dict) and "error" in result:
                        raise Exception(result.get("error", "Scan failed"))
                    execution_output = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    execution_success = True
                    logger.info(f"✅ Network scan completed successfully")
                    
                elif action_name == "security.docker_scan":
                    logger.info(f"🐳 Starting Docker security scan")
                    result = scan_docker_security()
                    if isinstance(result, dict) and "error" in result:
                        raise Exception(result.get("error", "Scan failed"))
                    execution_output = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    execution_success = True
                    logger.info(f"✅ Docker scan completed successfully")
                    
                elif action_name == "logs.read":
                    path = resource or "/var/log"
                    lines = tool_args.get("lines", 1000)
                    logger.info(f"📋 Starting logs scan on path: {path}, lines: {lines}")
                    result = scan_logs_auth(path, lines)
                    if isinstance(result, dict) and "error" in result:
                        raise Exception(result.get("error", "Scan failed"))
                    execution_output = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    execution_success = True
                    logger.info(f"✅ Logs scan completed. Found {result.get('summary', {}).get('total_failed', 0)} failed logins")
                    
                else:
                    execution_output = f"Action '{action_name}' approved. Security scan type not implemented for execution."
                    execution_success = True
                    logger.warning(f"⚠️ Security action {action_name} not implemented for execution")
            except Exception as scan_error:
                error_msg = f"Security scan execution error: {str(scan_error)}"
                logger.error(f"❌ {error_msg}", exc_info=True)
                execution_error = error_msg
                execution_output = None
                execution_success = False
                
        elif tool_name.startswith("cicd.") or tool_name.startswith("backup."):
            action_name = tool_name
            logger.info(f"Action-based request: {action_name}")
            # For cicd/backup actions, mark as approved but don't execute here
            execution_output = f"Action '{action_name}' approved. Execution should be triggered from the respective endpoint."
            execution_success = True
            logger.info(f"Action {action_name} approved")
            
        # Generic action handling
        elif isinstance(tool_args, dict) and "action" in tool_args:
            action_name = tool_args.get("action", "")
            logger.info(f"Generic action request: {action_name}")
            execution_output = f"Action '{action_name}' approved. Ready for execution."
            execution_success = True
            
        # Check for cmd in tool_args (fallback for run_shell)
        elif isinstance(tool_args, dict) and "cmd" in tool_args:
            cmd = tool_args.get("cmd", "")
            logger.info(f"Executing shell command from tool_args: {cmd}")
            execution_output = run_shell_run(cmd)
            execution_success = True
            
        # Check for path in tool_args (fallback for read_file)
        elif isinstance(tool_args, dict) and "path" in tool_args:
            path = tool_args.get("path", "")
            logger.info(f"Reading file from tool_args: {path}")
            execution_output = read_file_run(path)
            execution_success = True
            
        # Check for name in tool_args (fallback for check_service)
        elif isinstance(tool_args, dict) and "name" in tool_args:
            name = tool_args.get("name", "")
            logger.info(f"Checking service from tool_args: {name}")
            execution_output = check_service_run(name)
            execution_success = True
            
        else:
            error_msg = f"Unknown tool/action: {tool_name}. tool_args: {tool_args}"
            logger.warning(error_msg)
            execution_error = error_msg
            execution_output = f"Action approved but execution not implemented for: {tool_name}"
            
    except Exception as e:
        error_msg = f"Execution error: {str(e)}"
        logger.error(f"Error executing action {action_id}: {error_msg}", exc_info=True)
        execution_error = error_msg
        execution_output = None
    
    # Update action with execution results
    action["executed_at"] = datetime.utcnow().isoformat()
    if execution_success:
        action["execution_result"] = execution_output
        if execution_error:
            action["execution_warning"] = execution_error
    else:
        action["execution_error"] = execution_error or "Execution failed"
        if execution_output:
            action["execution_result"] = execution_output
    
    # Save the updated action
    from app.pending_actions import load_pending_actions, save_pending_actions
    all_actions = load_pending_actions()
    for idx, a in enumerate(all_actions):
        if a["id"] == action_id:
            all_actions[idx] = action
            break
    else:
        # Action not found in list, append it
        all_actions.append(action)
    
    save_pending_actions(all_actions)
    logger.info(f"Action {action_id} saved with execution result")
    
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

