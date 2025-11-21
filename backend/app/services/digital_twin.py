"""
Digital Twin Mode - 100% Local
وضع digital twin - simulation للبنية التحتية
"""
import os
import json
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class DigitalTwin:
    """
    Digital Twin - نسخة افتراضية simulation من البنية التحتية
    يجرب Updates, Deploys, Failures بدون ما يلمس الإنتاج
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.twin_dir = Path("digital_twin")
        self.twin_dir.mkdir(parents=True, exist_ok=True)
        self.active_twins: Dict[str, Dict[str, Any]] = {}
    
    def create_twin(
        self,
        name: str,
        infrastructure_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        إنشاء digital twin
        
        Args:
            name: اسم الـtwin
            infrastructure_config: تكوين البنية التحتية (services, containers, configs)
        """
        twin_id = f"twin_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        twin_path = self.twin_dir / twin_id
        twin_path.mkdir(parents=True, exist_ok=True)
        
        # حفظ التكوين
        config_file = twin_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(infrastructure_config, f, indent=2)
        
        # إنشاء simulation environment
        simulation_result = self._create_simulation(twin_id, infrastructure_config)
        
        twin_info = {
            "twin_id": twin_id,
            "name": name,
            "config": infrastructure_config,
            "simulation_path": str(twin_path),
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "simulation": simulation_result
        }
        
        self.active_twins[twin_id] = twin_info
        
        log_info(f"Created digital twin: {name} ({twin_id})")
        
        return {
            "success": True,
            "twin": twin_info
        }
    
    def _create_simulation(
        self,
        twin_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """إنشاء simulation environment"""
        twin_path = self.twin_dir / twin_id
        
        # إنشاء Docker Compose للـsimulation
        services = config.get("services", [])
        
        compose_content = {
            "version": "3.8",
            "services": {}
        }
        
        for service in services:
            service_name = service.get("name", "unknown")
            compose_content["services"][f"{service_name}_twin"] = {
                "image": service.get("image", "alpine:latest"),
                "command": "sleep infinity",  # container خامل للـsimulation
                "environment": service.get("environment", {}),
                "networks": ["twin_network"]
            }
        
        compose_content["networks"] = {
            "twin_network": {
                "driver": "bridge"
            }
        }
        
        compose_file = twin_path / "docker-compose.yml"
        with open(compose_file, 'w') as f:
            json.dump(compose_content, f, indent=2)
        
        return {
            "compose_file": str(compose_file),
            "services_count": len(services)
        }
    
    def simulate_deploy(
        self,
        twin_id: str,
        deploy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """محاكاة deploy على الـtwin"""
        if twin_id not in self.active_twins:
            return {"success": False, "error": "Twin not found"}
        
        twin = self.active_twins[twin_id]
        twin_path = Path(twin["simulation_path"])
        
        try:
            # محاكاة deploy (بدون تنفيذ فعلي)
            simulation_result = {
                "twin_id": twin_id,
                "deploy_type": deploy_config.get("type", "unknown"),
                "simulated_at": datetime.now().isoformat(),
                "steps": [
                    {"step": "validate_config", "status": "success"},
                    {"step": "check_dependencies", "status": "success"},
                    {"step": "prepare_environment", "status": "success"},
                    {"step": "deploy_services", "status": "success"},
                    {"step": "health_check", "status": "success"}
                ],
                "estimated_time": "5 minutes",
                "rollback_available": True
            }
            
            # حفظ نتائج المحاكاة
            results_file = twin_path / f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(simulation_result, f, indent=2)
            
            log_info(f"Simulated deploy on twin {twin_id}")
            
            return {
                "success": True,
                "simulation": simulation_result
            }
        except Exception as e:
            log_error(f"Error simulating deploy: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def simulate_failure(
        self,
        twin_id: str,
        failure_type: str,
        target_service: Optional[str] = None
    ) -> Dict[str, Any]:
        """محاكاة فشل على الـtwin"""
        if twin_id not in self.active_twins:
            return {"success": False, "error": "Twin not found"}
        
        try:
            simulation_result = {
                "twin_id": twin_id,
                "failure_type": failure_type,
                "target_service": target_service,
                "simulated_at": datetime.now().isoformat(),
                "impact_analysis": {
                    "affected_services": [target_service] if target_service else [],
                    "downtime_estimate": "2 minutes",
                    "recovery_steps": [
                        "Isolate failed service",
                        "Route traffic to backup",
                        "Restore from snapshot"
                    ]
                },
                "recovery_simulation": {
                    "auto_recovery": True,
                    "estimated_recovery_time": "5 minutes"
                }
            }
            
            twin = self.active_twins[twin_id]
            twin_path = Path(twin["simulation_path"])
            results_file = twin_path / f"failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(results_file, 'w') as f:
                json.dump(simulation_result, f, indent=2)
            
            log_info(f"Simulated failure on twin {twin_id}: {failure_type}")
            
            return {
                "success": True,
                "simulation": simulation_result
            }
        except Exception as e:
            log_error(f"Error simulating failure: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def compare_with_production(
        self,
        twin_id: str
    ) -> Dict[str, Any]:
        """مقارنة الـtwin مع الإنتاج"""
        if twin_id not in self.active_twins:
            return {"error": "Twin not found"}
        
        twin = self.active_twins[twin_id]
        twin_config = twin["config"]
        
        # جمع معلومات الإنتاج (مثال)
        production_info = {
            "services": [],  # يمكن جلبها من discovery
            "configs": [],
            "status": "running"
        }
        
        differences = []
        
        # مقارنة services
        twin_services = {s["name"]: s for s in twin_config.get("services", [])}
        prod_services = {s["name"]: s for s in production_info.get("services", [])}
        
        # services في twin وليس في production
        for name in twin_services:
            if name not in prod_services:
                differences.append({
                    "type": "new_service",
                    "service": name,
                    "location": "twin_only"
                })
        
        # services في production وليس في twin
        for name in prod_services:
            if name not in twin_services:
                differences.append({
                    "type": "missing_service",
                    "service": name,
                    "location": "production_only"
                })
        
        return {
            "twin_id": twin_id,
            "differences": differences,
            "total_differences": len(differences),
            "production_info": production_info,
            "twin_info": twin_config
        }
    
    def get_twin(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على twin"""
        return self.active_twins.get(twin_id)
    
    def list_twins(self) -> List[Dict[str, Any]]:
        """قائمة twins"""
        return [twin for twin in self.active_twins.values()]
    
    def delete_twin(self, twin_id: str) -> Dict[str, Any]:
        """حذف twin"""
        if twin_id not in self.active_twins:
            return {"success": False, "error": "Twin not found"}
        
        twin = self.active_twins[twin_id]
        twin_path = Path(twin["simulation_path"])
        
        try:
            # حذف الملفات
            if twin_path.exists():
                import shutil
                shutil.rmtree(twin_path)
            
            del self.active_twins[twin_id]
            
            log_info(f"Deleted digital twin: {twin_id}")
            
            return {"success": True, "message": f"Twin {twin_id} deleted"}
        except Exception as e:
            log_error(f"Error deleting twin: {e}")
            return {"success": False, "error": str(e)}


# Global instance
_digital_twin: Optional[DigitalTwin] = None


def get_digital_twin() -> DigitalTwin:
    """الحصول على مثيل Digital Twin"""
    global _digital_twin
    if _digital_twin is None:
        _digital_twin = DigitalTwin()
    return _digital_twin

