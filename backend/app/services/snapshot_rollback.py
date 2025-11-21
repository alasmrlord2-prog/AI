"""
Snapshot + Rollback Engine - 100% Local
نظام snapshots وrollback شامل
"""
import os
import shutil
import tarfile
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class Snapshot:
    """لقطة من النظام"""
    def __init__(
        self,
        snapshot_id: str,
        snapshot_type: str,
        target: str,
        timestamp: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.snapshot_id = snapshot_id
        self.snapshot_type = snapshot_type  # "container", "volume", "config", "full"
        self.target = target
        self.timestamp = timestamp
        self.metadata = metadata or {}
        self.path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "type": self.snapshot_type,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "path": self.path
        }


class SnapshotRollbackEngine:
    """
    محرك Snapshots وRollback
    يدعم: Containers, Volumes, Configs, Full System
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.snapshots_dir = Path("snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots: Dict[str, Snapshot] = {}
        self._load_snapshots()
    
    def _load_snapshots(self):
        """تحميل قائمة الـsnapshots"""
        index_file = self.snapshots_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    for snap_data in data.get("snapshots", []):
                        snapshot = Snapshot(
                            snapshot_id=snap_data["snapshot_id"],
                            snapshot_type=snap_data["type"],
                            target=snap_data["target"],
                            timestamp=datetime.fromisoformat(snap_data["timestamp"]),
                            metadata=snap_data.get("metadata", {})
                        )
                        snapshot.path = snap_data.get("path")
                        self.snapshots[snapshot.snapshot_id] = snapshot
            except Exception as e:
                log_warning(f"Error loading snapshots index: {e}")
    
    def _save_index(self):
        """حفظ فهرس الـsnapshots"""
        index_file = self.snapshots_dir / "index.json"
        try:
            data = {
                "snapshots": [s.to_dict() for s in self.snapshots.values()]
            }
            with open(index_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log_error(f"Error saving snapshots index: {e}")
    
    def create_snapshot(
        self,
        snapshot_type: str,
        target: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Snapshot:
        """
        إنشاء snapshot
        
        Args:
            snapshot_type: "container", "volume", "config", "full"
            target: اسم الـcontainer/volume/path
            metadata: معلومات إضافية
        """
        snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{snapshot_type}"
        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            snapshot_type=snapshot_type,
            target=target,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        try:
            if snapshot_type == "container":
                snapshot.path = self._snapshot_container(target, snapshot_id)
            elif snapshot_type == "volume":
                snapshot.path = self._snapshot_volume(target, snapshot_id)
            elif snapshot_type == "config":
                snapshot.path = self._snapshot_config(target, snapshot_id)
            elif snapshot_type == "full":
                snapshot.path = self._snapshot_full(target, snapshot_id)
            else:
                raise ValueError(f"Unknown snapshot type: {snapshot_type}")
            
            self.snapshots[snapshot_id] = snapshot
            self._save_index()
            
            log_info(f"Created snapshot: {snapshot_id} ({snapshot_type})")
            return snapshot
        except Exception as e:
            log_error(f"Error creating snapshot: {e}")
            raise
    
    def _snapshot_container(self, container_name: str, snapshot_id: str) -> str:
        """إنشاء snapshot لـcontainer"""
        import subprocess
        
        # إنشاء مجلد للـsnapshot
        snap_dir = self.snapshots_dir / snapshot_id
        snap_dir.mkdir(parents=True, exist_ok=True)
        
        # تصدير container image
        image_file = snap_dir / "image.tar"
        result = subprocess.run(
            ["docker", "commit", container_name, f"{container_name}:{snapshot_id}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to commit container: {result.stderr}")
        
        # حفظ image
        result = subprocess.run(
            ["docker", "save", f"{container_name}:{snapshot_id}", "-o", str(image_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to save container image: {result.stderr}")
        
        # حفظ metadata
        metadata = {
            "container_name": container_name,
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(snap_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(snap_dir)
    
    def _snapshot_volume(self, volume_name: str, snapshot_id: str) -> str:
        """إنشاء snapshot لـvolume"""
        import subprocess
        
        snap_dir = self.snapshots_dir / snapshot_id
        snap_dir.mkdir(parents=True, exist_ok=True)
        
        # إنشاء container مؤقت لنسخ الـvolume
        temp_container = f"snapshot_temp_{snapshot_id}"
        
        try:
            # تشغيل container مع الـvolume
            result = subprocess.run(
                ["docker", "run", "--name", temp_container, "-v", f"{volume_name}:/data", "busybox", "true"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to create temp container: {result.stderr}")
            
            # نسخ البيانات
            volume_file = snap_dir / "volume.tar"
            result = subprocess.run(
                ["docker", "cp", f"{temp_container}:/data", "-"],
                capture_output=True,
                stdout=open(volume_file, 'wb')
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to copy volume data: {result.stderr}")
        finally:
            # حذف container المؤقت
            subprocess.run(["docker", "rm", temp_container], capture_output=True)
        
        # حفظ metadata
        metadata = {
            "volume_name": volume_name,
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(snap_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(snap_dir)
    
    def _snapshot_config(self, config_path: str, snapshot_id: str) -> str:
        """إنشاء snapshot لـconfig"""
        snap_dir = self.snapshots_dir / snapshot_id
        snap_dir.mkdir(parents=True, exist_ok=True)
        
        if os.path.isfile(config_path):
            # ملف واحد
            shutil.copy2(config_path, snap_dir / os.path.basename(config_path))
        elif os.path.isdir(config_path):
            # مجلد
            shutil.copytree(config_path, snap_dir / os.path.basename(config_path))
        else:
            raise ValueError(f"Config path does not exist: {config_path}")
        
        # حفظ metadata
        metadata = {
            "config_path": config_path,
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(snap_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(snap_dir)
    
    def _snapshot_full(self, target: str, snapshot_id: str) -> str:
        """إنشاء snapshot كامل للنظام"""
        snap_dir = self.snapshots_dir / snapshot_id
        snap_dir.mkdir(parents=True, exist_ok=True)
        
        # نسخ configs مهمة
        important_paths = [
            "/etc/nginx",
            "/etc/apache2",
            "/app/config",
            "/etc/docker"
        ]
        
        for path in important_paths:
            if os.path.exists(path):
                dest = snap_dir / path.lstrip('/').replace('/', '_')
                if os.path.isdir(path):
                    shutil.copytree(path, dest)
                else:
                    shutil.copy2(path, dest)
        
        # حفظ metadata
        metadata = {
            "target": target,
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "type": "full"
        }
        
        with open(snap_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(snap_dir)
    
    def rollback(self, snapshot_id: str, force: bool = False) -> Dict[str, Any]:
        """
        استعادة من snapshot
        
        Args:
            snapshot_id: معرف الـsnapshot
            force: فرض الاستعادة حتى لو كان هناك تغييرات
        """
        if snapshot_id not in self.snapshots:
            return {
                "success": False,
                "error": f"Snapshot {snapshot_id} not found"
            }
        
        snapshot = self.snapshots[snapshot_id]
        
        try:
            if snapshot.snapshot_type == "container":
                return self._rollback_container(snapshot, force)
            elif snapshot.snapshot_type == "volume":
                return self._rollback_volume(snapshot, force)
            elif snapshot.snapshot_type == "config":
                return self._rollback_config(snapshot, force)
            elif snapshot.snapshot_type == "full":
                return self._rollback_full(snapshot, force)
            else:
                return {
                    "success": False,
                    "error": f"Unknown snapshot type: {snapshot.snapshot_type}"
                }
        except Exception as e:
            log_error(f"Error rolling back snapshot {snapshot_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _rollback_container(self, snapshot: Snapshot, force: bool) -> Dict[str, Any]:
        """استعادة container"""
        import subprocess
        
        # تحميل image
        image_file = Path(snapshot.path) / "image.tar"
        if not image_file.exists():
            return {"success": False, "error": "Snapshot image file not found"}
        
        result = subprocess.run(
            ["docker", "load", "-i", str(image_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"success": False, "error": f"Failed to load image: {result.stderr}"}
        
        # إيقاف container الحالي إذا كان يعمل
        result = subprocess.run(
            ["docker", "stop", snapshot.target],
            capture_output=True
        )
        
        # حذف container القديم
        subprocess.run(["docker", "rm", snapshot.target], capture_output=True)
        
        # إنشاء container جديد من الـsnapshot
        result = subprocess.run(
            ["docker", "run", "-d", "--name", snapshot.target, f"{snapshot.target}:{snapshot.snapshot_id}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"success": False, "error": f"Failed to create container: {result.stderr}"}
        
        log_info(f"Rolled back container {snapshot.target} from snapshot {snapshot.snapshot_id}")
        return {"success": True, "message": f"Container {snapshot.target} rolled back"}
    
    def _rollback_volume(self, snapshot: Snapshot, force: bool) -> Dict[str, Any]:
        """استعادة volume"""
        import subprocess
        
        volume_file = Path(snapshot.path) / "volume.tar"
        if not volume_file.exists():
            return {"success": False, "error": "Snapshot volume file not found"}
        
        # إنشاء container مؤقت
        temp_container = f"rollback_temp_{snapshot.snapshot_id}"
        
        try:
            # تشغيل container مع volume
            result = subprocess.run(
                ["docker", "run", "--name", temp_container, "-v", f"{snapshot.target}:/data", "busybox", "sh", "-c", "rm -rf /data/*"],
                capture_output=True,
                text=True
            )
            
            # استخراج البيانات
            result = subprocess.run(
                ["tar", "-xf", str(volume_file), "-C", "/"],
                capture_output=True
            )
            
            log_info(f"Rolled back volume {snapshot.target} from snapshot {snapshot.snapshot_id}")
            return {"success": True, "message": f"Volume {snapshot.target} rolled back"}
        finally:
            subprocess.run(["docker", "rm", temp_container], capture_output=True)
    
    def _rollback_config(self, snapshot: Snapshot, force: bool) -> Dict[str, Any]:
        """استعادة config"""
        snap_dir = Path(snapshot.path)
        
        # البحث عن الملفات المحفوظة
        config_files = list(snap_dir.glob("*"))
        config_files = [f for f in config_files if f.name != "metadata.json"]
        
        if not config_files:
            return {"success": False, "error": "No config files found in snapshot"}
        
        # نسخ الملفات
        for file_path in config_files:
            dest = snapshot.target
            if os.path.isdir(dest):
                dest = os.path.join(dest, file_path.name)
            
            # إنشاء backup قبل الاستعادة
            if os.path.exists(dest) and not force:
                backup_path = f"{dest}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(dest, backup_path)
            
            if file_path.is_file():
                shutil.copy2(file_path, dest)
            elif file_path.is_dir():
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(file_path, dest)
        
        log_info(f"Rolled back config {snapshot.target} from snapshot {snapshot.snapshot_id}")
        return {"success": True, "message": f"Config {snapshot.target} rolled back"}
    
    def _rollback_full(self, snapshot: Snapshot, force: bool) -> Dict[str, Any]:
        """استعادة كاملة"""
        # استعادة configs
        snap_dir = Path(snapshot.path)
        
        for item in snap_dir.iterdir():
            if item.name == "metadata.json":
                continue
            
            # استخراج المسار الأصلي من الاسم
            original_path = "/" + item.name.replace('_', '/')
            
            if os.path.exists(original_path):
                if force or os.path.isdir(original_path):
                    shutil.rmtree(original_path)
                else:
                    os.remove(original_path)
            
            if item.is_dir():
                shutil.copytree(item, original_path)
            else:
                shutil.copy2(item, original_path)
        
        log_info(f"Rolled back full system from snapshot {snapshot.snapshot_id}")
        return {"success": True, "message": "Full system rolled back"}
    
    def list_snapshots(self, snapshot_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """قائمة الـsnapshots"""
        snapshots = list(self.snapshots.values())
        
        if snapshot_type:
            snapshots = [s for s in snapshots if s.snapshot_type == snapshot_type]
        
        # ترتيب حسب الوقت
        snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [s.to_dict() for s in snapshots]
    
    def delete_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """حذف snapshot"""
        if snapshot_id not in self.snapshots:
            return {"success": False, "error": "Snapshot not found"}
        
        snapshot = self.snapshots[snapshot_id]
        
        # حذف الملفات
        if snapshot.path and os.path.exists(snapshot.path):
            shutil.rmtree(snapshot.path)
        
        # حذف من الفهرس
        del self.snapshots[snapshot_id]
        self._save_index()
        
        log_info(f"Deleted snapshot {snapshot_id}")
        return {"success": True, "message": f"Snapshot {snapshot_id} deleted"}


# Global instance
_snapshot_engine: Optional[SnapshotRollbackEngine] = None


def get_snapshot_engine() -> SnapshotRollbackEngine:
    """الحصول على مثيل محرك Snapshots"""
    global _snapshot_engine
    if _snapshot_engine is None:
        _snapshot_engine = SnapshotRollbackEngine()
    return _snapshot_engine

