"""
Log Collector - 100% Local
جامع اللوغات محلي بالكامل
"""
import os
import time
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class LogFileHandler(FileSystemEventHandler):
    """معالج تغييرات ملفات الـlogs"""
    
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback
        self.last_position: Dict[str, int] = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.log'):
            self._read_new_lines(event.src_path)
    
    def _read_new_lines(self, file_path: str):
        """قراءة الأسطر الجديدة فقط"""
        try:
            current_size = os.path.getsize(file_path)
            last_pos = self.last_position.get(file_path, 0)
            
            if current_size > last_pos:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_pos)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        if line.strip():
                            self.callback(file_path, line.strip())
                    
                    self.last_position[file_path] = f.tell()
        except Exception as e:
            log_warning(f"Error reading log file {file_path}: {e}")


class LogCollector:
    """
    جامع اللوغات - محلي 100%
    يراقب ملفات الـlogs ويرسل الأحداث للمحرك الأمني
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.watched_files: List[str] = []
        self.observer: Optional[Observer] = None
        self.callbacks: List[Callable[[str, str], None]] = []
        self._initialize_paths()
    
    def _initialize_paths(self):
        """تهيئة المسارات المراقبة"""
        # المسارات من الإعدادات
        for path in self.settings.SECURITY_AI_LOG_PATHS:
            if os.path.exists(path):
                self.watched_files.append(path)
            elif os.path.exists(os.path.expanduser(path)):
                self.watched_files.append(os.path.expanduser(path))
        
        # مسارات إضافية شائعة
        common_paths = [
            "/var/log/nginx/access.log",
            "/var/log/nginx/error.log",
            "/var/log/auth.log",
            "/var/log/syslog",
            "/var/log/app/backend.log",
            "/app/logs/backend.log",
            "./logs/backend.log",
        ]
        
        for path in common_paths:
            if os.path.exists(path) and path not in self.watched_files:
                self.watched_files.append(path)
    
    def add_callback(self, callback: Callable[[str, str], None]):
        """إضافة callback عند وصول log جديد"""
        self.callbacks.append(callback)
    
    def _on_log_line(self, file_path: str, line: str):
        """معالج سطر log جديد"""
        source = os.path.basename(file_path)
        
        for callback in self.callbacks:
            try:
                callback(file_path, line)
            except Exception as e:
                log_warning(f"Error in log callback: {e}")
    
    def start(self):
        """بدء مراقبة ملفات الـlogs"""
        if not self.watched_files:
            log_warning("No log files to watch")
            return
        
        self.observer = Observer()
        
        # تجميع الملفات حسب المجلدات
        dirs_to_watch = set()
        files_to_watch = []
        
        for file_path in self.watched_files:
            if os.path.isfile(file_path):
                files_to_watch.append(file_path)
                dirs_to_watch.add(os.path.dirname(file_path))
            elif os.path.isdir(file_path):
                dirs_to_watch.add(file_path)
        
        # مراقبة المجلدات
        handler = LogFileHandler(self._on_log_line)
        for directory in dirs_to_watch:
            try:
                self.observer.schedule(handler, directory, recursive=False)
                log_info(f"Watching directory: {directory}")
            except Exception as e:
                log_warning(f"Failed to watch directory {directory}: {e}")
        
        self.observer.start()
        log_info(f"Log collector started, watching {len(self.watched_files)} files")
    
    def stop(self):
        """إيقاف المراقبة"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            log_info("Log collector stopped")
    
    def read_recent_logs(self, file_path: str, lines: int = 100) -> List[str]:
        """قراءة آخر N سطر من ملف log"""
        try:
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                return [line.strip() for line in all_lines[-lines:] if line.strip()]
        except Exception as e:
            log_warning(f"Error reading recent logs from {file_path}: {e}")
            return []
    
    def get_all_logs(self, hours: int = 1) -> Dict[str, List[str]]:
        """الحصول على جميع الـlogs من الملفات المراقبة"""
        result = {}
        cutoff_time = time.time() - (hours * 3600)
        
        for file_path in self.watched_files:
            if os.path.exists(file_path):
                try:
                    # قراءة الملف والتحقق من وقت التعديل
                    mtime = os.path.getmtime(file_path)
                    if mtime > cutoff_time:
                        logs = self.read_recent_logs(file_path, 1000)
                        if logs:
                            result[file_path] = logs
                except Exception as e:
                    log_warning(f"Error reading {file_path}: {e}")
        
        return result


# Global instance
_log_collector: Optional[LogCollector] = None


def get_log_collector() -> LogCollector:
    """الحصول على مثيل جامع اللوغات"""
    global _log_collector
    if _log_collector is None:
        _log_collector = LogCollector()
    return _log_collector

