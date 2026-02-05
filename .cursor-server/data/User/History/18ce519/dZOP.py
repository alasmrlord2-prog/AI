"""Settings-related models."""
from pydantic import BaseModel
from typing import List, Optional


class SettingsModel(BaseModel):
    """Settings model."""
    allow_shell: bool = False
    allow_read_file: bool = True
    allow_doc_search: bool = True
    allow_logs: bool = True
    long_memory_enabled: bool = True
    agent_mode: str = "devops"
    memory_mode: str = "short"
    require_approval: List[str] = ["run_shell"]
    
    # إعدادات المسارات - للتحكم بالوصول للملفات
    # allowed_paths: قائمة المسارات المسموحة (فارغة = السماح بكل المسارات)
    # restricted_paths: قائمة المسارات المحظورة (مثل /etc/shadow, /proc/kcore)
    # base_path: المسار الأساسي للعمل (افتراضي: /app داخل container)
    # host_mount_path: مسار mount المجلد الرئيسي من host (افتراضي: /host/ai-agent)
    allowed_paths: List[str] = []  # فارغة = السماح بكل المسارات
    restricted_paths: List[str] = ["/proc/kcore", "/dev/mem", "/sys/kernel"]  # مسارات محظورة افتراضياً
    base_path: Optional[str] = None  # None = استخدام المسار الحالي
    host_mount_path: Optional[str] = "/host/ai-agent"  # مسار mount المجلد الرئيسي من host

