"""Backup Service - Database and Docker volumes backup."""
import subprocess
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import shutil
from enum import Enum


class BackupType(Enum):
    """Backup types."""
    DATABASE = "database"
    DOCKER_VOLUME = "docker_volume"
    FILESYSTEM = "filesystem"


class BackupService:
    """Backup service for databases and Docker volumes."""
    
    def __init__(self, backup_dir: str = "/data/backups"):
        """Initialize backup service."""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_metadata_file = self.backup_dir / "backups.json"
        self.backups = self._load_metadata()
    
    def _load_metadata(self) -> List[Dict]:
        """Load backup metadata."""
        if self.backup_metadata_file.exists():
            try:
                with open(self.backup_metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_metadata(self):
        """Save backup metadata."""
        with open(self.backup_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.backups, f, indent=2, ensure_ascii=False)
    
    def backup_postgresql(
        self,
        db_name: str,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: Optional[str] = None
    ) -> Dict:
        """Backup PostgreSQL database."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"postgresql_{db_name}_{timestamp}.sql"
            
            # Set password in environment
            env = os.environ.copy()
            if password:
                env["PGPASSWORD"] = password
            
            # Run pg_dump
            result = subprocess.run(
                [
                    "pg_dump",
                    "-h", host,
                    "-p", str(port),
                    "-U", user,
                    "-d", db_name,
                    "-f", str(backup_file)
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            # Calculate MD5
            md5_hash = self._calculate_md5(backup_file)
            
            # Save metadata
            backup_info = {
                "id": f"pg_{db_name}_{timestamp}",
                "type": BackupType.DATABASE.value,
                "database_type": "postgresql",
                "database_name": db_name,
                "file": str(backup_file),
                "size": backup_file.stat().st_size,
                "md5": md5_hash,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            self.backups.append(backup_info)
            self._save_metadata()
            
            return {
                "success": True,
                "backup": backup_info
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Backup timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def backup_mysql(
        self,
        db_name: str,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: Optional[str] = None
    ) -> Dict:
        """Backup MySQL database."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"mysql_{db_name}_{timestamp}.sql"
            
            # Build mysqldump command
            cmd = [
                "mysqldump",
                "-h", host,
                "-P", str(port),
                "-u", user,
                db_name
            ]
            
            if password:
                cmd.append(f"-p{password}")
            
            # Run mysqldump
            with open(backup_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=600
                )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr.decode() if isinstance(result.stderr, bytes) else result.stderr
                }
            
            # Calculate MD5
            md5_hash = self._calculate_md5(backup_file)
            
            # Save metadata
            backup_info = {
                "id": f"mysql_{db_name}_{timestamp}",
                "type": BackupType.DATABASE.value,
                "database_type": "mysql",
                "database_name": db_name,
                "file": str(backup_file),
                "size": backup_file.stat().st_size,
                "md5": md5_hash,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            self.backups.append(backup_info)
            self._save_metadata()
            
            return {
                "success": True,
                "backup": backup_info
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Backup timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def backup_docker_volume(
        self,
        volume_name: str
    ) -> Dict:
        """Backup Docker volume."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"docker_volume_{volume_name}_{timestamp}.tar.gz"
            
            # Create backup using docker run
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{volume_name}:/data",
                    "-v", f"{self.backup_dir}:/backup",
                    "alpine",
                    "tar", "czf", f"/backup/{backup_file.name}", "-C", "/data", "."
                ],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            # Calculate MD5
            md5_hash = self._calculate_md5(backup_file)
            
            # Save metadata
            backup_info = {
                "id": f"vol_{volume_name}_{timestamp}",
                "type": BackupType.DOCKER_VOLUME.value,
                "volume_name": volume_name,
                "file": str(backup_file),
                "size": backup_file.stat().st_size,
                "md5": md5_hash,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            self.backups.append(backup_info)
            self._save_metadata()
            
            return {
                "success": True,
                "backup": backup_info
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Backup timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def backup_system(self) -> Dict:
        """Create a general system backup (snapshot of current state)."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"system_backup_{timestamp}.tar.gz"
            
            # Create a snapshot of important system directories
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                snapshot_dir = Path(tmpdir) / "snapshot"
                snapshot_dir.mkdir()
                
                # Backup important directories (if they exist)
                important_dirs = [
                    "/home/ai/ai-agent/backend/memory",
                    "/home/ai/ai-agent/backend/database",
                ]
                
                for dir_path in important_dirs:
                    src = Path(dir_path)
                    if src.exists():
                        dst = snapshot_dir / src.name
                        if src.is_dir():
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src, dst)
                
                # Create tar archive
                result = subprocess.run(
                    [
                        "tar", "czf", str(backup_file),
                        "-C", str(snapshot_dir.parent),
                        "snapshot"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": result.stderr or "Failed to create backup archive"
                    }
            
            # Calculate MD5
            md5_hash = self._calculate_md5(backup_file)
            
            # Save metadata
            backup_info = {
                "id": f"system_{timestamp}",
                "type": BackupType.FILESYSTEM.value,
                "file": str(backup_file),
                "size": backup_file.stat().st_size,
                "md5": md5_hash,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            self.backups.append(backup_info)
            self._save_metadata()
            
            return {
                "success": True,
                "backup": backup_info
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Backup timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def verify_backup(self, backup_id: str) -> Dict:
        """Verify backup integrity."""
        backup = next((b for b in self.backups if b["id"] == backup_id), None)
        
        if not backup:
            return {
                "success": False,
                "error": "Backup not found"
            }
        
        backup_file = Path(backup["file"])
        
        if not backup_file.exists():
            return {
                "success": False,
                "error": "Backup file not found"
            }
        
        # Recalculate MD5
        current_md5 = self._calculate_md5(backup_file)
        
        return {
            "success": True,
            "backup_id": backup_id,
            "original_md5": backup.get("md5"),
            "current_md5": current_md5,
            "match": current_md5 == backup.get("md5"),
            "file_exists": True,
            "file_size": backup_file.stat().st_size
        }
    
    def list_backups(
        self,
        backup_type: Optional[BackupType] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List backups."""
        backups = self.backups.copy()
        
        if backup_type:
            backups = [b for b in backups if b.get("type") == backup_type.value]
        
        # Sort by timestamp descending
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return backups[:limit]
    
    def delete_backup(self, backup_id: str) -> Dict:
        """Delete a backup."""
        backup = next((b for b in self.backups if b["id"] == backup_id), None)
        
        if not backup:
            return {
                "success": False,
                "error": "Backup not found"
            }
        
        # Delete file
        backup_file = Path(backup["file"])
        if backup_file.exists():
            backup_file.unlink()
        
        # Remove from metadata
        self.backups = [b for b in self.backups if b["id"] != backup_id]
        self._save_metadata()
        
        return {
            "success": True,
            "message": f"Backup {backup_id} deleted"
        }


# Global instance
backup_service = BackupService()

