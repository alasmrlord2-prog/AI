"""Tools API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.tools import ToolReadFile, ToolRunShell, ToolService
from app.utils.helpers import load_settings
from app.api.auth import get_current_user
from app.exceptions import AuthorizationError
from app.core.permissions import get_permission_engine
from app.pending_actions import add_pending_action, get_action_by_id

router = APIRouter(prefix="/api/tools", tags=["tools"])

# Import auth functions
try:
    from auth import check_permission, can_approve
except ImportError:
    def check_permission(*args, **kwargs):
        return True
    def can_approve(*args, **kwargs):
        return True

# Import tools
try:
    from app.tools.read_file import run as read_file_run
    from app.tools.run_shell import run as run_shell_run
    from app.tools.check_service import run as check_service_run
except ImportError:
    def read_file_run(path):
        return "File read not available"
    def run_shell_run(cmd):
        return "Shell not available"
    def check_service_run(name):
        return "Service check not available"


@router.post("/read_file")
def api_read_file(payload: ToolReadFile, current_user: dict = Depends(get_current_user)):
    """Read file tool endpoint."""
    # Check permission using Permission Engine
    engine = get_permission_engine()
    result = engine.check_tool_permission("read_file", current_user.get("role"))
    
    if not result.allowed:
        raise HTTPException(
            status_code=403,
            detail=result.reason or "Permission denied: read_file is not allowed"
        )
    
    if result.requires_approval:
        action = add_pending_action(
            user_email=current_user.get("email", "unknown"),
            tool_name="read_file",
            tool_args={"path": payload.path},
            reason="read_file requires approval"
        )
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=202,
            content={
                "error": {
                    "status": "pending",
                    "action_id": action["id"],
                    "message": "Action requires approval"
                }
            }
        )
    
    try:
        return {"content": read_file_run(payload.path)}
    except Exception as e:
        return {"error": str(e)}


@router.post("/run_shell")
async def api_run_shell(payload: ToolRunShell, current_user: dict = Depends(get_current_user)):
    """Run shell command tool endpoint."""
    # Check permission using Permission Engine
    engine = get_permission_engine()
    result = engine.check_tool_permission("run_shell", current_user.get("role"))
    
    if not result.allowed:
        raise HTTPException(
            status_code=403,
            detail=result.reason or "Permission denied: run_shell is not allowed"
        )
    
    if result.requires_approval:
        action = add_pending_action(
            user_email=current_user.get("email", "unknown"),
            tool_name="run_shell",
            tool_args={"cmd": payload.cmd},
            reason="run_shell requires approval"
        )
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=202,
            content={
                "error": {
                    "status": "pending",
                    "action_id": action["id"],
                    "message": "Action requires approval"
                }
            }
        )
    
    try:
        return {"output": run_shell_run(payload.cmd)}
    except Exception as e:
        return {"error": str(e)}


@router.post("/service")
def api_service(payload: ToolService, current_user: dict = Depends(get_current_user)):
    """Service check tool endpoint."""
    # Check permission using Permission Engine
    engine = get_permission_engine()
    result = engine.check_tool_permission("check_service", current_user.get("role"))
    
    if not result.allowed:
        raise HTTPException(
            status_code=403,
            detail=result.reason or "Permission denied: check_service is not allowed"
        )
    
    if result.requires_approval:
        action = add_pending_action(
            user_email=current_user.get("email", "unknown"),
            tool_name="check_service",
            tool_args={"name": payload.name},
            reason="check_service requires approval"
        )
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=202,
            content={
                "error": {
                    "status": "pending",
                    "action_id": action["id"],
                    "message": "Action requires approval"
                }
            }
        )
    
    try:
        return {"status": check_service_run(payload.name)}
    except Exception as e:
        return {"error": str(e)}

