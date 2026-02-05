"""
Plugin Store - 100% Local
متجر plugins داخلي
"""
import os
import json
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning, log_error


class Plugin:
    """Plugin"""
    def __init__(
        self,
        plugin_id: str,
        name: str,
        version: str,
        description: str,
        plugin_type: str,
        author: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.description = description
        self.plugin_type = plugin_type  # "tool", "workflow", "monitoring", "security"
        self.author = author
        self.metadata = metadata or {}
        self.installed = False
        self.install_path: Optional[str] = None
        self.installed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "type": self.plugin_type,
            "author": self.author,
            "metadata": self.metadata,
            "installed": self.installed,
            "install_path": self.install_path,
            "installed_at": self.installed_at.isoformat() if self.installed_at else None
        }


class PluginStore:
    """
    متجر plugins داخلي
    أدوات، Modules، Workflows، Monitoring plugins
    قابل للتثبيت بزر واحد
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.store_dir = Path("plugins/store")
        self.store_dir.mkdir(parents=True, exist_ok=True)
        
        self.installed_dir = Path("plugins/installed")
        self.installed_dir.mkdir(parents=True, exist_ok=True)
        
        self.plugins: Dict[str, Plugin] = {}
        self.installed_plugins: Dict[str, Plugin] = {}
        
        self._load_store()
        self._load_installed()
    
    def _load_store(self):
        """تحميل قائمة plugins المتاحة"""
        index_file = self.store_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                    for plugin_data in data.get("plugins", []):
                        plugin = Plugin(
                            plugin_id=plugin_data["plugin_id"],
                            name=plugin_data["name"],
                            version=plugin_data["version"],
                            description=plugin_data.get("description", ""),
                            plugin_type=plugin_data.get("type", "tool"),
                            author=plugin_data.get("author", "unknown"),
                            metadata=plugin_data.get("metadata", {})
                        )
                        self.plugins[plugin.plugin_id] = plugin
            except Exception as e:
                log_warning(f"Error loading plugin store: {e}")
    
    def _load_installed(self):
        """تحميل قائمة plugins المثبتة"""
        installed_file = self.installed_dir / "installed.json"
        if installed_file.exists():
            try:
                with open(installed_file, 'r') as f:
                    data = json.load(f)
                    for plugin_data in data.get("plugins", []):
                        plugin = Plugin(
                            plugin_id=plugin_data["plugin_id"],
                            name=plugin_data["name"],
                            version=plugin_data["version"],
                            description=plugin_data.get("description", ""),
                            plugin_type=plugin_data.get("type", "tool"),
                            author=plugin_data.get("author", "unknown"),
                            metadata=plugin_data.get("metadata", {})
                        )
                        plugin.installed = True
                        plugin.install_path = plugin_data.get("install_path")
                        if plugin_data.get("installed_at"):
                            plugin.installed_at = datetime.fromisoformat(plugin_data["installed_at"])
                        
                        self.installed_plugins[plugin.plugin_id] = plugin
            except Exception as e:
                log_warning(f"Error loading installed plugins: {e}")
    
    def _save_installed(self):
        """حفظ قائمة plugins المثبتة"""
        installed_file = self.installed_dir / "installed.json"
        try:
            data = {
                "plugins": [p.to_dict() for p in self.installed_plugins.values()]
            }
            with open(installed_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log_error(f"Error saving installed plugins: {e}")
    
    def register_plugin(
        self,
        name: str,
        version: str,
        description: str,
        plugin_type: str,
        author: str,
        plugin_file: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Plugin:
        """تسجيل plugin جديد في المتجر"""
        plugin_id = f"{name.lower().replace(' ', '_')}_{version}"
        
        plugin = Plugin(
            plugin_id=plugin_id,
            name=name,
            version=version,
            description=description,
            plugin_type=plugin_type,
            author=author,
            metadata=metadata or {}
        )
        
        self.plugins[plugin_id] = plugin
        
        # حفظ plugin file إذا كان موجوداً
        if plugin_file and os.path.exists(plugin_file):
            dest = self.store_dir / f"{plugin_id}.py"
            shutil.copy2(plugin_file, dest)
            plugin.metadata["file_path"] = str(dest)
        
        # حفظ الفهرس
        self._save_store()
        
        log_info(f"Registered plugin: {name} ({plugin_id})")
        return plugin
    
    def _save_store(self):
        """حفظ فهرس المتجر"""
        index_file = self.store_dir / "index.json"
        try:
            data = {
                "plugins": [p.to_dict() for p in self.plugins.values()]
            }
            with open(index_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log_error(f"Error saving plugin store: {e}")
    
    def list_plugins(self, plugin_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """قائمة plugins المتاحة"""
        plugins = list(self.plugins.values())
        
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        
        return [p.to_dict() for p in plugins]
    
    def install_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """تثبيت plugin"""
        if plugin_id not in self.plugins:
            return {"success": False, "error": "Plugin not found in store"}
        
        if plugin_id in self.installed_plugins:
            return {"success": False, "error": "Plugin already installed"}
        
        plugin = self.plugins[plugin_id]
        
        try:
            # نسخ plugin إلى مجلد المثبتة
            install_path = self.installed_dir / f"{plugin_id}.py"
            
            # إذا كان هناك ملف plugin
            if "file_path" in plugin.metadata:
                source_file = plugin.metadata["file_path"]
                if os.path.exists(source_file):
                    shutil.copy2(source_file, install_path)
            
            # تحديث plugin
            plugin.installed = True
            plugin.install_path = str(install_path)
            plugin.installed_at = datetime.now()
            
            self.installed_plugins[plugin_id] = plugin
            self._save_installed()
            
            log_info(f"Installed plugin: {plugin.name} ({plugin_id})")
            
            return {
                "success": True,
                "message": f"Plugin {plugin.name} installed successfully",
                "plugin": plugin.to_dict()
            }
        except Exception as e:
            log_error(f"Error installing plugin {plugin_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def uninstall_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """إلغاء تثبيت plugin"""
        if plugin_id not in self.installed_plugins:
            return {"success": False, "error": "Plugin not installed"}
        
        plugin = self.installed_plugins[plugin_id]
        
        try:
            # حذف ملف plugin
            if plugin.install_path and os.path.exists(plugin.install_path):
                os.remove(plugin.install_path)
            
            # حذف من القائمة
            del self.installed_plugins[plugin_id]
            self._save_installed()
            
            log_info(f"Uninstalled plugin: {plugin.name} ({plugin_id})")
            
            return {
                "success": True,
                "message": f"Plugin {plugin.name} uninstalled successfully"
            }
        except Exception as e:
            log_error(f"Error uninstalling plugin {plugin_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_installed(self) -> List[Dict[str, Any]]:
        """قائمة plugins المثبتة"""
        return [p.to_dict() for p in self.installed_plugins.values()]
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """معلومات plugin"""
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            info = plugin.to_dict()
            info["installed"] = plugin_id in self.installed_plugins
            return info
        return None


# Global instance
_plugin_store: Optional[PluginStore] = None


def get_plugin_store() -> PluginStore:
    """الحصول على مثيل متجر plugins"""
    global _plugin_store
    if _plugin_store is None:
        _plugin_store = PluginStore()
    return _plugin_store

