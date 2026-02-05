"""
Helper functions for using Permission Engine in API endpoints
"""
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Tuple
from app.core.permissions import get_permission_engine
from app.pending_actions import add_pending_action


def check_action_permission(
    action: str,
    current_user: Optional[Dict] = None,
    resource: Optional[str] = None,
    server: Optional[str] = None
) -> Tuple[bool, Optional[JSONResponse]]:
    """
    Check if action is allowed, return (allowed, response) tuple
    
    Args:
        action: Action name (e.g., "security.scan", "tool.run_shell")
        current_user: Current user dict (optional)
        resource: Resource path (optional)
        server: Server name (optional)
    
    Returns:
        Tuple[bool, Optional[JSONResponse]]: 
            - (True, None) if allowed and no approval needed
            - (False, JSONResponse) if requires approval
            - Raises HTTPException if denied
    
    Raises:
        HTTPException: If permission denied
    """
    engine = get_permission_engine()
    user_role = current_user.get("role") if current_user else None
    
    result = engine.check_permission(
        action=action,
        user_role=user_role
    )
    
    if not result.allowed:
        raise HTTPException(
            status_code=403,
            detail=result.reason or f"Permission denied: {action} is not allowed"
        )
    
    if result.requires_approval:
        user_email = current_user.get("email", "system") if current_user else "system"
        action_obj = add_pending_action(
            user_email=user_email,
            tool_name=action,
            tool_args={
                "action": action,
                "resource": resource,
                "server": server
            },
            reason=f"Action '{action}' requires approval"
        )
        return False, JSONResponse(
            status_code=202,
            content={
                "error": {
                    "status": "pending",
                    "action_id": action_obj["id"],
                    "message": "Action requires approval"
                }
            }
        )
    
    return True, None


def check_tool_permission(
    tool_name: str,
    current_user: Optional[Dict] = None
) -> None:
    """
    Check if tool is allowed, raise HTTPException if not
    
    Args:
        tool_name: Tool name (e.g., "run_shell", "read_file")
        current_user: Current user dict (optional)
    
    Raises:
        HTTPException: If permission denied or requires approval
    """
    check_action_permission(
        action=f"tool.{tool_name}",
        current_user=current_user
    )

