"""
Infrastructure Cost Analyzer
محلل تكاليف البنية التحتية
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil
import os
from app.utils.logger import log_info


class CostMetric:
    """مقياس تكلفة"""
    def __init__(
        self,
        resource_type: str,
        resource_name: str,
        cost_per_hour: float,
        usage: float,
        unit: str = "GB"
    ):
        self.resource_type = resource_type  # "cpu", "memory", "storage", "network"
        self.resource_name = resource_name
        self.cost_per_hour = cost_per_hour
        self.usage = usage
        self.unit = unit
        self.timestamp = datetime.now()
    
    def calculate_cost(self, hours: float = 1.0) -> float:
        """حساب التكلفة"""
        return self.cost_per_hour * hours * (self.usage / 100.0 if self.usage <= 100 else 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "cost_per_hour": self.cost_per_hour,
            "usage": self.usage,
            "unit": self.unit,
            "cost_1h": self.calculate_cost(1.0),
            "cost_24h": self.calculate_cost(24.0),
            "cost_30d": self.calculate_cost(24.0 * 30),
            "timestamp": self.timestamp.isoformat()
        }


class CostAnalyzer:
    """
    محلل التكاليف
    يراقب استهلاك الموارد ويحسب التكاليف
    """
    
    def __init__(self):
        # أسعار افتراضية (يمكن تكوينها)
        self.pricing = {
            "cpu": {
                "cost_per_core_per_hour": 0.05,  # $0.05 per CPU core per hour
                "unit": "cores"
            },
            "memory": {
                "cost_per_gb_per_hour": 0.01,  # $0.01 per GB per hour
                "unit": "GB"
            },
            "storage": {
                "cost_per_gb_per_hour": 0.0001,  # $0.0001 per GB per hour
                "unit": "GB"
            },
            "network": {
                "cost_per_gb": 0.09,  # $0.09 per GB transferred
                "unit": "GB"
            }
        }
        self.metrics_history: List[CostMetric] = []
        self.max_history = 10000
    
    def update_pricing(self, resource_type: str, pricing_data: Dict[str, Any]):
        """تحديث الأسعار"""
        self.pricing[resource_type] = pricing_data
        log_info(f"Updated pricing for {resource_type}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """الحصول على مقاييس النظام"""
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # حساب التكاليف
        cpu_cost = self.pricing["cpu"]["cost_per_core_per_hour"] * cpu_count * (cpu_percent / 100.0)
        memory_cost = self.pricing["memory"]["cost_per_gb_per_hour"] * (memory.total / (1024**3)) * (memory.percent / 100.0)
        storage_cost = self.pricing["storage"]["cost_per_gb_per_hour"] * (disk.total / (1024**3))
        
        metrics = {
            "cpu": {
                "cores": cpu_count,
                "usage_percent": cpu_percent,
                "cost_per_hour": cpu_cost,
                "cost_24h": cpu_cost * 24,
                "cost_30d": cpu_cost * 24 * 30
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "used_gb": memory.used / (1024**3),
                "usage_percent": memory.percent,
                "cost_per_hour": memory_cost,
                "cost_24h": memory_cost * 24,
                "cost_30d": memory_cost * 24 * 30
            },
            "storage": {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "usage_percent": (disk.used / disk.total) * 100,
                "cost_per_hour": storage_cost,
                "cost_24h": storage_cost * 24,
                "cost_30d": storage_cost * 24 * 30
            }
        }
        
        total_cost_per_hour = cpu_cost + memory_cost + storage_cost
        metrics["total"] = {
            "cost_per_hour": total_cost_per_hour,
            "cost_24h": total_cost_per_hour * 24,
            "cost_30d": total_cost_per_hour * 24 * 30,
            "cost_per_year": total_cost_per_hour * 24 * 365
        }
        
        return metrics
    
    def analyze_service_cost(self, service_name: str, cpu_usage: float, memory_usage_gb: float) -> Dict[str, Any]:
        """تحليل تكلفة خدمة محددة"""
        cpu_cost = self.pricing["cpu"]["cost_per_core_per_hour"] * cpu_usage
        memory_cost = self.pricing["memory"]["cost_per_gb_per_hour"] * memory_usage_gb
        
        total_cost_per_hour = cpu_cost + memory_cost
        
        return {
            "service": service_name,
            "cpu_usage": cpu_usage,
            "memory_usage_gb": memory_usage_gb,
            "cost_per_hour": total_cost_per_hour,
            "cost_24h": total_cost_per_hour * 24,
            "cost_30d": total_cost_per_hour * 24 * 30,
            "breakdown": {
                "cpu": cpu_cost,
                "memory": memory_cost
            }
        }
    
    def get_cost_summary(self, hours: int = 24) -> Dict[str, Any]:
        """ملخص التكاليف"""
        current_metrics = self.get_system_metrics()
        
        # حساب متوسط التكاليف من التاريخ
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp > cutoff
        ]
        
        avg_costs = {}
        if recent_metrics:
            for resource_type in ["cpu", "memory", "storage"]:
                type_metrics = [m for m in recent_metrics if m.resource_type == resource_type]
                if type_metrics:
                    avg_costs[resource_type] = sum(m.calculate_cost(1.0) for m in type_metrics) / len(type_metrics)
        
        return {
            "current": current_metrics,
            "average": avg_costs,
            "time_range_hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_cost_anomalies(self) -> List[Dict[str, Any]]:
        """كشف الشذوذات في التكاليف"""
        anomalies = []
        
        current_metrics = self.get_system_metrics()
        
        # حساب المتوسط من التاريخ
        if len(self.metrics_history) > 10:
            recent_cpu = [m for m in self.metrics_history[-100:] if m.resource_type == "cpu"]
            recent_memory = [m for m in self.metrics_history[-100:] if m.resource_type == "memory"]
            
            if recent_cpu:
                avg_cpu_cost = sum(m.calculate_cost(1.0) for m in recent_cpu) / len(recent_cpu)
                current_cpu_cost = current_metrics["cpu"]["cost_per_hour"]
                
                if current_cpu_cost > avg_cpu_cost * 2.0:
                    anomalies.append({
                        "type": "cpu_cost_spike",
                        "current": current_cpu_cost,
                        "average": avg_cpu_cost,
                        "increase_percent": ((current_cpu_cost - avg_cpu_cost) / avg_cpu_cost) * 100,
                        "severity": "high"
                    })
            
            if recent_memory:
                avg_memory_cost = sum(m.calculate_cost(1.0) for m in recent_memory) / len(recent_memory)
                current_memory_cost = current_metrics["memory"]["cost_per_hour"]
                
                if current_memory_cost > avg_memory_cost * 2.0:
                    anomalies.append({
                        "type": "memory_cost_spike",
                        "current": current_memory_cost,
                        "average": avg_memory_cost,
                        "increase_percent": ((current_memory_cost - avg_memory_cost) / avg_memory_cost) * 100,
                        "severity": "high"
                    })
        
        return anomalies
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """الحصول على توصيات لتقليل التكاليف"""
        recommendations = []
        current_metrics = self.get_system_metrics()
        
        # توصيات CPU
        if current_metrics["cpu"]["usage_percent"] < 20:
            recommendations.append({
                "type": "cpu",
                "message": "CPU usage is low. Consider downsizing to reduce costs.",
                "potential_savings": current_metrics["cpu"]["cost_30d"] * 0.3,  # 30% savings estimate
                "action": "downsize_cpu"
            })
        
        # توصيات Memory
        if current_metrics["memory"]["usage_percent"] < 30:
            recommendations.append({
                "type": "memory",
                "message": "Memory usage is low. Consider reducing allocated memory.",
                "potential_savings": current_metrics["memory"]["cost_30d"] * 0.2,
                "action": "reduce_memory"
            })
        
        # توصيات Storage
        if current_metrics["storage"]["usage_percent"] < 40:
            recommendations.append({
                "type": "storage",
                "message": "Storage usage is low. Consider using smaller volumes.",
                "potential_savings": current_metrics["storage"]["cost_30d"] * 0.15,
                "action": "reduce_storage"
            })
        
        return recommendations
    
    def record_metrics(self):
        """تسجيل المقاييس الحالية"""
        metrics = self.get_system_metrics()
        
        # تسجيل CPU
        cpu_metric = CostMetric(
            resource_type="cpu",
            resource_name="system",
            cost_per_hour=metrics["cpu"]["cost_per_hour"],
            usage=metrics["cpu"]["usage_percent"],
            unit="percent"
        )
        self.metrics_history.append(cpu_metric)
        
        # تسجيل Memory
        memory_metric = CostMetric(
            resource_type="memory",
            resource_name="system",
            cost_per_hour=metrics["memory"]["cost_per_hour"],
            usage=metrics["memory"]["usage_percent"],
            unit="percent"
        )
        self.metrics_history.append(memory_metric)
        
        # تسجيل Storage
        storage_metric = CostMetric(
            resource_type="storage",
            resource_name="system",
            cost_per_hour=metrics["storage"]["cost_per_hour"],
            usage=metrics["storage"]["usage_percent"],
            unit="percent"
        )
        self.metrics_history.append(storage_metric)
        
        # تقليل التاريخ إذا كان كبيراً
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]


# Global instance
_cost_analyzer: Optional[CostAnalyzer] = None


def get_cost_analyzer() -> CostAnalyzer:
    """الحصول على مثيل محلل التكاليف"""
    global _cost_analyzer
    if _cost_analyzer is None:
        _cost_analyzer = CostAnalyzer()
    return _cost_analyzer

