"""
Incident Command Center - 100% Local
مركز إدارة الحوادث
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class Incident:
    """حادث أمني"""
    def __init__(
        self,
        incident_id: str,
        title: str,
        severity: str,
        incident_type: str,
        description: str,
        status: str = "open"
    ):
        self.incident_id = incident_id
        self.title = title
        self.severity = severity  # "low", "medium", "high", "critical"
        self.incident_type = incident_type
        self.description = description
        self.status = status  # "open", "investigating", "resolved", "closed"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.timeline: List[Dict[str, Any]] = []
        self.root_cause: Optional[str] = None
        self.fix_applied: Optional[str] = None
        self.logs: List[str] = []
        self.graphs: Dict[str, Any] = {}
        self.team_chat: List[Dict[str, Any]] = []
        self.related_incidents: List[str] = []
    
    def add_timeline_event(self, event: str, user: str, metadata: Optional[Dict[str, Any]] = None):
        """إضافة حدث للـtimeline"""
        self.timeline.append({
            "event": event,
            "user": user,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        self.updated_at = datetime.now()
    
    def set_root_cause(self, root_cause: str, user: str):
        """تعيين السبب الجذري"""
        self.root_cause = root_cause
        self.add_timeline_event(f"Root cause identified: {root_cause}", user)
    
    def apply_fix(self, fix: str, user: str):
        """تطبيق إصلاح"""
        self.fix_applied = fix
        self.status = "resolved"
        self.add_timeline_event(f"Fix applied: {fix}", user)
    
    def add_log(self, log_line: str):
        """إضافة log"""
        self.logs.append(f"{datetime.now().isoformat()}: {log_line}")
    
    def add_chat_message(self, user: str, message: str):
        """إضافة رسالة في chat الفريق"""
        self.team_chat.append({
            "user": user,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "severity": self.severity,
            "type": self.incident_type,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "timeline": self.timeline,
            "root_cause": self.root_cause,
            "fix_applied": self.fix_applied,
            "logs": self.logs[-100:],  # آخر 100 log
            "graphs": self.graphs,
            "team_chat": self.team_chat[-50:],  # آخر 50 رسالة
            "related_incidents": self.related_incidents
        }


class IncidentCommandCenter:
    """
    مركز إدارة الحوادث
    يدير الحوادث الأمنية مع timeline, root cause, fixes, logs, graphs, chat
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.incidents: Dict[str, Incident] = {}
        self.max_incidents = 10000
    
    def create_incident(
        self,
        title: str,
        severity: str,
        incident_type: str,
        description: str,
        created_by: str
    ) -> Incident:
        """إنشاء حادث جديد"""
        incident_id = f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.incidents)}"
        
        incident = Incident(
            incident_id=incident_id,
            title=title,
            severity=severity,
            incident_type=incident_type,
            description=description
        )
        
        incident.add_timeline_event(f"Incident created: {title}", created_by)
        
        self.incidents[incident_id] = incident
        
        # تقليل الحوادث إذا لزم الأمر
        if len(self.incidents) > self.max_incidents:
            # حذف أقدم الحوادث المغلقة
            closed_incidents = [
                (id, inc) for id, inc in self.incidents.items()
                if inc.status == "closed"
            ]
            closed_incidents.sort(key=lambda x: x[1].updated_at)
            
            for id, _ in closed_incidents[:100]:
                del self.incidents[id]
        
        log_info(f"Created incident: {incident_id} ({severity})")
        return incident
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """الحصول على حادث"""
        return self.incidents.get(incident_id)
    
    def list_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """قائمة الحوادث"""
        incidents = list(self.incidents.values())
        
        # تصفية حسب status
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        # تصفية حسب severity
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        
        # تصفية حسب الوقت
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            incidents = [i for i in incidents if i.created_at > cutoff]
        
        # ترتيب حسب الوقت
        incidents.sort(key=lambda x: x.created_at, reverse=True)
        
        return [i.to_dict() for i in incidents]
    
    def update_incident_status(
        self,
        incident_id: str,
        status: str,
        user: str
    ) -> Dict[str, Any]:
        """تحديث حالة الحادث"""
        incident = self.get_incident(incident_id)
        if not incident:
            return {"success": False, "error": "Incident not found"}
        
        old_status = incident.status
        incident.status = status
        incident.add_timeline_event(f"Status changed: {old_status} -> {status}", user)
        
        log_info(f"Updated incident {incident_id} status to {status}")
        return {"success": True, "incident": incident.to_dict()}
    
    def set_root_cause(
        self,
        incident_id: str,
        root_cause: str,
        user: str
    ) -> Dict[str, Any]:
        """تعيين السبب الجذري"""
        incident = self.get_incident(incident_id)
        if not incident:
            return {"success": False, "error": "Incident not found"}
        
        incident.set_root_cause(root_cause, user)
        
        return {"success": True, "incident": incident.to_dict()}
    
    def apply_fix(
        self,
        incident_id: str,
        fix: str,
        user: str
    ) -> Dict[str, Any]:
        """تطبيق إصلاح"""
        incident = self.get_incident(incident_id)
        if not incident:
            return {"success": False, "error": "Incident not found"}
        
        incident.apply_fix(fix, user)
        
        return {"success": True, "incident": incident.to_dict()}
    
    def add_log(
        self,
        incident_id: str,
        log_line: str
    ) -> Dict[str, Any]:
        """إضافة log للحادث"""
        incident = self.get_incident(incident_id)
        if not incident:
            return {"success": False, "error": "Incident not found"}
        
        incident.add_log(log_line)
        
        return {"success": True}
    
    def add_chat_message(
        self,
        incident_id: str,
        user: str,
        message: str
    ) -> Dict[str, Any]:
        """إضافة رسالة في chat الفريق"""
        incident = self.get_incident(incident_id)
        if not incident:
            return {"success": False, "error": "Incident not found"}
        
        incident.add_chat_message(user, message)
        
        return {"success": True, "message": "Chat message added"}
    
    def get_statistics(self) -> Dict[str, Any]:
        """إحصائيات الحوادث"""
        incidents = list(self.incidents.values())
        
        status_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for incident in incidents:
            status_counts[incident.status] += 1
            severity_counts[incident.severity] += 1
            type_counts[incident.incident_type] += 1
        
        # حوادث مفتوحة حرجة
        critical_open = len([
            i for i in incidents
            if i.severity == "critical" and i.status != "closed"
        ])
        
        return {
            "total_incidents": len(incidents),
            "open_incidents": status_counts.get("open", 0),
            "critical_open": critical_open,
            "by_status": dict(status_counts),
            "by_severity": dict(severity_counts),
            "by_type": dict(type_counts)
        }


# Global instance
_incident_center: Optional[IncidentCommandCenter] = None


def get_incident_center() -> IncidentCommandCenter:
    """الحصول على مثيل مركز الحوادث"""
    global _incident_center
    if _incident_center is None:
        _incident_center = IncidentCommandCenter()
    return _incident_center

