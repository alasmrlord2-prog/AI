"""
Security AI Orchestrator - 100% Local
منسق النظام الأمني - يجمع كل المكونات
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.security_ai.collector import get_log_collector
from app.services.security_ai.detector import get_anomaly_detector
from app.services.ai_threat_detection import get_threat_detector
from app.services.security_ai.explainer import get_ai_explainer
from app.services.security_ai.responder import get_auto_responder
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class SecurityAIOrchestrator:
    """
    منسق النظام الأمني - محلي 100%
    يجمع Log Collector + Threat Detection + Anomaly Detection + AI Explainer + Auto Responder
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.collector = get_log_collector()
        self.threat_detector = get_threat_detector()
        self.anomaly_detector = get_anomaly_detector()
        self.explainer = get_ai_explainer()
        self.responder = get_auto_responder()
        self.incidents: List[Dict[str, Any]] = []
        self.max_incidents = 1000
        
        # ربط collector مع detectors
        self.collector.add_callback(self._on_log_line)
    
    def _on_log_line(self, file_path: str, line: str):
        """معالج سطر log جديد"""
        try:
            # تحليل التهديدات
            threat = self.threat_detector.analyze_log_line(line, file_path)
            
            if threat:
                # إنشاء incident
                incident = self._create_incident(threat, line, file_path)
                self.incidents.append(incident)
                
                # حفظ فقط آخر N incidents
                if len(self.incidents) > self.max_incidents:
                    self.incidents = self.incidents[-self.max_incidents:]
                
                # الاستجابة التلقائية
                if self.settings.SECURITY_AI_AUTO_RESPONSE:
                    response = self.responder.respond_to_threat(threat)
                    incident["auto_response"] = response
                
                log_warning(f"Security threat detected: {threat.get('pattern')} - {incident.get('id')}")
        except Exception as e:
            log_warning(f"Error processing log line: {e}")
    
    def _create_incident(self, threat: Dict[str, Any], log_line: str, source: str) -> Dict[str, Any]:
        """إنشاء incident من threat"""
        incident_id = f"incident_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.incidents)}"
        
        # شرح AI
        explanation = self.explainer.explain_threat(threat)
        
        incident = {
            "id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "threat": threat,
            "source": source,
            "log_line": log_line[:500],
            "explanation": explanation,
            "status": "open",
            "severity": threat.get("severity", "medium")
        }
        
        return incident
    
    def start(self):
        """بدء النظام الأمني"""
        if not self.settings.SECURITY_AI_ENABLED:
            log_warning("Security AI is disabled")
            return
        
        # التحقق من OFFLINE_MODE
        if self.settings.OFFLINE_MODE:
            log_info("Security AI running in OFFLINE_MODE - 100% local, no external connections")
        
        # بدء collector
        self.collector.start()
        
        log_info("Security AI Orchestrator started")
    
    def stop(self):
        """إيقاف النظام الأمني"""
        self.collector.stop()
        log_info("Security AI Orchestrator stopped")
    
    def analyze_realtime(self, log_lines: List[str], source: str = "logs") -> Dict[str, Any]:
        """تحليل real-time"""
        # تحليل التهديدات
        threat_result = self.threat_detector.analyze_realtime(log_lines, source)
        
        # تحليل الشذوذات
        events = [
            {
                "type": "log_event",
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "line": line[:200]
            }
            for line in log_lines
        ]
        anomaly_result = self.anomaly_detector.detect(events)
        
        return {
            "threats": threat_result,
            "anomalies": anomaly_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_incidents(self, hours: int = 24, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """الحصول على الحوادث"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        
        filtered = [
            i for i in self.incidents
            if datetime.fromisoformat(i["timestamp"]) > cutoff
        ]
        
        if severity:
            filtered = [i for i in filtered if i.get("severity") == severity]
        
        return filtered
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام"""
        return {
            "enabled": self.settings.SECURITY_AI_ENABLED,
            "offline_mode": self.settings.OFFLINE_MODE,
            "auto_response": self.settings.SECURITY_AI_AUTO_RESPONSE,
            "incidents_count": len(self.incidents),
            "blocked_ips": len(self.responder.blocked_ips),
            "isolated_services": len(self.responder.isolated_services),
            "collector_status": "running" if self.collector.observer and self.collector.observer.is_alive() else "stopped"
        }


# Global instance
_orchestrator: Optional[SecurityAIOrchestrator] = None


def get_security_ai_orchestrator() -> SecurityAIOrchestrator:
    """الحصول على مثيل المنسق"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SecurityAIOrchestrator()
    return _orchestrator

