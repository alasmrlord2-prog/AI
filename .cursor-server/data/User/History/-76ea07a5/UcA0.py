"""Tools API endpoints."""
from fastapi import APIRouter, Depends
from app.models.tools import ToolReadFile, ToolRunShell, ToolService
from app.utils.helpers import load_settings
from app.api.auth import get_current_user
from app.exceptions import AuthorizationError

router = APIRouter(prefix="/api/tools", tags=["tools"])

# Import auth functions
try:
    from auth import check_permission, can_approve
except ImportError:
    def check_permission(*args, **kwargs):
        return True
    def can_approve(*args, **kwargs):
        return True

# Import pending actions
try:
    from pending_actions import add_pending_action
    PENDING_ACTIONS_AVAILABLE = True
except ImportError:
    PENDING_ACTIONS_AVAILABLE = False
    def add_pending_action(*args, **kwargs):
        return {}

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
    settings = load_settings()
    if not settings.allow_read_file:
        return {"error": "read_file disabled from settings"}
    
    if not check_permission(current_user.get("role", "viewer"), "read_file"):
        raise AuthorizationError("Permission denied")
    
    try:
        return {"content": read_file_run(payload.path)}
    except Exception as e:
        return {"error": str(e)}


@router.post("/run_shell")
async def api_run_shell(payload: ToolRunShell, current_user: dict = Depends(get_current_user)):
    """Run shell command tool endpoint."""
    settings = load_settings()
    if not settings.allow_shell:
        return {"error": "run_shell disabled from settings"}
    
    # Check if approval required
    if "run_shell" in settings.require_approval:
        if not can_approve(current_user.get("role", "viewer")):
            if PENDING_ACTIONS_AVAILABLE:
                action = add_pending_action(
                    user_email=current_user.get("email", "unknown"),
                    tool_name="run_shell",
                    tool_args={"cmd": payload.cmd},
                    reason="Requires approval"
                )
                return {
                    "status": "pending",
                    "action_id": action["id"],
                    "message": "Action requires approval"
                }
            else:
                return {"error": "Action requires approval but approval system not available"}
    
    if not check_permission(current_user.get("role", "viewer"), "run_shell"):
        raise AuthorizationError("Permission denied")
    
    try:
        return {"output": run_shell_run(payload.cmd)}
    except Exception as e:
        return {"error": str(e)}


@router.post("/service")
def api_service(payload: ToolService, current_user: dict = Depends(get_current_user)):
    """Service check tool endpoint."""
    if not check_permission(current_user.get("role", "viewer"), "check_service"):
        raise AuthorizationError("Permission denied")
    
    try:
        return {"status": check_service_run(payload.name)}
    except Exception as e:
        return {"error": str(e)}

