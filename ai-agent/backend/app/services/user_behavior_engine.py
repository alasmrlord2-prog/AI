"""
User Behavior Engine - 100% Local
نظام مراقبة سلوك المستخدمين
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class UserAction:
    """إجراء مستخدم"""
    def __init__(
        self,
        user: str,
        action: str,
        resource: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.user = user
        self.action = action
        self.resource = resource
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user": self.user,
            "action": self.action,
            "resource": self.resource,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class UserBehaviorEngine:
    """
    محرك مراقبة سلوك المستخدمين
    يكشف الأنماط المشبوهة في سلوك المستخدمين
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.user_actions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.user_baselines: Dict[str, Dict[str, Any]] = {}
        self.suspicious_actions: List[Dict[str, Any]] = []
        self.max_suspicious = 1000
        
        # قائمة الإجراءات الخطرة
        self.dangerous_actions = [
            "app.delete",
            "service.stop",
            "backup.delete",
            "config.write",
            "tool.run_shell",
            "filesystem.delete",
            "database.drop",
        ]
        
        # قائمة الإجراءات غير المعتادة
        self.unusual_actions = [
            "service.restart",
            "backup.restore",
            "cicd.deploy",
            "security.scan",
        ]
    
    def record_action(
        self,
        user: str,
        action: str,
        resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """تسجيل إجراء مستخدم"""
        action_obj = UserAction(user, action, resource, metadata=metadata)
        self.user_actions[user].append(action_obj)
        
        # التحقق من السلوك المشبوه
        suspicious = self._check_suspicious_behavior(user, action_obj)
        if suspicious:
            self.suspicious_actions.append({
                **suspicious,
                "user": user,
                "action": action,
                "timestamp": datetime.now().isoformat()
            })
            
            # حفظ فقط آخر N
            if len(self.suspicious_actions) > self.max_suspicious:
                self.suspicious_actions = self.suspicious_actions[-self.max_suspicious:]
            
            log_warning(f"Suspicious behavior detected for user {user}: {suspicious.get('reason')}")
    
    def _check_suspicious_behavior(self, user: str, action: UserAction) -> Optional[Dict[str, Any]]:
        """التحقق من السلوك المشبوه"""
        user_history = list(self.user_actions[user])
        
        # 1. إجراء خطير بدون سبب واضح
        if action.action in self.dangerous_actions:
            # التحقق من السياق
            recent_actions = [a for a in user_history[-10:] if a.action != action.action]
            
            # إذا كان الإجراء الخطير بدون تحضير
            if not any(a.action in ["backup.create", "config.read"] for a in recent_actions):
                return {
                    "type": "dangerous_action_without_preparation",
                    "severity": "high",
                    "reason": f"User performed dangerous action '{action.action}' without proper preparation",
                    "recommendation": "Review action and consider enabling safe mode"
                }
        
        # 2. إجراءات متعددة خطرة في وقت قصير
        recent_dangerous = [
            a for a in user_history[-20:]
            if a.action in self.dangerous_actions
        ]
        
        if len(recent_dangerous) >= 3:
            time_span = (recent_dangerous[-1].timestamp - recent_dangerous[0].timestamp).total_seconds()
            if time_span < 300:  # أقل من 5 دقائق
                return {
                    "type": "multiple_dangerous_actions",
                    "severity": "critical",
                    "reason": f"User performed {len(recent_dangerous)} dangerous actions in {time_span:.0f} seconds",
                    "recommendation": "Immediately review user activity and consider disabling account"
                }
        
        # 3. إجراء غير معتاد من المستخدم
        if action.action in self.unusual_actions:
            # التحقق من التاريخ
            user_baseline = self.user_baselines.get(user, {})
            action_frequency = user_baseline.get("action_frequency", {})
            
            if action.action not in action_frequency:
                # إجراء جديد تماماً
                return {
                    "type": "unusual_action",
                    "severity": "medium",
                    "reason": f"User performed unusual action '{action.action}' for the first time",
                    "recommendation": "Verify user intent and monitor closely"
                }
        
        # 4. نمط غير طبيعي (مثل حذف app بدون سبب)
        if action.action == "app.delete":
            # التحقق من وجود backups
            has_backup = any(
                a.action == "backup.create" 
                for a in user_history[-50:]
            )
            
            if not has_backup:
                return {
                    "type": "deletion_without_backup",
                    "severity": "high",
                    "reason": "User attempting to delete application without backup",
                    "recommendation": "Block action and require backup creation"
                }
        
        # 5. فتح shell بخدمة critical
        if action.action == "tool.run_shell":
            resource = action.resource or ""
            if "critical" in resource.lower() or "production" in resource.lower():
                return {
                    "type": "shell_access_critical_service",
                    "severity": "critical",
                    "reason": f"User attempting shell access to critical service: {resource}",
                    "recommendation": "Require additional approval or block"
                }
        
        # 6. تعديل DB بدون backup
        if action.action in ["database.write", "database.modify"]:
            has_backup = any(
                a.action == "backup.create"
                for a in user_history[-20:]
            )
            
            if not has_backup:
                return {
                    "type": "database_modification_without_backup",
                    "severity": "high",
                    "reason": "User attempting database modification without backup",
                    "recommendation": "Require backup before allowing modification"
                }
        
        return None
    
    def get_user_profile(self, user: str) -> Dict[str, Any]:
        """الحصول على ملف المستخدم"""
        user_history = list(self.user_actions[user])
        
        if not user_history:
            return {
                "user": user,
                "total_actions": 0,
                "action_breakdown": {},
                "most_used_actions": [],
                "risk_score": 0.0
            }
        
        # حساب الإحصائيات
        action_counts = defaultdict(int)
        for action in user_history:
            action_counts[action.action] += 1
        
        # حساب risk score
        risk_score = self._calculate_risk_score(user, user_history)
        
        # تحديث baseline
        self._update_baseline(user, user_history)
        
        return {
            "user": user,
            "total_actions": len(user_history),
            "action_breakdown": dict(action_counts),
            "most_used_actions": sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "risk_score": risk_score,
            "baseline": self.user_baselines.get(user, {})
        }
    
    def _calculate_risk_score(self, user: str, history: List[UserAction]) -> float:
        """حساب درجة المخاطرة"""
        if not history:
            return 0.0
        
        score = 0.0
        
        # إجراءات خطرة
        dangerous_count = sum(1 for a in history if a.action in self.dangerous_actions)
        score += dangerous_count * 0.3
        
        # إجراءات غير معتادة
        unusual_count = sum(1 for a in history if a.action in self.unusual_actions)
        score += unusual_count * 0.1
        
        # كثافة الإجراءات
        if len(history) > 1:
            time_span = (history[-1].timestamp - history[0].timestamp).total_seconds()
            if time_span > 0:
                actions_per_minute = len(history) / (time_span / 60)
                if actions_per_minute > 10:  # أكثر من 10 إجراءات في الدقيقة
                    score += 0.2
        
        return min(score, 1.0)  # حد أقصى 1.0
    
    def _update_baseline(self, user: str, history: List[UserAction]):
        """تحديث baseline للمستخدم"""
        if not history:
            return
        
        action_frequency = defaultdict(int)
        for action in history[-1000:]:  # آخر 1000 إجراء
            action_frequency[action.action] += 1
        
        self.user_baselines[user] = {
            "action_frequency": dict(action_frequency),
            "total_actions": len(history),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_suspicious_activities(self, hours: int = 24) -> List[Dict[str, Any]]:
        """الحصول على الأنشطة المشبوهة"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [
            activity for activity in self.suspicious_actions
            if datetime.fromisoformat(activity["timestamp"]) > cutoff
        ]
    
    def suggest_safe_mode(self, user: str) -> Dict[str, Any]:
        """اقتراح تفعيل Safe Mode"""
        user_profile = self.get_user_profile(user)
        risk_score = user_profile["risk_score"]
        
        if risk_score > 0.7:
            return {
                "recommendation": "enable_safe_mode",
                "reason": f"High risk score detected: {risk_score:.2f}",
                "user": user,
                "risk_score": risk_score,
                "message": "في شي مش طبيعي، هل تريد تفعيل Safe Mode؟"
            }
        
        return {
            "recommendation": "monitor",
            "reason": "Risk score within normal range",
            "user": user,
            "risk_score": risk_score
        }


# Global instance
_user_behavior_engine: Optional[UserBehaviorEngine] = None


def get_user_behavior_engine() -> UserBehaviorEngine:
    """الحصول على مثيل محرك سلوك المستخدمين"""
    global _user_behavior_engine
    if _user_behavior_engine is None:
        _user_behavior_engine = UserBehaviorEngine()
    return _user_behavior_engine

