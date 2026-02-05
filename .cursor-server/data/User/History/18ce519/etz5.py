"""Settings-related models."""
from pydantic import BaseModel
from typing import List, Optional, Dict


class ServerConfig(BaseModel):
    """Server configuration for multi-server access"""
    name: str
    host: str
    port: int = 9090
    protocol: str = "ws"  # ws or http
    token: Optional[str] = None
    enabled: bool = True


class SettingsModel(BaseModel):
    """Settings model with unified permissions."""
    # Tool Permissions
    allow_shell: bool = False
    allow_read_file: bool = True
    allow_doc_search: bool = True
    allow_logs: bool = True
    
    # Agent Mode: safe, devops, root, short
    agent_mode: str = "devops"
    
    # Memory Mode: off, short, long
    memory_mode: str = "short"
    long_memory_enabled: bool = True
    
    # Actions requiring approval (in DevOps mode)
    require_approval: List[str] = ["run_shell", "write_file", "restart_service", "backup.restore", "cicd.deploy"]
    
    # إعدادات المسارات - للتحكم بالوصول للملفات
    # allowed_paths: قائمة المسارات المسموحة (فارغة = السماح بكل المسارات)
    # restricted_paths: قائمة المسارات المحظورة (مثل /etc/shadow, /proc/kcore)
    # base_path: المسار الأساسي للعمل (افتراضي: /app داخل container)
    # host_mount_path: مسار mount المجلد الرئيسي من host (افتراضي: /host/ai-agent)
    allowed_paths: List[str] = []  # فارغة = السماح بكل المسارات
    restricted_paths: List[str] = ["/proc/kcore", "/dev/mem", "/sys/kernel"]  # مسارات محظورة افتراضياً
    base_path: Optional[str] = None  # None = استخدام المسار الحالي
    host_mount_path: Optional[str] = "/host/ai-agent"  # مسار mount المجلد الرئيسي من host
    
    # Multi-server configuration
    servers: List[Dict] = []  # List of ServerConfig dicts
    default_server: str = "local"  # Default server name

