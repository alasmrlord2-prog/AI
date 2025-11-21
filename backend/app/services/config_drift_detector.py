"""
Configuration Drift Detector
كاشف تغييرات الـconfig غير المصرح بها
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
from app.utils.logger import log_info, log_warning


class ConfigSnapshot:
    """لقطة من الـconfig"""
    def __init__(self, path: str, content: str, hash_value: str, timestamp: datetime):
        self.path = path
        self.content = content
        self.hash_value = hash_value
        self.timestamp = timestamp
        self.deployment_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "hash": self.hash_value,
            "timestamp": self.timestamp.isoformat(),
            "deployment_id": self.deployment_id
        }


class ConfigDriftDetector:
    """
    كاشف تغييرات الـconfig
    يراقب ملفات الـconfig ويكتشف التغييرات غير المصرح بها
    """
    
    def __init__(self):
        self.snapshots: Dict[str, List[ConfigSnapshot]] = {}  # path -> [snapshots]
        self.monitored_paths: List[str] = []
        self.deployment_snapshots: Dict[str, ConfigSnapshot] = {}  # deployment_id -> snapshot
        self._initialize_default_paths()
    
    def _initialize_default_paths(self):
        """تهيئة المسارات الافتراضية للمراقبة"""
        default_paths = [
            "/etc/nginx/nginx.conf",
            "/etc/nginx/conf.d/",
            "/etc/apache2/",
            "/etc/systemd/system/",
            "/app/config/",
            "/app/.env",
            "/etc/docker/daemon.json",
        ]
        self.monitored_paths.extend(default_paths)
    
    def add_monitored_path(self, path: str):
        """إضافة مسار للمراقبة"""
        if path not in self.monitored_paths:
            self.monitored_paths.append(path)
            log_info(f"Added monitored path: {path}")
    
    def remove_monitored_path(self, path: str):
        """إزالة مسار من المراقبة"""
        if path in self.monitored_paths:
            self.monitored_paths.remove(path)
            log_info(f"Removed monitored path: {path}")
    
    def calculate_hash(self, content: str) -> str:
        """حساب hash للمحتوى"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def read_file(self, path: str) -> Optional[str]:
        """قراءة ملف"""
        try:
            if os.path.isdir(path):
                # إذا كان مجلد، قراءة جميع الملفات
                files_content = []
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                files_content.append(f"{file_path}:\n{f.read()}\n")
                        except:
                            pass
                return "\n".join(files_content)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            log_warning(f"Failed to read {path}: {e}")
            return None
    
    def create_snapshot(self, path: str, deployment_id: Optional[str] = None) -> Optional[ConfigSnapshot]:
        """إنشاء لقطة من الـconfig"""
        content = self.read_file(path)
        if content is None:
            return None
        
        hash_value = self.calculate_hash(content)
        snapshot = ConfigSnapshot(
            path=path,
            content=content,
            hash_value=hash_value,
            timestamp=datetime.now()
        )
        
        if deployment_id:
            snapshot.deployment_id = deployment_id
            self.deployment_snapshots[deployment_id] = snapshot
        
        # إضافة للتاريخ
        if path not in self.snapshots:
            self.snapshots[path] = []
        self.snapshots[path].append(snapshot)
        
        log_info(f"Created snapshot for {path}, hash: {hash_value[:8]}")
        return snapshot
    
    def check_drift(self, path: str, reference_snapshot: Optional[ConfigSnapshot] = None) -> Dict[str, Any]:
        """
        التحقق من تغييرات الـconfig
        
        Args:
            path: مسار الملف
            reference_snapshot: اللقطة المرجعية (إذا لم يتم تحديدها، تستخدم آخر snapshot)
        
        Returns:
            {
                "drift_detected": bool,
                "current_hash": str,
                "reference_hash": str,
                "reference_timestamp": str,
                "drift_details": Dict
            }
        """
        current_content = self.read_file(path)
        if current_content is None:
            return {
                "drift_detected": False,
                "error": "Could not read file"
            }
        
        current_hash = self.calculate_hash(current_content)
        
        # تحديد اللقطة المرجعية
        if reference_snapshot is None:
            if path in self.snapshots and self.snapshots[path]:
                reference_snapshot = self.snapshots[path][-1]
            else:
                return {
                    "drift_detected": False,
                    "error": "No reference snapshot found"
                }
        
        reference_hash = reference_snapshot.hash_value
        
        if current_hash == reference_hash:
            return {
                "drift_detected": False,
                "current_hash": current_hash,
                "reference_hash": reference_hash,
                "reference_timestamp": reference_snapshot.timestamp.isoformat()
            }
        
        # تم اكتشاف تغيير
        drift_details = self._analyze_drift(current_content, reference_snapshot.content)
        
        return {
            "drift_detected": True,
            "current_hash": current_hash,
            "reference_hash": reference_hash,
            "reference_timestamp": reference_snapshot.timestamp.isoformat(),
            "drift_details": drift_details,
            "severity": self._calculate_severity(drift_details)
        }
    
    def _analyze_drift(self, current_content: str, reference_content: str) -> Dict[str, Any]:
        """تحليل التغييرات"""
        current_lines = current_content.split('\n')
        reference_lines = reference_content.split('\n')
        
        added_lines = []
        removed_lines = []
        modified_lines = []
        
        # مقارنة بسيطة (يمكن تحسينها)
        current_set = set(current_lines)
        reference_set = set(reference_lines)
        
        added_lines = list(current_set - reference_set)
        removed_lines = list(reference_set - current_set)
        
        return {
            "added_lines": len(added_lines),
            "removed_lines": len(removed_lines),
            "added_samples": added_lines[:5],  # أول 5 أسطر مضافة
            "removed_samples": removed_lines[:5]  # أول 5 أسطر محذوفة
        }
    
    def _calculate_severity(self, drift_details: Dict[str, Any]) -> str:
        """حساب مستوى الخطورة"""
        total_changes = drift_details.get("added_lines", 0) + drift_details.get("removed_lines", 0)
        
        if total_changes > 50:
            return "critical"
        elif total_changes > 20:
            return "high"
        elif total_changes > 5:
            return "medium"
        else:
            return "low"
    
    def scan_all_monitored(self) -> Dict[str, Any]:
        """فحص جميع المسارات المراقبة"""
        results = {}
        drifts = []
        
        for path in self.monitored_paths:
            if os.path.exists(path):
                result = self.check_drift(path)
                results[path] = result
                
                if result.get("drift_detected"):
                    drifts.append({
                        "path": path,
                        "severity": result.get("severity", "unknown"),
                        "details": result.get("drift_details", {})
                    })
        
        return {
            "total_scanned": len(results),
            "drifts_detected": len(drifts),
            "drifts": drifts,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def restore_from_snapshot(self, path: str, snapshot: Optional[ConfigSnapshot] = None) -> Dict[str, Any]:
        """
        استعادة الـconfig من لقطة
        
        Args:
            path: مسار الملف
            snapshot: اللقطة (إذا لم يتم تحديدها، تستخدم آخر snapshot)
        """
        if snapshot is None:
            if path in self.snapshots and self.snapshots[path]:
                snapshot = self.snapshots[path][-1]
            else:
                return {
                    "success": False,
                    "error": "No snapshot found"
                }
        
        try:
            # إنشاء backup قبل الاستعادة
            backup_path = f"{path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            current_content = self.read_file(path)
            if current_content:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(current_content)
            
            # استعادة المحتوى
            with open(path, 'w', encoding='utf-8') as f:
                f.write(snapshot.content)
            
            log_info(f"Restored {path} from snapshot {snapshot.timestamp}")
            
            return {
                "success": True,
                "path": path,
                "restored_from": snapshot.timestamp.isoformat(),
                "backup_path": backup_path
            }
        except Exception as e:
            log_warning(f"Failed to restore {path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_snapshots(self, path: str) -> List[Dict[str, Any]]:
        """الحصول على جميع اللقطات لمسار"""
        if path not in self.snapshots:
            return []
        
        return [s.to_dict() for s in self.snapshots[path]]


# Global instance
_drift_detector: Optional[ConfigDriftDetector] = None


def get_drift_detector() -> ConfigDriftDetector:
    """الحصول على مثيل كاشف التغييرات"""
    global _drift_detector
    if _drift_detector is None:
        _drift_detector = ConfigDriftDetector()
    return _drift_detector

