import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from app.utils.path_resolver import resolve_path

# Use resolve_path for portable path resolution
try:
    PENDING_ACTIONS_FILE = resolve_path("memory/pending_actions.json")
except:
    # Fallback to direct path if resolve fails
    PENDING_ACTIONS_FILE = "memory/pending_actions.json"

def load_pending_actions() -> List[Dict]:
    """Load pending actions from JSON file"""
    if not os.path.exists(PENDING_ACTIONS_FILE):
        return []
    
    try:
        with open(PENDING_ACTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_pending_actions(actions: List[Dict]):
    """Save pending actions to JSON file"""
    os.makedirs(os.path.dirname(PENDING_ACTIONS_FILE), exist_ok=True)
    try:
        with open(PENDING_ACTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(actions, f, ensure_ascii=False, indent=2)
        # Fix permissions
        os.chmod(PENDING_ACTIONS_FILE, 0o666)
    except PermissionError:
        # If permission denied, try to create in temp location
        import tempfile
        temp_file = os.path.join(tempfile.gettempdir(), "pending_actions.json")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(actions, f, ensure_ascii=False, indent=2)
        print(f"Warning: Could not write to {PENDING_ACTIONS_FILE}, using {temp_file}")

def add_pending_action(
    user_email: str,
    tool_name: str,
    tool_args: Dict,
    reason: str = ""
) -> Dict:
    """Add a new pending action"""
    actions = load_pending_actions()
    
    action = {
        "id": f"action_{datetime.utcnow().timestamp()}",
        "user_email": user_email,
        "tool_name": tool_name,
        "tool_args": tool_args,
        "reason": reason,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "approved_by": None,
        "approved_at": None,
    }
    
    actions.append(action)
    save_pending_actions(actions)
    return action

def approve_action(action_id: str, approved_by: str) -> Optional[Dict]:
    """Approve a pending action"""
    actions = load_pending_actions()
    
    for action in actions:
        if action["id"] == action_id and action["status"] == "pending":
            action["status"] = "approved"
            action["approved_by"] = approved_by
            action["approved_at"] = datetime.utcnow().isoformat()
            save_pending_actions(actions)
            return action
    
    return None

def reject_action(action_id: str, rejected_by: str, reason: str = "") -> Optional[Dict]:
    """Reject a pending action"""
    actions = load_pending_actions()
    
    for action in actions:
        if action["id"] == action_id and action["status"] == "pending":
            action["status"] = "rejected"
            action["approved_by"] = rejected_by
            action["approved_at"] = datetime.utcnow().isoformat()
            action["rejection_reason"] = reason
            save_pending_actions(actions)
            return action
    
    return None

def get_pending_actions() -> List[Dict]:
    """Get all pending actions"""
    actions = load_pending_actions()
    return [a for a in actions if a["status"] == "pending"]

def get_all_actions() -> List[Dict]:
    """Get all actions (pending, approved, rejected)"""
    return load_pending_actions()

def get_action_by_id(action_id: str) -> Optional[Dict]:
    """Get action by ID"""
    actions = load_pending_actions()
    for action in actions:
        if action["id"] == action_id:
            return action
    return None

