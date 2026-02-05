"""
AI Threat Detection Service
نظام كشف التهديدات بالذكاء الاصطناعي
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict
from app.utils.logger import log_info, log_warning, log_error


class ThreatPattern:
    """نمط تهديد"""
    def __init__(self, name: str, pattern: str, severity: str, description: str):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.severity = severity  # "low", "medium", "high", "critical"
        self.description = description


class AIThreatDetector:
    """
    كاشف التهديدات بالذكاء الاصطناعي
    يراقب الـlogs real-time ويكشف الأنماط المشبوهة
    """
    
    def __init__(self):
        self.threat_patterns: List[ThreatPattern] = []
        self.anomaly_threshold = 0.7
        self.baseline_metrics: Dict[str, Any] = {}
        self.recent_events: List[Dict[str, Any]] = []
        self.max_events = 10000
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """تهيئة أنماط التهديدات"""
        patterns = [
            ThreatPattern(
                name="sql_injection",
                pattern=r"(union\s+select|drop\s+table|';?\s*(or|and)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
                severity="high",
                description="Possible SQL injection attempt"
            ),
            ThreatPattern(
                name="xss_attack",
                pattern=r"(<script|javascript:|onerror=|onload=)",
                severity="high",
                description="Possible XSS attack"
            ),
            ThreatPattern(
                name="command_injection",
                pattern=r"(;\s*(rm|cat|wget|curl|nc|bash|sh)\s|`.*`|\$\(.*\))",
                severity="critical",
                description="Possible command injection"
            ),
            ThreatPattern(
                name="path_traversal",
                pattern=r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow)",
                severity="high",
                description="Possible path traversal attack"
            ),
            ThreatPattern(
                name="brute_force",
                pattern=r"(failed\s+login|authentication\s+failed|invalid\s+password)",
                severity="medium",
                description="Possible brute force attack"
            ),
            ThreatPattern(
                name="privilege_escalation",
                pattern=r"(sudo|su\s|chmod\s+777|chown\s+root)",
                severity="critical",
                description="Possible privilege escalation attempt"
            ),
            ThreatPattern(
                name="data_exfiltration",
                pattern=r"(wget|curl|nc|scp|rsync).*http|ftp",
                severity="high",
                description="Possible data exfiltration"
            ),
            ThreatPattern(
                name="suspicious_process",
                pattern=r"(miner|crypto|backdoor|trojan)",
                severity="critical",
                description="Suspicious process detected"
            ),
        ]
        self.threat_patterns.extend(patterns)
    
    def analyze_log_line(self, log_line: str, source: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        تحليل سطر log واحد
        
        Returns:
            None إذا لم يكن هناك تهديد، أو Dict مع تفاصيل التهديد
        """
        threats_found = []
        
        for pattern in self.threat_patterns:
            matches = pattern.pattern.findall(log_line)
            if matches:
                threats_found.append({
                    "pattern": pattern.name,
                    "severity": pattern.severity,
                    "description": pattern.description,
                    "matches": matches[:3]  # أول 3 تطابقات
                })
        
        if threats_found:
            # تحديد أعلى مستوى خطورة
            severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            max_severity = max(threats_found, key=lambda x: severity_levels[x["severity"]])
            
            return {
                "threat_detected": True,
                "severity": max_severity["severity"],
                "threats": threats_found,
                "log_line": log_line[:500],  # أول 500 حرف
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def detect_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        كشف الشذوذات في الأحداث
        
        Args:
            events: قائمة الأحداث
        
        Returns:
            قائمة الشذوذات المكتشفة
        """
        anomalies = []
        
        # تحليل التكرار
        event_counts = defaultdict(int)
        for event in events:
            event_type = event.get("type", "unknown")
            event_counts[event_type] += 1
        
        # إذا كان هناك حدث يتكرر بشكل غير طبيعي
        for event_type, count in event_counts.items():
            baseline = self.baseline_metrics.get(event_type, {}).get("avg_count", 0)
            if baseline > 0:
                ratio = count / baseline
                if ratio > 3.0:  # أكثر من 3 أضعاف المعدل الطبيعي
                    anomalies.append({
                        "type": "frequency_anomaly",
                        "event_type": event_type,
                        "count": count,
                        "baseline": baseline,
                        "ratio": ratio,
                        "severity": "high" if ratio > 5 else "medium"
                    })
        
        # تحليل الأنماط الزمنية
        if len(events) > 10:
            time_diffs = []
            prev_time = None
            for event in events[-100:]:  # آخر 100 حدث
                timestamp = event.get("timestamp")
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            event_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        else:
                            event_time = timestamp
                        
                        if prev_time:
                            diff = (event_time - prev_time).total_seconds()
                            time_diffs.append(diff)
                        prev_time = event_time
                    except:
                        pass
            
            if time_diffs:
                avg_diff = sum(time_diffs) / len(time_diffs)
                if avg_diff < 1.0:  # أحداث بسرعة كبيرة
                    anomalies.append({
                        "type": "temporal_anomaly",
                        "avg_interval": avg_diff,
                        "severity": "medium",
                        "description": "Events occurring too frequently"
                    })
        
        return anomalies
    
    def add_event(self, event: Dict[str, Any]):
        """إضافة حدث جديد"""
        self.recent_events.append(event)
        if len(self.recent_events) > self.max_events:
            self.recent_events = self.recent_events[-self.max_events:]
    
    def analyze_realtime(self, log_lines: List[str], source: str = "logs") -> Dict[str, Any]:
        """
        تحليل real-time للـlogs
        
        Args:
            log_lines: قائمة أسطر الـlogs
            source: مصدر الـlogs
        
        Returns:
            تقرير التحليل
        """
        threats = []
        events = []
        
        for line in log_lines:
            # تحليل التهديدات
            threat = self.analyze_log_line(line, source)
            if threat:
                threats.append(threat)
                self.add_event({
                    "type": "threat",
                    "timestamp": datetime.now().isoformat(),
                    "data": threat
                })
            
            # إضافة حدث عادي
            events.append({
                "type": "log_event",
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "line": line[:200]
            })
        
        # كشف الشذوذات
        anomalies = self.detect_anomalies(events)
        
        # تحديد الإجراء المطلوب
        action = self._determine_action(threats, anomalies)
        
        return {
            "threats_detected": len(threats),
            "anomalies_detected": len(anomalies),
            "threats": threats,
            "anomalies": anomalies,
            "recommended_action": action,
            "timestamp": datetime.now().isoformat()
        }
    
    def _determine_action(self, threats: List[Dict], anomalies: List[Dict]) -> Dict[str, Any]:
        """تحديد الإجراء المطلوب بناءً على التهديدات"""
        if not threats and not anomalies:
            return {"action": "none", "reason": "No threats detected"}
        
        # البحث عن تهديدات حرجة
        critical_threats = [t for t in threats if t.get("severity") == "critical"]
        if critical_threats:
            return {
                "action": "isolate",
                "reason": "Critical threats detected",
                "details": critical_threats
            }
        
        # البحث عن تهديدات عالية
        high_threats = [t for t in threats if t.get("severity") == "high"]
        if high_threats:
            return {
                "action": "alert_and_monitor",
                "reason": "High severity threats detected",
                "details": high_threats
            }
        
        # شذوذات
        if anomalies:
            return {
                "action": "alert",
                "reason": "Anomalies detected",
                "details": anomalies
            }
        
        return {
            "action": "monitor",
            "reason": "Low severity issues detected"
        }
    
    def update_baseline(self, metrics: Dict[str, Any]):
        """تحديث الخط الأساسي للمقاييس"""
        self.baseline_metrics.update(metrics)
    
    def get_threat_summary(self, hours: int = 24) -> Dict[str, Any]:
        """ملخص التهديدات خلال فترة زمنية"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_threats = [
            e for e in self.recent_events
            if e.get("type") == "threat"
            and datetime.fromisoformat(e.get("timestamp", "")) > cutoff
        ]
        
        severity_counts = defaultdict(int)
        pattern_counts = defaultdict(int)
        
        for event in recent_threats:
            threat_data = event.get("data", {})
            severity = threat_data.get("severity", "unknown")
            severity_counts[severity] += 1
            
            for threat in threat_data.get("threats", []):
                pattern = threat.get("pattern", "unknown")
                pattern_counts[pattern] += 1
        
        return {
            "total_threats": len(recent_threats),
            "severity_breakdown": dict(severity_counts),
            "pattern_breakdown": dict(pattern_counts),
            "time_range_hours": hours
        }


# Global instance
_threat_detector: Optional[AIThreatDetector] = None


def get_threat_detector() -> AIThreatDetector:
    """الحصول على مثيل كاشف التهديدات"""
    global _threat_detector
    if _threat_detector is None:
        _threat_detector = AIThreatDetector()
    return _threat_detector

