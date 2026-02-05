"""
Permissions API endpoints - Unified Permission System
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel
from app.core.permissions import get_permission_engine, PermissionResult, FEATURE_PERMISSIONS
from app.auth import verify_token, get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/permissions", tags=["permissions"])
security = HTTPBearer()


def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user if token is provided, otherwise return None"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload:
            return {
                "email": payload.get("email"),
                "role": payload.get("role", "viewer"),
                "name": payload.get("name")
            }
    except:
        pass
    return None


class PermissionCheckRequest(BaseModel):
    """Request to check permission"""
    action: str
    tool_name: Optional[str] = None
    resource: Optional[str] = None
    server: Optional[str] = None


class PermissionCheckResponse(BaseModel):
    """Response from permission check"""
    allowed: bool
    requires_approval: bool = False
    reason: Optional[str] = None
    action_id: Optional[str] = None


@router.post("/validate", response_model=PermissionCheckResponse)
async def validate_permission(
    request: PermissionCheckRequest,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Validate if an action is allowed
    
    This is the main endpoint that all features should use before executing any action.
    """
    engine = get_permission_engine()
    
    user_role = current_user.get("role") if current_user else None
    
    result = engine.check_permission(
        action=request.action,
        tool_name=request.tool_name,
        user_role=user_role
    )
    
    # If approval is required, create pending action
    if result.allowed and result.requires_approval:
        from app.pending_actions import add_pending_action
        action = add_pending_action(
            user_email=current_user.get("email", "system") if current_user else "system",
            tool_name=request.tool_name or request.action,
            tool_args={
                "action": request.action,
                "resource": request.resource,
                "server": request.server
            },
            reason=f"Action '{request.action}' requires approval"
        )
        result.action_id = action["id"]
    
    return PermissionCheckResponse(
        allowed=result.allowed,
        requires_approval=result.requires_approval,
        reason=result.reason,
        action_id=result.action_id
    )


@router.get("/validate")
async def validate_permission_get(
    action: str,
    tool_name: Optional[str] = None,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """Validate permission (GET version)"""
    request = PermissionCheckRequest(
        action=action,
        tool_name=tool_name
    )
    return await validate_permission(request, current_user)


@router.get("/list")
async def list_permissions(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    List all available permissions and their status
    """
    engine = get_permission_engine()
    
    permissions = []
    for action, feature in FEATURE_PERMISSIONS.items():
        result = engine.check_permission(action)
        permissions.append({
            "action": action,
            "description": feature.get("description", ""),
            "allowed": result.allowed,
            "requires_approval": result.requires_approval,
            "reason": result.reason,
            "tools": feature.get("tools", [])
        })
    
    return {
        "permissions": permissions,
        "agent_mode": engine.settings.agent_mode,
        "memory_mode": engine.settings.memory_mode,
        "tool_permissions": {
            "allow_shell": engine.settings.allow_shell,
            "allow_read_file": engine.settings.allow_read_file,
            "allow_doc_search": engine.settings.allow_doc_search,
            "allow_logs": engine.settings.allow_logs,
        }
    }


@router.get("/actions")
async def get_allowed_actions(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get list of all allowed actions
    """
    engine = get_permission_engine()
    allowed = engine.get_allowed_actions()
    requiring_approval = engine.get_actions_requiring_approval()
    
    return {
        "allowed_actions": allowed,
        "requiring_approval": requiring_approval,
        "total": len(allowed)
    }


@router.get("/actions/requiring-approval")
async def get_actions_requiring_approval(
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get list of actions that require approval
    """
    engine = get_permission_engine()
    requiring_approval = engine.get_actions_requiring_approval()
    
    return {
        "actions": requiring_approval,
        "total": len(requiring_approval)
    }


@router.get("/feature/{feature_name}")
async def get_feature_permission(
    feature_name: str,
    current_user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Get permission status for a specific feature
    """
    engine = get_permission_engine()
    
    if feature_name not in FEATURE_PERMISSIONS:
        raise HTTPException(status_code=404, detail=f"Feature '{feature_name}' not found")
    
    feature = FEATURE_PERMISSIONS[feature_name]
    result = engine.check_permission(feature_name)
    
    return {
        "feature": feature_name,
        "description": feature.get("description", ""),
        "allowed": result.allowed,
        "requires_approval": result.requires_approval,
        "reason": result.reason,
        "tools": feature.get("tools", []),
        "action_id": result.action_id
    }

