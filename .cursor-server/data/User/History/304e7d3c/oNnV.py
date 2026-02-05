"""
AI Performance Tuner - 100% Local
ضبط الأداء بالذكاء الاصطناعي
"""
import psutil
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class PerformanceMetrics:
    """مقاييس الأداء"""
    def __init__(self):
        self.cpu_usage: deque = deque(maxlen=1000)
        self.memory_usage: deque = deque(maxlen=1000)
        self.response_times: deque = deque(maxlen=1000)
        self.error_rates: deque = deque(maxlen=1000)
        self.timestamps: deque = deque(maxlen=1000)
    
    def add_sample(self, cpu: float, memory: float, response_time: float, error_rate: float):
        """إضافة عينة جديدة"""
        self.cpu_usage.append(cpu)
        self.memory_usage.append(memory)
        self.response_times.append(response_time)
        self.error_rates.append(error_rate)
        self.timestamps.append(datetime.now())


class AIPerformanceTuner:
    """
    ضابط الأداء بالذكاء الاصطناعي
    يراقب الأداء ويعطي توصيات تلقائية
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.metrics = PerformanceMetrics()
        self.baseline: Dict[str, Any] = {}
        self.recommendations_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def collect_metrics(self) -> Dict[str, Any]:
        """جمع المقاييس الحالية"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # حساب response time متوسط (مثال - يمكن جلبها من monitoring)
        response_time = self._estimate_response_time()
        
        # حساب error rate (مثال)
        error_rate = self._estimate_error_rate()
        
        metrics = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": memory.used / (1024**3),
            "memory_total_gb": memory.total / (1024**3),
            "disk_percent": (disk.used / disk.total) * 100,
            "response_time_ms": response_time,
            "error_rate": error_rate,
            "timestamp": datetime.now().isoformat()
        }
        
        # إضافة للتاريخ
        self.metrics.add_sample(
            cpu_percent,
            memory.percent,
            response_time,
            error_rate
        )
        
        return metrics
    
    def _estimate_response_time(self) -> float:
        """تقدير response time (مثال)"""
        if len(self.metrics.response_times) > 0:
            return sum(self.metrics.response_times) / len(self.metrics.response_times)
        return 100.0  # افتراضي
    
    def _estimate_error_rate(self) -> float:
        """تقدير error rate (مثال)"""
        if len(self.metrics.error_rates) > 0:
            return sum(self.metrics.error_rates) / len(self.metrics.error_rates)
        return 0.0
    
    def analyze_and_recommend(self) -> Dict[str, Any]:
        """تحليل الأداء وإعطاء توصيات"""
        current_metrics = self.collect_metrics()
        recommendations = []
        
        # 1. تحليل CPU
        cpu_rec = self._analyze_cpu(current_metrics)
        if cpu_rec:
            recommendations.append(cpu_rec)
        
        # 2. تحليل Memory
        memory_rec = self._analyze_memory(current_metrics)
        if memory_rec:
            recommendations.append(memory_rec)
        
        # 3. تحليل Response Time
        response_rec = self._analyze_response_time(current_metrics)
        if response_rec:
            recommendations.append(response_rec)
        
        # 4. تحليل Error Rate
        error_rec = self._analyze_error_rate(current_metrics)
        if error_rec:
            recommendations.append(error_rec)
        
        # 5. تحليل Bottlenecks
        bottleneck_rec = self._analyze_bottlenecks(current_metrics)
        if bottleneck_rec:
            recommendations.append(bottleneck_rec)
        
        result = {
            "current_metrics": current_metrics,
            "recommendations": recommendations,
            "priority": self._calculate_priority(recommendations),
            "timestamp": datetime.now().isoformat()
        }
        
        # حفظ في التاريخ
        self.recommendations_history.append(result)
        if len(self.recommendations_history) > self.max_history:
            self.recommendations_history = self.recommendations_history[-self.max_history:]
        
        return result
    
    def _analyze_cpu(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تحليل CPU"""
        cpu_percent = metrics["cpu_percent"]
        
        if cpu_percent > 90:
            return {
                "type": "cpu",
                "severity": "critical",
                "issue": f"CPU usage is very high: {cpu_percent:.1f}%",
                "recommendation": "افتح worker زيادة أو scale out",
                "action": "increase_workers",
                "details": {
                    "current": cpu_percent,
                    "threshold": 90,
                    "suggested_workers": int(cpu_percent / 50) + 1
                }
            }
        elif cpu_percent > 70:
            return {
                "type": "cpu",
                "severity": "high",
                "issue": f"CPU usage is high: {cpu_percent:.1f}%",
                "recommendation": "افتح worker زيادة",
                "action": "increase_workers",
                "details": {
                    "current": cpu_percent,
                    "threshold": 70
                }
            }
        elif cpu_percent < 20 and len(self.metrics.cpu_usage) > 10:
            # CPU منخفض - يمكن تقليل الموارد
            avg_cpu = sum(list(self.metrics.cpu_usage)[-100:]) / min(100, len(self.metrics.cpu_usage))
            if avg_cpu < 20:
                return {
                    "type": "cpu",
                    "severity": "low",
                    "issue": f"CPU usage is low: {cpu_percent:.1f}%",
                    "recommendation": "خفف workers أو scale down لتوفير التكاليف",
                    "action": "decrease_workers",
                    "details": {
                        "current": cpu_percent,
                        "avg": avg_cpu
                    }
                }
        
        return None
    
    def _analyze_memory(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تحليل Memory"""
        memory_percent = metrics["memory_percent"]
        memory_used_gb = metrics["memory_used_gb"]
        
        if memory_percent > 90:
            return {
                "type": "memory",
                "severity": "critical",
                "issue": f"Memory usage is very high: {memory_percent:.1f}% ({memory_used_gb:.2f} GB)",
                "recommendation": "زيادة memory allocation أو تنظيف cache",
                "action": "increase_memory",
                "details": {
                    "current_percent": memory_percent,
                    "current_gb": memory_used_gb,
                    "threshold": 90
                }
            }
        elif memory_percent > 80:
            return {
                "type": "memory",
                "severity": "high",
                "issue": f"Memory usage is high: {memory_percent:.1f}%",
                "recommendation": "مراقبة memory وزيادة إذا لزم",
                "action": "monitor_memory",
                "details": {
                    "current": memory_percent,
                    "threshold": 80
                }
            }
        
        return None
    
    def _analyze_response_time(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تحليل Response Time"""
        response_time = metrics["response_time_ms"]
        
        if response_time > 1000:
            return {
                "type": "response_time",
                "severity": "critical",
                "issue": f"Response time is very high: {response_time:.0f}ms",
                "recommendation": "تحسين queries أو نقل DB على volume أسرع",
                "action": "optimize_queries",
                "details": {
                    "current": response_time,
                    "threshold": 1000
                }
            }
        elif response_time > 500:
            return {
                "type": "response_time",
                "severity": "high",
                "issue": f"Response time is high: {response_time:.0f}ms",
                "recommendation": "مراجعة database queries وindexes",
                "action": "review_queries",
                "details": {
                    "current": response_time,
                    "threshold": 500
                }
            }
        
        return None
    
    def _analyze_error_rate(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تحليل Error Rate"""
        error_rate = metrics["error_rate"]
        
        if error_rate > 0.1:  # 10%
            return {
                "type": "error_rate",
                "severity": "critical",
                "issue": f"Error rate is high: {error_rate:.2%}",
                "recommendation": "مراجعة logs وتحديد سبب الأخطاء",
                "action": "review_logs",
                "details": {
                    "current": error_rate,
                    "threshold": 0.1
                }
            }
        elif error_rate > 0.05:  # 5%
            return {
                "type": "error_rate",
                "severity": "high",
                "issue": f"Error rate is elevated: {error_rate:.2%}",
                "recommendation": "مراقبة الأخطاء",
                "action": "monitor_errors",
                "details": {
                    "current": error_rate,
                    "threshold": 0.05
                }
            }
        
        return None
    
    def _analyze_bottlenecks(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تحليل Bottlenecks"""
        bottlenecks = []
        
        # CPU bottleneck
        if metrics["cpu_percent"] > 80 and metrics["response_time_ms"] > 500:
            bottlenecks.append("CPU")
        
        # Memory bottleneck
        if metrics["memory_percent"] > 85:
            bottlenecks.append("Memory")
        
        # Disk bottleneck (يمكن إضافته)
        
        if bottlenecks:
            return {
                "type": "bottleneck",
                "severity": "high",
                "issue": f"Bottlenecks detected: {', '.join(bottlenecks)}",
                "recommendation": f"تحسين {', '.join(bottlenecks)}",
                "action": "optimize_bottlenecks",
                "details": {
                    "bottlenecks": bottlenecks
                }
            }
        
        return None
    
    def _calculate_priority(self, recommendations: List[Dict[str, Any]]) -> str:
        """حساب الأولوية"""
        if not recommendations:
            return "none"
        
        severities = [r.get("severity") for r in recommendations]
        
        if "critical" in severities:
            return "critical"
        elif "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        else:
            return "low"
    
    def get_recommendations_summary(self, hours: int = 24) -> Dict[str, Any]:
        """ملخص التوصيات"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_recs = [
            r for r in self.recommendations_history
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]
        
        type_counts = {}
        severity_counts = {}
        
        for rec in recent_recs:
            for recommendation in rec.get("recommendations", []):
                rec_type = recommendation.get("type", "unknown")
                severity = recommendation.get("severity", "unknown")
                
                type_counts[rec_type] = type_counts.get(rec_type, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_recommendations": len(recent_recs),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "time_range_hours": hours
        }


# Global instance
_performance_tuner: Optional[AIPerformanceTuner] = None


def get_performance_tuner() -> AIPerformanceTuner:
    """الحصول على مثيل ضابط الأداء"""
    global _performance_tuner
    if _performance_tuner is None:
        _performance_tuner = AIPerformanceTuner()
    return _performance_tuner

