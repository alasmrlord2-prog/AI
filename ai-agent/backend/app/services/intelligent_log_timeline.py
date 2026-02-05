"""
Intelligent Log Timeline Service
نظام timeline ذكي للـlogs يربط الأحداث ويحدد السبب الجذري
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import re


class LogEvent:
    """حدث log"""
    def __init__(
        self,
        timestamp: datetime,
        level: str,
        message: str,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = timestamp
        self.level = level  # "debug", "info", "warning", "error", "critical"
        self.message = message
        self.source = source
        self.metadata = metadata or {}
        self.related_events: List['LogEvent'] = []
        self.correlation_score = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "source": self.source,
            "metadata": self.metadata,
            "correlation_score": self.correlation_score,
            "related_count": len(self.related_events)
        }


class IntelligentTimeline:
    """
    Timeline ذكي للـlogs
    يربط الأحداث ويحدد السبب الجذري
    """
    
    def __init__(self):
        self.events: List[LogEvent] = []
        self.error_patterns = [
            r"error|exception|failed|failure",
            r"timeout|connection\s+refused",
            r"out\s+of\s+memory|oom",
            r"permission\s+denied|access\s+denied",
            r"not\s+found|404|500",
        ]
        self.correlation_window = timedelta(minutes=5)  # نافذة الارتباط
    
    def parse_log_line(self, line: str, source: str = "logs") -> Optional[LogEvent]:
        """تحليل سطر log وإنشاء حدث"""
        # محاولة استخراج timestamp
        timestamp = datetime.now()
        level = "info"
        
        # محاولة استخراج timestamp من بداية السطر
        timestamp_patterns = [
            r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})",
            r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})",
            r"\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]",
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace(" ", "T"))
                    except:
                        pass
                break
        
        # تحديد المستوى
        line_lower = line.lower()
        if any(re.search(p, line_lower) for p in ["critical", "fatal", "panic"]):
            level = "critical"
        elif any(re.search(p, line_lower) for p in ["error", "exception"]):
            level = "error"
        elif any(re.search(p, line_lower) for p in ["warn", "warning"]):
            level = "warning"
        elif any(re.search(p, line_lower) for p in ["debug", "trace"]):
            level = "debug"
        else:
            level = "info"
        
        # استخراج metadata
        metadata = {}
        if "request_id" in line:
            match = re.search(r"request[_-]id[=:]?\s*([\w-]+)", line, re.IGNORECASE)
            if match:
                metadata["request_id"] = match.group(1)
        
        if "user" in line:
            match = re.search(r"user[=:]?\s*([\w@.]+)", line, re.IGNORECASE)
            if match:
                metadata["user"] = match.group(1)
        
        return LogEvent(
            timestamp=timestamp,
            level=level,
            message=line[:500],  # أول 500 حرف
            source=source,
            metadata=metadata
        )
    
    def add_logs(self, log_lines: List[str], source: str = "logs"):
        """إضافة logs جديدة"""
        for line in log_lines:
            event = self.parse_log_line(line, source)
            if event:
                self.events.append(event)
        
        # ترتيب حسب الوقت
        self.events.sort(key=lambda e: e.timestamp)
        
        # ربط الأحداث
        self._correlate_events()
    
    def _correlate_events(self):
        """ربط الأحداث ذات الصلة"""
        # إعادة تعيين الروابط
        for event in self.events:
            event.related_events = []
            event.correlation_score = 0.0
        
        # ربط الأحداث
        for i, event1 in enumerate(self.events):
            if event1.level not in ["error", "critical", "warning"]:
                continue
            
            for j, event2 in enumerate(self.events):
                if i == j:
                    continue
                
                # التحقق من النافذة الزمنية
                time_diff = abs((event1.timestamp - event2.timestamp).total_seconds())
                if time_diff > self.correlation_window.total_seconds():
                    continue
                
                score = self._calculate_correlation(event1, event2)
                if score > 0.3:  # عتبة الارتباط
                    event1.related_events.append(event2)
                    event1.correlation_score = max(event1.correlation_score, score)
    
    def _calculate_correlation(self, event1: LogEvent, event2: LogEvent) -> float:
        """حساب درجة الارتباط بين حدثين"""
        score = 0.0
        
        # نفس المصدر
        if event1.source == event2.source:
            score += 0.2
        
        # نفس request_id
        if event1.metadata.get("request_id") == event2.metadata.get("request_id"):
            score += 0.5
        
        # نفس المستخدم
        if event1.metadata.get("user") == event2.metadata.get("user"):
            score += 0.2
        
        # كلمات مشتركة في الرسالة
        words1 = set(event1.message.lower().split())
        words2 = set(event2.message.lower().split())
        common_words = words1.intersection(words2)
        if len(words1) > 0:
            score += 0.3 * (len(common_words) / len(words1))
        
        # القرب الزمني
        time_diff = abs((event1.timestamp - event2.timestamp).total_seconds())
        if time_diff < 60:  # أقل من دقيقة
            score += 0.2
        elif time_diff < 300:  # أقل من 5 دقائق
            score += 0.1
        
        return min(score, 1.0)
    
    def get_timeline(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level_filter: Optional[List[str]] = None,
        source_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        الحصول على timeline
        
        Args:
            start_time: وقت البداية
            end_time: وقت النهاية
            level_filter: تصفية حسب المستوى
            source_filter: تصفية حسب المصدر
        """
        filtered_events = self.events
        
        # تصفية حسب الوقت
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        # تصفية حسب المستوى
        if level_filter:
            filtered_events = [e for e in filtered_events if e.level in level_filter]
        
        # تصفية حسب المصدر
        if source_filter:
            filtered_events = [e for e in filtered_events if e.source in source_filter]
        
        # تجميع حسب الوقت
        timeline_data = []
        for event in filtered_events:
            timeline_data.append({
                **event.to_dict(),
                "related_events": [e.to_dict() for e in event.related_events[:5]]  # أول 5 أحداث مرتبطة
            })
        
        return {
            "events": timeline_data,
            "total_events": len(timeline_data),
            "time_range": {
                "start": (start_time or filtered_events[0].timestamp if filtered_events else None),
                "end": (end_time or filtered_events[-1].timestamp if filtered_events else None)
            }
        }
    
    def find_root_cause(self, error_event: LogEvent) -> Dict[str, Any]:
        """العثور على السبب الجذري لخطأ"""
        # البحث عن الأحداث المرتبطة قبل الخطأ
        before_events = [
            e for e in self.events
            if e.timestamp < error_event.timestamp
            and (e.timestamp - error_event.timestamp).total_seconds() > -300  # آخر 5 دقائق
        ]
        
        # ترتيب حسب درجة الارتباط
        before_events.sort(key=lambda e: self._calculate_correlation(error_event, e), reverse=True)
        
        # البحث عن نمط
        patterns = []
        for event in before_events[:10]:  # أول 10 أحداث
            if "timeout" in event.message.lower():
                patterns.append("timeout_before_error")
            if "connection" in event.message.lower():
                patterns.append("connection_issue")
            if "memory" in event.message.lower():
                patterns.append("memory_issue")
        
        return {
            "error_event": error_event.to_dict(),
            "likely_causes": [e.to_dict() for e in before_events[:5]],
            "patterns": list(set(patterns)),
            "recommendation": self._generate_recommendation(patterns)
        }
    
    def _generate_recommendation(self, patterns: List[str]) -> str:
        """توليد توصية بناءً على الأنماط"""
        if "timeout_before_error" in patterns:
            return "Check network connectivity and service response times"
        if "connection_issue" in patterns:
            return "Verify database and external service connections"
        if "memory_issue" in patterns:
            return "Check memory usage and consider increasing resources"
        return "Review related events in the timeline for more context"
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """ملخص الأخطاء"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            e for e in self.events
            if e.level in ["error", "critical"]
            and e.timestamp > cutoff
        ]
        
        error_by_source = defaultdict(int)
        error_by_level = defaultdict(int)
        
        for event in recent_errors:
            error_by_source[event.source] += 1
            error_by_level[event.level] += 1
        
        return {
            "total_errors": len(recent_errors),
            "by_source": dict(error_by_source),
            "by_level": dict(error_by_level),
            "time_range_hours": hours
        }


# Global instance
_timeline: Optional[IntelligentTimeline] = None


def get_timeline() -> IntelligentTimeline:
    """الحصول على مثيل timeline"""
    global _timeline
    if _timeline is None:
        _timeline = IntelligentTimeline()
    return _timeline

