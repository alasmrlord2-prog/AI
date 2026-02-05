"""
Unified Permission Engine - نظام صلاحيات موحد لكل الواجهات
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
from app.models.settings import SettingsModel
from app.utils.helpers import load_settings


class AgentMode(str, Enum):
    """Agent Modes"""
    SAFE = "safe"
    DEVOPS = "devops"
    ROOT = "root"
    SHORT = "short"  # Short session


class MemoryMode(str, Enum):
    """Memory Modes"""
    OFF = "off"
    SHORT = "short"
    LONG = "long"


# Mapping between features and required tools/permissions
FEATURE_PERMISSIONS: Dict[str, Dict] = {
    # Security Center
    "security.scan": {
        "tools": ["read_file", "run_shell"],
        "description": "Run security scan"
    },
    "security.repo_scan": {
        "tools": ["read_file"],
        "description": "Repository scan"
    },
    "security.infra_scan": {
        "tools": ["read_file", "run_shell"],
        "description": "Infrastructure scan"
    },
    "security.network_scan": {
        "tools": ["run_shell"],
        "description": "Network scan"
    },
    "security.docker_scan": {
        "tools": ["run_shell"],
        "description": "Docker scan"
    },
    "security.vulnerability_scan": {
        "tools": ["read_file", "run_shell"],
        "description": "Vulnerability scan"
    },
    "security.malware_scan": {
        "tools": ["read_file", "run_shell"],
        "description": "Malware scan"
    },
    "security.penetration_test": {
        "tools": ["run_shell"],
        "description": "Penetration testing",
        "requires_approval": True
    },
    
    # SOC/SIEM
    "soc.alerts": {
        "tools": ["read_logs"],
        "description": "SOC alerts access"
    },
    "siem.query": {
        "tools": ["doc_search", "read_file"],
        "description": "SIEM queries"
    },
    "siem.monitor": {
        "tools": ["read_logs", "read_file"],
        "description": "SIEM monitoring"
    },
    
    # CI/CD
    "cicd.deploy": {
        "tools": ["run_shell"],
        "description": "CI/CD deployment",
        "requires_approval": True
    },
    "cicd.build": {
        "tools": ["run_shell"],
        "description": "CI/CD build",
        "requires_approval": True
    },
    "cicd.rollback": {
        "tools": ["run_shell"],
        "description": "CI/CD rollback",
        "requires_approval": True
    },
    
    # AI Debugger
    "debugger.analyze": {
        "tools": ["read_logs"],
        "description": "AI Debugger analysis"
    },
    "debugger.full": {
        "tools": ["read_logs", "run_shell"],
        "description": "AI Debugger full access",
        "requires_approval": True
    },
    "debugger.auto_fix": {
        "tools": ["run_shell", "write_file"],
        "description": "AI Debugger auto-fix",
        "requires_approval": True
    },
    
    # Monitoring
    "monitoring.view": {
        "tools": ["read_logs"],
        "description": "View monitoring data"
    },
    "monitoring.configure": {
        "tools": ["read_file", "write_file"],
        "description": "Configure monitoring",
        "requires_approval": True
    },
    
    # Logs
    "logs.read": {
        "tools": ["read_logs"],
        "description": "Read logs"
    },
    "logs.download": {
        "tools": ["read_logs"],
        "description": "Download logs"
    },
    
    # Backup
    "backup.create": {
        "tools": ["run_shell"],
        "description": "Create backup",
        "requires_approval": True
    },
    "backup.restore": {
        "tools": ["run_shell"],
        "description": "Restore backup",
        "requires_approval": True
    },
    "backup.list": {
        "tools": ["read_file"],
        "description": "List backups"
    },
    
    # Workflows
    "workflow.execute": {
        "tools": ["run_shell"],
        "description": "Execute workflow",
        "requires_approval": True
    },
    "workflow.create": {
        "tools": ["write_file"],
        "description": "Create workflow",
        "requires_approval": True
    },
    "workflow.edit": {
        "tools": ["read_file", "write_file"],
        "description": "Edit workflow",
        "requires_approval": True
    },
    
    # Incidents
    "incidents.view": {
        "tools": [],
        "description": "View incidents"
    },
    "incidents.create": {
        "tools": [],
        "description": "Create incident"
    },
    "incidents.resolve": {
        "tools": ["read_file"],
        "description": "Resolve incident"
    },
    
    # Services
    "service.restart": {
        "tools": ["run_shell"],
        "description": "Restart service",
        "requires_approval": True
    },
    "service.stop": {
        "tools": ["run_shell"],
        "description": "Stop service",
        "requires_approval": True
    },
    "service.start": {
        "tools": ["run_shell"],
        "description": "Start service",
        "requires_approval": True
    },
    
    # Filesystem
    "filesystem.read": {
        "tools": ["read_file"],
        "description": "Read file"
    },
    "filesystem.write": {
        "tools": ["write_file"],
        "description": "Write file",
        "requires_approval": True
    },
    "filesystem.list": {
        "tools": ["read_file"],  # list_dir uses read_file internally
        "description": "List directory"
    },
    
    # Tools (direct tool access)
    "tool.run_shell": {
        "tools": ["run_shell"],
        "description": "Run shell command",
        "requires_approval": True
    },
    "tool.read_file": {
        "tools": ["read_file"],
        "description": "Read file"
    },
    "tool.write_file": {
        "tools": ["write_file"],
        "description": "Write file",
        "requires_approval": True
    },
    "tool.read_logs": {
        "tools": ["read_logs"],
        "description": "Read logs"
    },
    "tool.doc_search": {
        "tools": ["doc_search"],
        "description": "Document search"
    },
    "tool.check_service": {
        "tools": ["check_service"],
        "description": "Check service status"
    },
}


class PermissionResult:
    """Result of permission check"""
    def __init__(
        self,
        allowed: bool,
        requires_approval: bool = False,
        reason: Optional[str] = None,
        action_id: Optional[str] = None
    ):
        self.allowed = allowed
        self.requires_approval = requires_approval
        self.reason = reason
        self.action_id = action_id
    
    def to_dict(self) -> Dict:
        return {
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reason": self.reason,
            "action_id": self.action_id
        }


class PermissionEngine:
    """Unified Permission Engine"""
    
    def __init__(self, settings: Optional[SettingsModel] = None):
        self.settings = settings or load_settings()
    
    def reload_settings(self):
        """Reload settings from file"""
        self.settings = load_settings()
    
    def check_permission(
        self,
        action: str,
        tool_name: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> PermissionResult:
        """
        Check if an action is allowed
        
        Args:
            action: Action name (e.g., "security.scan", "tool.run_shell")
            tool_name: Direct tool name (e.g., "run_shell") - optional
            user_role: User role for additional checks - optional
        
        Returns:
            PermissionResult
        """
        # Reload settings to get latest
        self.reload_settings()
        
        # If tool_name is provided directly, map it to action
        if tool_name and not action.startswith("tool."):
            action = f"tool.{tool_name}"
        
        # Get feature requirements
        feature = FEATURE_PERMISSIONS.get(action)
        
        if not feature:
            # Unknown action - deny by default
            return PermissionResult(
                allowed=False,
                reason=f"Unknown action: {action}"
            )
        
        required_tools = feature.get("tools", [])
        feature_requires_approval = feature.get("requires_approval", False)
        
        # Check agent mode
        agent_mode = self.settings.agent_mode.lower()
        
        # ROOT mode - allow everything
        if agent_mode == AgentMode.ROOT.value:
            return PermissionResult(
                allowed=True,
                requires_approval=False
            )
        
        # SAFE mode - only read operations
        if agent_mode == AgentMode.SAFE.value:
            dangerous_tools = ["run_shell", "write_file", "restart_service"]
            if any(tool in required_tools for tool in dangerous_tools):
                return PermissionResult(
                    allowed=False,
                    reason=f"Action '{action}' requires dangerous tools which are blocked in SAFE mode"
                )
        
        # Check tool permissions from settings
        tool_permissions = {
            "run_shell": self.settings.allow_shell,
            "read_file": self.settings.allow_read_file,
            "write_file": self.settings.allow_shell,  # write_file needs shell access
            "doc_search": self.settings.allow_doc_search,
            "read_logs": self.settings.allow_logs,
            "check_service": self.settings.allow_shell,  # check_service needs shell
        }
        
        # Check if all required tools are allowed
        for tool in required_tools:
            if tool in tool_permissions:
                if not tool_permissions[tool]:
                    return PermissionResult(
                        allowed=False,
                        reason=f"Tool '{tool}' is disabled in settings"
                    )
        
        # Check if specific tool is disabled
        if tool_name:
            if tool_name == "run_shell" and not self.settings.allow_shell:
                return PermissionResult(
                    allowed=False,
                    reason="run_shell is disabled in settings"
                )
            if tool_name == "read_file" and not self.settings.allow_read_file:
                return PermissionResult(
                    allowed=False,
                    reason="read_file is disabled in settings"
                )
            if tool_name == "doc_search" and not self.settings.allow_doc_search:
                return PermissionResult(
                    allowed=False,
                    reason="doc_search is disabled in settings"
                )
            if tool_name == "read_logs" and not self.settings.allow_logs:
                return PermissionResult(
                    allowed=False,
                    reason="read_logs is disabled in settings"
                )
        
        # Check memory mode for DB-dependent operations
        memory_mode = self.settings.memory_mode.lower()
        if memory_mode == MemoryMode.OFF.value:
            # Some operations might need memory - check if action needs it
            # For now, we allow all operations but memory won't be saved
            pass
        
        # Determine if approval is required
        requires_approval = False
        
        if agent_mode == AgentMode.DEVOPS.value:
            # In DevOps mode, check if action or tool requires approval
            if feature_requires_approval:
                requires_approval = True
            elif tool_name in self.settings.require_approval:
                requires_approval = True
            elif any(tool in self.settings.require_approval for tool in required_tools):
                requires_approval = True
        
        # Action is allowed
        return PermissionResult(
            allowed=True,
            requires_approval=requires_approval
        )
    
    def check_tool_permission(
        self,
        tool_name: str,
        user_role: Optional[str] = None
    ) -> PermissionResult:
        """Check permission for a specific tool"""
        return self.check_permission(
            action=f"tool.{tool_name}",
            tool_name=tool_name,
            user_role=user_role
        )
    
    def get_allowed_actions(self) -> List[str]:
        """Get list of all allowed actions based on current settings"""
        allowed = []
        
        for action, feature in FEATURE_PERMISSIONS.items():
            result = self.check_permission(action)
            if result.allowed:
                allowed.append(action)
        
        return allowed
    
    def get_actions_requiring_approval(self) -> List[str]:
        """Get list of actions that require approval"""
        requiring_approval = []
        
        for action, feature in FEATURE_PERMISSIONS.items():
            result = self.check_permission(action)
            if result.allowed and result.requires_approval:
                requiring_approval.append(action)
        
        return requiring_approval


# Global instance
_permission_engine: Optional[PermissionEngine] = None


def get_permission_engine() -> PermissionEngine:
    """Get global permission engine instance"""
    global _permission_engine
    if _permission_engine is None:
        _permission_engine = PermissionEngine()
    return _permission_engine

