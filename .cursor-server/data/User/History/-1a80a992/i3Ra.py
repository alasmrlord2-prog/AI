"""
Attribute-Based Access Control (ABAC) Engine
نظام صلاحيات متقدم يعتمد على الصفات والظروف
"""
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json


class AttributeType(str, Enum):
    """أنواع الصفات"""
    USER = "user"  # صفات المستخدم
    RESOURCE = "resource"  # صفات المورد
    ENVIRONMENT = "environment"  # صفات البيئة
    ACTION = "action"  # صفات الإجراء


@dataclass
class Attribute:
    """صفة واحدة"""
    name: str
    value: Any
    attribute_type: AttributeType


@dataclass
class PolicyRule:
    """قاعدة سياسة ABAC"""
    name: str
    description: str
    conditions: Dict[str, Any]  # الشروط (مثل: team="devops", source_ip="vpn", last_login_days < 7)
    effect: str  # "allow" or "deny"
    priority: int = 100  # الأولوية (أقل = أعلى أولوية)
    actions: List[str] = field(default_factory=list)  # الإجراءات المسموحة
    resources: List[str] = field(default_factory=list)  # الموارد المستهدفة


@dataclass
class AccessRequest:
    """طلب وصول"""
    user: Dict[str, Any]  # معلومات المستخدم
    action: str  # الإجراء المطلوب
    resource: Optional[str] = None  # المورد المستهدف
    context: Dict[str, Any] = field(default_factory=dict)  # السياق الإضافي


