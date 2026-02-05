"""
Behavior-Based Alerting - 100% Local
تنبيهات ذكية قائمة على السلوك
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class Alert:
    """تنبيه"""
    def __init__(
        self,
        alert_id: str,
        alert_type: str,
        severity: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        self.alert_id = alert_id
        self.alert_type = alert_type
        self.severity = severity  # "low", "medium", "high", "critical"
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()
        self.acknowledged = False
        self.resolved = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved
        }


class BehaviorBasedAlerter:
    """
    نظام تنبيهات ذكي قائم على السلوك
    بدل alert غبي مثل "CPU > 80%"
    alerts ذكية مثل "زيادة غير طبيعية باستعلامات DB بعد تحديث backend"
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.alerts: List[Alert] = []
        self.max_alerts = 10000
        self.baseline: Dict[str, Any] = {}
        self.event_history: deque = deque(maxlen=10000)
        
        # أنماط التنبيهات
        self.alert_patterns = {
            "db_query_spike_after_update": {
                "description": "زيادة غير طبيعية باستعلامات DB بعد تحديث backend",
                "severity": "high"
            },
            "service_restart_pattern": {
                "description": "خدمة عم تعيد تشغيل حالها كل X دقايق",
                "severity": "critical"
            },
            "traffic_spike_from_unknown_ip": {
                "description": "Traffic spike من IP غريب",
                "severity": "high"
            },
            "unusual_user_activity": {
                "description": "نشاط غير معتاد من مستخدم",
                "severity": "medium"
            },
            "config_change_without_deploy": {
                "description": "تغيير config بدون deploy رسمي",
                "severity": "high"
            }
        }
    
    def record_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ):
        """تسجيل حدث"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.event_history.append(event)
        
        # التحقق من الأنماط
        self._check_patterns(event)
    
    def _check_patterns(self, event: Dict[str, Any]):
        """التحقق من أنماط التنبيهات"""
        event_type = event["type"]
        data = event["data"]
        
        # 1. DB query spike after update
        if event_type == "db_query" and data.get("count", 0) > 100:
            # التحقق من وجود update حديث
            recent_updates = [
                e for e in list(self.event_history)[-100:]
                if e["type"] == "backend_update"
                and (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 300
            ]
            
            if recent_updates:
                self._create_alert(
                    "db_query_spike_after_update",
                    f"زيادة غير طبيعية باستعلامات DB ({data.get('count')}) بعد تحديث backend",
                    {"query_count": data.get("count"), "update_time": recent_updates[0]["timestamp"]}
                )
        
        # 2. Service restart pattern
        if event_type == "service_restart":
            service_name = data.get("service", "unknown")
            
            # حساب عدد إعادة التشغيل في آخر 10 دقائق
            recent_restarts = [
                e for e in list(self.event_history)[-1000:]
                if e["type"] == "service_restart"
                and e["data"].get("service") == service_name
                and (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 600
            ]
            
            if len(recent_restarts) >= 3:
                self._create_alert(
                    "service_restart_pattern",
                    f"خدمة {service_name} عم تعيد تشغيل حالها كل {600/len(recent_restarts):.0f} دقيقة",
                    {"service": service_name, "restart_count": len(recent_restarts)}
                )
        
        # 3. Traffic spike from unknown IP
        if event_type == "traffic":
            ip = data.get("ip", "")
            request_count = data.get("count", 0)
            
            # التحقق من أن IP جديد أو غير معتاد
            ip_history = [
                e for e in list(self.event_history)[-1000:]
                if e["type"] == "traffic" and e["data"].get("ip") == ip
            ]
            
            if len(ip_history) < 5 and request_count > 100:
                self._create_alert(
                    "traffic_spike_from_unknown_ip",
                    f"Traffic spike من IP غريب: {ip} ({request_count} requests)",
                    {"ip": ip, "request_count": request_count}
                )
        
        # 4. Config change without deploy
        if event_type == "config_change":
            # التحقق من وجود deploy حديث
            recent_deploys = [
                e for e in list(self.event_history)[-100:]
                if e["type"] == "deploy"
                and (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 3600
            ]
            
            if not recent_deploys:
                self._create_alert(
                    "config_change_without_deploy",
                    f"تغيير config ({data.get('path', 'unknown')}) بدون deploy رسمي",
                    {"path": data.get("path"), "change_type": data.get("type")}
                )
    
    def _create_alert(
        self,
        alert_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """إنشاء تنبيه"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alerts)}"
        
        pattern = self.alert_patterns.get(alert_type, {})
        severity = pattern.get("severity", "medium")
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            context=context or {}
        )
        
        self.alerts.append(alert)
        
        # حفظ فقط آخر N
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        log_warning(f"Alert created: {alert_type} - {message}")
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        hours: Optional[int] = None,
        resolved: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """الحصول على التنبيهات"""
        filtered = self.alerts
        
        # تصفية حسب severity
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        
        # تصفية حسب الوقت
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            filtered = [a for a in filtered if a.timestamp > cutoff]
        
        # تصفية حسب resolved
        if resolved is not None:
            filtered = [a for a in filtered if a.resolved == resolved]
        
        # ترتيب حسب الوقت
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [a.to_dict() for a in filtered]
    
    def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """الاعتراف بتنبيه"""
        alert = next((a for a in self.alerts if a.alert_id == alert_id), None)
        
        if not alert:
            return {"success": False, "error": "Alert not found"}
        
        alert.acknowledged = True
        
        return {"success": True, "alert": alert.to_dict()}
    
    def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """حل تنبيه"""
        alert = next((a for a in self.alerts if a.alert_id == alert_id), None)
        
        if not alert:
            return {"success": False, "error": "Alert not found"}
        
        alert.resolved = True
        
        return {"success": True, "alert": alert.to_dict()}
    
    def get_statistics(self) -> Dict[str, Any]:
        """إحصائيات التنبيهات"""
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for alert in self.alerts:
            severity_counts[alert.severity] += 1
            type_counts[alert.alert_type] += 1
        
        # تنبيهات غير محلولة
        unresolved = [a for a in self.alerts if not a.resolved]
        
        return {
            "total_alerts": len(self.alerts),
            "unresolved": len(unresolved),
            "by_severity": dict(severity_counts),
            "by_type": dict(type_counts)
        }


# Global instance
_behavior_alerter: Optional[BehaviorBasedAlerter] = None


def get_behavior_alerter() -> BehaviorBasedAlerter:
    """الحصول على مثيل نظام التنبيهات"""
    global _behavior_alerter
    if _behavior_alerter is None:
        _behavior_alerter = BehaviorBasedAlerter()
    return _behavior_alerter

