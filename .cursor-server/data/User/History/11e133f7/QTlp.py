"""
ABAC Service Layer
طبقة خدمة لنظام ABAC
"""
from typing import Dict, Any, Optional
from app.core.abac import get_abac_engine, AccessRequest, PolicyRule
from app.utils.logger import log_info, log_warning


class ABACService:
    """خدمة ABAC"""
    
    def __init__(self):
        self.engine = get_abac_engine()
    
    def check_access(
        self,
        user: Dict[str, Any],
        action: str,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        التحقق من الصلاحيات
        
        Args:
            user: معلومات المستخدم
            action: الإجراء المطلوب
            resource: المورد المستهدف
            context: السياق الإضافي (IP, VPN, etc.)
        
        Returns:
            نتيجة التحقق من الصلاحيات
        """
        request = AccessRequest(
            user=user,
            action=action,
            resource=resource,
            context=context or {}
        )
        
        result = self.engine.check_access(request)
        
        log_info(f"ABAC check: user={user.get('email')}, action={action}, allowed={result['allowed']}")
        
        return result
    
    def add_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """إضافة سياسة جديدة"""
        try:
            policy = PolicyRule(
                name=policy_data["name"],
                description=policy_data.get("description", ""),
                conditions=policy_data.get("conditions", {}),
                effect=policy_data.get("effect", "allow"),
                priority=policy_data.get("priority", 100),
                actions=policy_data.get("actions", []),
                resources=policy_data.get("resources", [])
            )
            self.engine.add_policy(policy)
            log_info(f"ABAC policy added: {policy.name}")
            return {"success": True, "policy": policy.name}
        except Exception as e:
            log_warning(f"Failed to add ABAC policy: {e}")
            return {"success": False, "error": str(e)}
    
    def list_policies(self) -> Dict[str, Any]:
        """قائمة السياسات"""
        policies = []
        for policy in self.engine.policies:
            policies.append({
                "name": policy.name,
                "description": policy.description,
                "effect": policy.effect,
                "priority": policy.priority,
                "actions": policy.actions,
                "resources": policy.resources,
                "conditions": policy.conditions
            })
        return {"policies": policies}
    
    def remove_policy(self, policy_name: str) -> Dict[str, Any]:
        """حذف سياسة"""
        try:
            self.engine.remove_policy(policy_name)
            log_info(f"ABAC policy removed: {policy_name}")
            return {"success": True}
        except Exception as e:
            log_warning(f"Failed to remove ABAC policy: {e}")
            return {"success": False, "error": str(e)}


# Global instance
abac_service = ABACService()

