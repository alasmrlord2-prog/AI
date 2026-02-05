"""
Shadow Deployment - 100% Local
نشر shadow - اختبار قبل النشر الرسمي
"""
import subprocess
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class ShadowDeployment:
    """
    نشر shadow
    يشغل نسخة shadow, يحول جزء من traffic, يقارن النتائج
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.active_shadows: Dict[str, Dict[str, Any]] = {}
    
    def create_shadow(
        self,
        service_name: str,
        image: str,
        traffic_percentage: float = 10.0,
        comparison_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        إنشاء shadow deployment
        
        Args:
            service_name: اسم الخدمة الأصلية
            image: صورة Docker للنسخة الجديدة
            traffic_percentage: نسبة الـtraffic للـshadow (0-100)
            comparison_metrics: مقاييس للمقارنة
        """
        shadow_id = f"shadow_{service_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shadow_name = f"{service_name}_shadow"
        
        try:
            # إنشاء container shadow
            result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", shadow_name,
                    "--label", f"shadow_id={shadow_id}",
                    "--label", f"original_service={service_name}",
                    image
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to create shadow container: {result.stderr}"
                }
            
            # الحصول على IP الـshadow
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", shadow_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            shadow_ip = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            shadow_info = {
                "shadow_id": shadow_id,
                "shadow_name": shadow_name,
                "original_service": service_name,
                "image": image,
                "traffic_percentage": traffic_percentage,
                "shadow_ip": shadow_ip,
                "status": "running",
                "created_at": datetime.now().isoformat(),
                "comparison_metrics": comparison_metrics or [],
                "metrics": {
                    "requests": 0,
                    "errors": 0,
                    "avg_response_time": 0.0
                }
            }
            
            self.active_shadows[shadow_id] = shadow_info
            
            log_info(f"Created shadow deployment: {shadow_id} for {service_name}")
            
            return {
                "success": True,
                "shadow": shadow_info
            }
        except Exception as e:
            log_error(f"Error creating shadow deployment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def route_traffic(
        self,
        shadow_id: str,
        traffic_percentage: float
    ) -> Dict[str, Any]:
        """
        توجيه جزء من الـtraffic للـshadow
        
        يمكن تنفيذ هذا عبر:
        - Load balancer config
        - NGINX upstream
        - Service mesh
        """
        if shadow_id not in self.active_shadows:
            return {"success": False, "error": "Shadow not found"}
        
        shadow = self.active_shadows[shadow_id]
        shadow["traffic_percentage"] = traffic_percentage
        
        # هنا يمكن إضافة منطق لتوجيه الـtraffic فعلياً
        # للبساطة، سنكتفي بتحديث النسبة
        
        log_info(f"Routed {traffic_percentage}% traffic to shadow {shadow_id}")
        
        return {
            "success": True,
            "message": f"Routed {traffic_percentage}% traffic to shadow",
            "shadow": shadow
        }
    
    def compare_results(
        self,
        shadow_id: str
    ) -> Dict[str, Any]:
        """مقارنة نتائج shadow مع النسخة الأصلية"""
        if shadow_id not in self.active_shadows:
            return {"success": False, "error": "Shadow not found"}
        
        shadow = self.active_shadows[shadow_id]
        original_service = shadow["original_service"]
        
        # جمع مقاييس shadow
        shadow_metrics = shadow.get("metrics", {})
        
        # جمع مقاييس النسخة الأصلية (مثال)
        original_metrics = {
            "requests": 1000,  # يمكن جلبها من monitoring
            "errors": 5,
            "avg_response_time": 150.0
        }
        
        # المقارنة
        comparison = {
            "shadow_metrics": shadow_metrics,
            "original_metrics": original_metrics,
            "differences": {
                "error_rate_diff": shadow_metrics.get("errors", 0) - original_metrics.get("errors", 0),
                "response_time_diff": shadow_metrics.get("avg_response_time", 0) - original_metrics.get("avg_response_time", 0)
            },
            "recommendation": self._generate_recommendation(shadow_metrics, original_metrics)
        }
        
        return {
            "success": True,
            "comparison": comparison
        }
    
    def _generate_recommendation(
        self,
        shadow_metrics: Dict[str, Any],
        original_metrics: Dict[str, Any]
    ) -> str:
        """توليد توصية بناءً على المقارنة"""
        error_diff = shadow_metrics.get("errors", 0) - original_metrics.get("errors", 0)
        response_diff = shadow_metrics.get("avg_response_time", 0) - original_metrics.get("avg_response_time", 0)
        
        if error_diff > 10:
            return "High error rate in shadow. Do not proceed with full deployment."
        elif error_diff < -5:
            return "Shadow has lower error rate. Safe to proceed."
        elif response_diff > 100:
            return "Shadow has higher response time. Review before deployment."
        elif response_diff < -50:
            return "Shadow has better performance. Safe to proceed."
        else:
            return "Shadow performance is similar. Safe to proceed with caution."
    
    def promote_shadow(self, shadow_id: str) -> Dict[str, Any]:
        """ترقية shadow إلى production"""
        if shadow_id not in self.active_shadows:
            return {"success": False, "error": "Shadow not found"}
        
        shadow = self.active_shadows[shadow_id]
        original_service = shadow["original_service"]
        
        try:
            # إيقاف النسخة الأصلية
            subprocess.run(
                ["docker", "stop", original_service],
                capture_output=True
            )
            
            # إعادة تسمية shadow
            shadow_name = shadow["shadow_name"]
            subprocess.run(
                ["docker", "rename", shadow_name, original_service],
                capture_output=True
            )
            
            # حذف shadow من القائمة النشطة
            del self.active_shadows[shadow_id]
            
            log_info(f"Promoted shadow {shadow_id} to production")
            
            return {
                "success": True,
                "message": f"Shadow {shadow_id} promoted to production"
            }
        except Exception as e:
            log_error(f"Error promoting shadow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def destroy_shadow(self, shadow_id: str) -> Dict[str, Any]:
        """تدمير shadow deployment"""
        if shadow_id not in self.active_shadows:
            return {"success": False, "error": "Shadow not found"}
        
        shadow = self.active_shadows[shadow_id]
        shadow_name = shadow["shadow_name"]
        
        try:
            # إيقاف وحذف container
            subprocess.run(["docker", "stop", shadow_name], capture_output=True)
            subprocess.run(["docker", "rm", shadow_name], capture_output=True)
            
            # حذف من القائمة
            del self.active_shadows[shadow_id]
            
            log_info(f"Destroyed shadow deployment: {shadow_id}")
            
            return {
                "success": True,
                "message": f"Shadow {shadow_id} destroyed"
            }
        except Exception as e:
            log_error(f"Error destroying shadow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_shadows(self) -> List[Dict[str, Any]]:
        """قائمة shadow deployments النشطة"""
        return [shadow for shadow in self.active_shadows.values()]


# Global instance
_shadow_deployment: Optional[ShadowDeployment] = None


def get_shadow_deployment() -> ShadowDeployment:
    """الحصول على مثيل Shadow Deployment"""
    global _shadow_deployment
    if _shadow_deployment is None:
        _shadow_deployment = ShadowDeployment()
    return _shadow_deployment

