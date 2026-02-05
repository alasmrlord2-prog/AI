"""AI Debugger API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
from app.services.ai_debugger import ai_debugger
from app.api.auth import get_current_user
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/debugger", tags=["debugger"])


class StartWatchingRequest(BaseModel):
    """Start watching request."""
    log_dirs: List[str]


class AnalyzeErrorRequest(BaseModel):
    """Analyze error request."""
    file_path: str
    errors: List[Dict]
    context: Optional[str] = None


@router.post("/watch/start")
async def start_watching(
    req: StartWatchingRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start watching log directories."""
    result = ai_debugger.start_watching(req.log_dirs)
    return result


@router.post("/watch/stop")
async def stop_watching(current_user: dict = Depends(get_current_user)):
    """Stop watching logs."""
    result = ai_debugger.stop_watching()
    return result


@router.post("/analyze")
async def analyze_error(
    req: AnalyzeErrorRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze an error using AI."""
    error_data = {
        "file": req.file_path,
        "errors": req.errors,
        "context": req.context or ""
    }
    
    analysis = ai_debugger.analyze_error(error_data)
    return analysis


@router.get("/errors")
async def get_recent_errors(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get recent errors."""
    return {
        "errors": ai_debugger.get_recent_errors(limit=limit)
    }


@router.post("/auto-fix/enable")
async def enable_auto_fix(current_user: dict = Depends(get_current_user)):
    """Enable auto-fix."""
    ai_debugger.auto_fix_enabled = True
    return {"status": "enabled"}


@router.post("/auto-fix/disable")
async def disable_auto_fix(current_user: dict = Depends(get_current_user)):
    """Disable auto-fix."""
    ai_debugger.auto_fix_enabled = False
    return {"status": "disabled"}


@router.get("/docker/{container_name}")
async def check_docker_logs(
    container_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Check Docker container logs."""
    result = ai_debugger.check_docker_logs(container_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to check logs"))
    
    return result


@router.get("/service/{service_name}")
async def check_service_status(
    service_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Check systemd service status."""
    result = ai_debugger.check_service_status(service_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to check service"))
    
    return result


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for live log streaming."""
    await websocket.accept()
    
    try:
        while True:
            # Send recent errors
            errors = ai_debugger.get_recent_errors(limit=5)
            await websocket.send_json({
                "type": "errors",
                "data": errors
            })
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass

