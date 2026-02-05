"""
Unified Secret Management - 100% Local
إدارة الأسرار الموحدة - محلي بالكامل
"""
import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class Secret:
    """سر محفوظ"""
    def __init__(
        self,
        secret_id: str,
        name: str,
        secret_type: str,
        encrypted_value: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.secret_id = secret_id
        self.name = name
        self.secret_type = secret_type  # "api_key", "password", "token", "certificate"
        self.encrypted_value = encrypted_value
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_rotated = datetime.now()
        self.access_count = 0
        self.last_accessed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "secret_id": self.secret_id,
            "name": self.name,
            "type": self.secret_type,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_rotated": self.last_rotated.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }


class UnifiedSecretManager:
    """
    مدير الأسرار الموحد - محلي 100%
    - Encryption at rest
    - Auto rotation
    - Per-service access policy
    - Audit logging
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.vault_dir = Path("vault")
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        
        # مفتاح التشفير (من environment أو ملف)
        self.master_key = self._get_or_create_master_key()
        self.cipher = Fernet(self.master_key)
        
        self.secrets: Dict[str, Secret] = {}
        self.access_policies: Dict[str, List[str]] = {}  # service -> [secret_ids]
        self.rotation_schedules: Dict[str, int] = {}  # secret_id -> days
        self.audit_log: List[Dict[str, Any]] = []
        self.max_audit_log = 10000
        
        self._load_secrets()
    
    def _get_or_create_master_key(self) -> bytes:
        """الحصول على أو إنشاء master key"""
        key_file = self.vault_dir / "master.key"
        
        if key_file.exists():
            # قراءة المفتاح الموجود
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # إنشاء مفتاح جديد
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # حماية الملف
            os.chmod(key_file, 0o600)
            log_info("Created new master key for secret vault")
            return key
    
    def _load_secrets(self):
        """تحميل الأسرار من الملفات"""
        secrets_file = self.vault_dir / "secrets.json"
        if not secrets_file.exists():
            return
        
        try:
            with open(secrets_file, 'r') as f:
                data = json.load(f)
                
                for secret_data in data.get("secrets", []):
                    secret = Secret(
                        secret_id=secret_data["secret_id"],
                        name=secret_data["name"],
                        secret_type=secret_data["type"],
                        encrypted_value=base64.b64decode(secret_data["encrypted_value"]),
                        metadata=secret_data.get("metadata", {})
                    )
                    secret.created_at = datetime.fromisoformat(secret_data.get("created_at", datetime.now().isoformat()))
                    secret.last_rotated = datetime.fromisoformat(secret_data.get("last_rotated", datetime.now().isoformat()))
                    secret.access_count = secret_data.get("access_count", 0)
                    if secret_data.get("last_accessed"):
                        secret.last_accessed = datetime.fromisoformat(secret_data["last_accessed"])
                    
                    self.secrets[secret.secret_id] = secret
                
                self.access_policies = data.get("access_policies", {})
                self.rotation_schedules = data.get("rotation_schedules", {})
                
            log_info(f"Loaded {len(self.secrets)} secrets from vault")
        except Exception as e:
            log_error(f"Error loading secrets: {e}")
    
    def _save_secrets(self):
        """حفظ الأسرار في الملفات"""
        secrets_file = self.vault_dir / "secrets.json"
        
        try:
            data = {
                "secrets": [
                    {
                        **secret.to_dict(),
                        "encrypted_value": base64.b64encode(secret.encrypted_value).decode()
                    }
                    for secret in self.secrets.values()
                ],
                "access_policies": self.access_policies,
                "rotation_schedules": self.rotation_schedules
            }
            
            with open(secrets_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # حماية الملف
            os.chmod(secrets_file, 0o600)
        except Exception as e:
            log_error(f"Error saving secrets: {e}")
    
    def _log_access(self, secret_id: str, service: str, action: str, success: bool):
        """تسجيل وصول"""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "secret_id": secret_id,
            "service": service,
            "action": action,
            "success": success
        })
        
        # حفظ فقط آخر N
        if len(self.audit_log) > self.max_audit_log:
            self.audit_log = self.audit_log[-self.max_audit_log:]
    
    def store_secret(
        self,
        name: str,
        value: str,
        secret_type: str = "api_key",
        metadata: Optional[Dict[str, Any]] = None,
        rotation_days: Optional[int] = None
    ) -> Secret:
        """تخزين سر جديد"""
        secret_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # تشفير القيمة
        encrypted_value = self.cipher.encrypt(value.encode())
        
        secret = Secret(
            secret_id=secret_id,
            name=name,
            secret_type=secret_type,
            encrypted_value=encrypted_value,
            metadata=metadata or {}
        )
        
        self.secrets[secret_id] = secret
        
        if rotation_days:
            self.rotation_schedules[secret_id] = rotation_days
        
        self._save_secrets()
        
        self._log_access(secret_id, "system", "store", True)
        log_info(f"Stored secret: {name} ({secret_id})")
        
        return secret
    
    def get_secret(
        self,
        secret_id: str,
        service: str = "unknown"
    ) -> Optional[str]:
        """الحصول على سر (فك التشفير)"""
        if secret_id not in self.secrets:
            self._log_access(secret_id, service, "get", False)
            return None
        
        # التحقق من الصلاحيات
        if not self._check_access(secret_id, service):
            self._log_access(secret_id, service, "get", False)
            log_warning(f"Access denied: service {service} tried to access secret {secret_id}")
            return None
        
        secret = self.secrets[secret_id]
        
        try:
            # فك التشفير
            decrypted_value = self.cipher.decrypt(secret.encrypted_value).decode()
            
            # تحديث الإحصائيات
            secret.access_count += 1
            secret.last_accessed = datetime.now()
            self._save_secrets()
            
            self._log_access(secret_id, service, "get", True)
            
            return decrypted_value
        except Exception as e:
            log_error(f"Error decrypting secret {secret_id}: {e}")
            self._log_access(secret_id, service, "get", False)
            return None
    
    def _check_access(self, secret_id: str, service: str) -> bool:
        """التحقق من صلاحيات الوصول"""
        # إذا لم تكن هناك سياسات محددة، السماح للجميع (للتبسيط)
        if not self.access_policies:
            return True
        
        # التحقق من أن الخدمة مسموح لها
        allowed_secrets = self.access_policies.get(service, [])
        if "*" in allowed_secrets or secret_id in allowed_secrets:
            return True
        
        return False
    
    def set_access_policy(self, service: str, secret_ids: List[str]):
        """تعيين سياسة وصول لخدمة"""
        self.access_policies[service] = secret_ids
        self._save_secrets()
        log_info(f"Set access policy for service {service}: {len(secret_ids)} secrets")
    
    def rotate_secret(self, secret_id: str, new_value: str) -> Dict[str, Any]:
        """تدوير سر (تغيير القيمة)"""
        if secret_id not in self.secrets:
            return {"success": False, "error": "Secret not found"}
        
        secret = self.secrets[secret_id]
        
        # تشفير القيمة الجديدة
        encrypted_value = self.cipher.encrypt(new_value.encode())
        secret.encrypted_value = encrypted_value
        secret.last_rotated = datetime.now()
        
        self._save_secrets()
        
        self._log_access(secret_id, "system", "rotate", True)
        log_info(f"Rotated secret: {secret.name} ({secret_id})")
        
        return {"success": True, "message": f"Secret {secret.name} rotated"}
    
    def auto_rotate_secrets(self) -> Dict[str, Any]:
        """تدوير تلقائي للأسرار"""
        rotated = []
        
        for secret_id, days in self.rotation_schedules.items():
            if secret_id not in self.secrets:
                continue
            
            secret = self.secrets[secret_id]
            days_since_rotation = (datetime.now() - secret.last_rotated).days
            
            if days_since_rotation >= days:
                # حان وقت التدوير (لكن نحتاج قيمة جديدة - هذا مثال)
                log_info(f"Secret {secret.name} needs rotation (scheduled every {days} days)")
                rotated.append(secret_id)
        
        return {
            "secrets_needing_rotation": rotated,
            "count": len(rotated)
        }
    
    def list_secrets(self, secret_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """قائمة الأسرار"""
        secrets = list(self.secrets.values())
        
        if secret_type:
            secrets = [s for s in secrets if s.secret_type == secret_type]
        
        return [s.to_dict() for s in secrets]
    
    def delete_secret(self, secret_id: str) -> Dict[str, Any]:
        """حذف سر"""
        if secret_id not in self.secrets:
            return {"success": False, "error": "Secret not found"}
        
        secret_name = self.secrets[secret_id].name
        del self.secrets[secret_id]
        
        # حذف من الجداول
        if secret_id in self.rotation_schedules:
            del self.rotation_schedules[secret_id]
        
        # حذف من السياسات
        for service, secrets in self.access_policies.items():
            if secret_id in secrets:
                secrets.remove(secret_id)
        
        self._save_secrets()
        
        self._log_access(secret_id, "system", "delete", True)
        log_info(f"Deleted secret: {secret_name} ({secret_id})")
        
        return {"success": True, "message": f"Secret {secret_name} deleted"}
    
    def get_audit_log(self, hours: int = 24) -> List[Dict[str, Any]]:
        """الحصول على سجل التدقيق"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [
            log for log in self.audit_log
            if datetime.fromisoformat(log["timestamp"]) > cutoff
        ]


# Global instance
_secret_manager: Optional[UnifiedSecretManager] = None


def get_secret_manager() -> UnifiedSecretManager:
    """الحصول على مثيل مدير الأسرار"""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = UnifiedSecretManager()
    return _secret_manager