class ABACEngine:
    """
    محرك ABAC - يتحقق من الصلاحيات بناءً على الصفات والظروف
    """
    
    def __init__(self):
        self.policies: List[PolicyRule] = []
        self.attribute_extractors: Dict[str, Callable] = {}
        self._initialize_default_extractors()
        self._load_default_policies()
    
    def _initialize_default_extractors(self):
        """تهيئة مستخرجي الصفات الافتراضيين"""
        self.attribute_extractors = {
            "user.team": lambda req: req.user.get("team", "unknown"),
            "user.role": lambda req: req.user.get("role", "user"),
            "user.email": lambda req: req.user.get("email", ""),
            "user.last_login_days": lambda req: self._get_last_login_days(req),
            "environment.source_ip": lambda req: req.context.get("source_ip", ""),
            "environment.is_vpn": lambda req: self._is_vpn(req),
            "environment.time_of_day": lambda req: datetime.now().hour,
            "environment.day_of_week": lambda req: datetime.now().weekday(),
            "resource.type": lambda req: self._get_resource_type(req.resource),
            "resource.owner": lambda req: self._get_resource_owner(req.resource),
        }
    
    def _get_last_login_days(self, req: AccessRequest) -> int:
        """حساب عدد الأيام منذ آخر تسجيل دخول"""
        last_login = req.user.get("last_login")
        if not last_login:
            return 999  # لم يسجل دخول أبداً
        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login)
        delta = datetime.now() - last_login
        return delta.days
    
    def _is_vpn(self, req: AccessRequest) -> bool:
        """التحقق إذا كان الاتصال من VPN"""
        source_ip = req.context.get("source_ip", "")
        vpn_ips = req.context.get("vpn_ips", [])
        return source_ip in vpn_ips or req.context.get("is_vpn", False)
    
    def _get_resource_type(self, resource: Optional[str]) -> str:
        """استخراج نوع المورد"""
        if not resource:
            return "unknown"
        if resource.startswith("/api/"):
            return "api"
        if resource.startswith("/app/"):
            return "application"
        if resource.startswith("/"):
            return "file"
        return "unknown"
    
    def _get_resource_owner(self, resource: Optional[str]) -> str:
        """استخراج مالك المورد"""
        # يمكن تحسين هذا لاحقاً
        return "system"
    
    def _load_default_policies(self):
        """تحميل السياسات الافتراضية"""
        default_policies = [
            PolicyRule(
                name="devops_vpn_deploy",
                description="DevOps team from VPN can deploy if last login < 7 days",
                conditions={
                    "user.team": "devops",
                    "environment.is_vpn": True,
                    "user.last_login_days": {"$lt": 7}
                },
                effect="allow",
                priority=10,
                actions=["cicd.deploy", "cicd.build"],
                resources=["*"]
            ),
            PolicyRule(
                name="admin_full_access",
                description="Admin role has full access",
                conditions={
                    "user.role": "admin"
                },
                effect="allow",
                priority=5,
                actions=["*"],
                resources=["*"]
            ),
            PolicyRule(
                name="safe_mode_block",
                description="Block dangerous actions in safe mode",
                conditions={
                    "environment.safe_mode": True,
                    "action": {"$in": ["tool.run_shell", "filesystem.write", "service.stop"]}
                },
                effect="deny",
                priority=1,
                actions=["*"],
                resources=["*"]
            ),
            PolicyRule(
                name="off_hours_restriction",
                description="Restrict certain actions outside business hours",
                conditions={
                    "environment.time_of_day": {"$not": {"$between": [9, 17]}},
                    "action": {"$in": ["cicd.deploy", "backup.restore"]}
                },
                effect="deny",
                priority=20,
                actions=["*"],
                resources=["*"]
            ),
        ]
        self.policies.extend(default_policies)
    
    def add_policy(self, policy: PolicyRule):
        """إضافة سياسة جديدة"""
        self.policies.append(policy)
        self.policies.sort(key=lambda p: p.priority)
    
    def remove_policy(self, policy_name: str):
        """حذف سياسة"""
        self.policies = [p for p in self.policies if p.name != policy_name]
    
    def extract_attributes(self, request: AccessRequest) -> Dict[str, Any]:
        """استخراج جميع الصفات من الطلب"""
        attributes = {}
        for attr_name, extractor in self.attribute_extractors.items():
            try:
                attributes[attr_name] = extractor(request)
            except Exception:
                attributes[attr_name] = None
        return attributes
    
    def evaluate_condition(self, condition: Any, attributes: Dict[str, Any]) -> bool:
        """تقييم شرط واحد"""
        if isinstance(condition, dict):
            # معالجة المشغلات الخاصة
            for operator, value in condition.items():
                if operator == "$eq":
                    return self._evaluate_operator("eq", condition, attributes, value)
                elif operator == "$ne":
                    return self._evaluate_operator("ne", condition, attributes, value)
                elif operator == "$lt":
                    return self._evaluate_operator("lt", condition, attributes, value)
                elif operator == "$gt":
                    return self._evaluate_operator("gt", condition, attributes, value)
                elif operator == "$lte":
                    return self._evaluate_operator("lte", condition, attributes, value)
                elif operator == "$gte":
                    return self._evaluate_operator("gte", condition, attributes, value)
                elif operator == "$in":
                    return self._evaluate_operator("in", condition, attributes, value)
                elif operator == "$not":
                    return not self.evaluate_condition(value, attributes)
                elif operator == "$between":
                    return self._evaluate_operator("between", condition, attributes, value)
                else:
                    # شرط عادي (key-value)
                    for key, val in condition.items():
                        attr_value = attributes.get(key)
                        if attr_value != val:
                            return False
                    return True
        else:
            # قيمة مباشرة
            return bool(condition)
    
    def _evaluate_operator(self, op: str, condition: Dict, attributes: Dict, value: Any) -> bool:
        """تقييم مشغل"""
        # استخراج اسم الصفة من الشرط
        # هذا يحتاج تحسين لكن للبساطة سنستخدم القيمة مباشرة
        if op == "eq":
            return value in attributes.values()
        elif op == "ne":
            return value not in attributes.values()
        elif op == "lt":
            for attr_val in attributes.values():
                if isinstance(attr_val, (int, float)) and attr_val < value:
                    return True
            return False
        elif op == "gt":
            for attr_val in attributes.values():
                if isinstance(attr_val, (int, float)) and attr_val > value:
                    return True
            return False
        elif op == "lte":
            for attr_val in attributes.values():
                if isinstance(attr_val, (int, float)) and attr_val <= value:
                    return True
            return False
        elif op == "gte":
            for attr_val in attributes.values():
                if isinstance(attr_val, (int, float)) and attr_val >= value:
                    return True
            return False
        elif op == "in":
            return any(attr_val in value for attr_val in attributes.values())
        elif op == "between":
            if isinstance(value, list) and len(value) == 2:
                for attr_val in attributes.values():
                    if isinstance(attr_val, (int, float)):
                        if value[0] <= attr_val <= value[1]:
                            return True
            return False
        return False
    
    def check_conditions(self, conditions: Dict[str, Any], attributes: Dict[str, Any]) -> bool:
        """التحقق من جميع الشروط"""
        for key, condition_value in conditions.items():
            if key.startswith("$"):
                # مشغل خاص
                if not self.evaluate_condition({key: condition_value}, attributes):
                    return False
            else:
                # شرط عادي
                attr_value = attributes.get(key)
                if isinstance(condition_value, dict):
                    if not self.evaluate_condition(condition_value, attributes):
                        return False
                else:
                    if attr_value != condition_value:
                        return False
        return True
    
    def check_access(self, request: AccessRequest) -> Dict[str, Any]:
        """
        التحقق من الصلاحيات
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "matched_policy": str,
                "attributes": Dict
            }
        """
        # استخراج الصفات
        attributes = self.extract_attributes(request)
        
        # إضافة الصفات الأساسية
        attributes["action"] = request.action
        attributes["resource"] = request.resource
        
        # التحقق من السياسات بالترتيب (حسب الأولوية)
        for policy in self.policies:
            # التحقق من تطابق الإجراء
            if policy.actions and "*" not in policy.actions:
                if request.action not in policy.actions:
                    continue
            
            # التحقق من تطابق المورد
            if policy.resources and "*" not in policy.resources:
                if request.resource and request.resource not in policy.resources:
                    continue
            
            # التحقق من الشروط
            if self.check_conditions(policy.conditions, attributes):
                return {
                    "allowed": policy.effect == "allow",
                    "reason": f"Policy '{policy.name}': {policy.description}",
                    "matched_policy": policy.name,
                    "attributes": attributes,
                    "effect": policy.effect
                }
        
        # افتراضياً: رفض الوصول
        return {
            "allowed": False,
            "reason": "No matching policy found - access denied by default",
            "matched_policy": None,
            "attributes": attributes,
            "effect": "deny"
        }
    
    def register_attribute_extractor(self, name: str, extractor: Callable):
        """تسجيل مستخرج صفة مخصص"""
        self.attribute_extractors[name] = extractor


# Global instance
_abac_engine: Optional[ABACEngine] = None


def get_abac_engine() -> ABACEngine:
    """الحصول على مثيل ABAC"""
    global _abac_engine
    if _abac_engine is None:
        _abac_engine = ABACEngine()
    return _abac_engine

