import os
from app.utils.path_resolver import resolve_path

def run(path="logs/agent.log"):
    """
    قراءة ملفات السجلات باستخدام نظام Path Resolver المحترف.
    يدعم جميع أنواع المسارات: logs/agent.log, /app/logs/agent.log, ./logs/agent.log
    """
    try:
        # استخدام نظام Path Resolver المحترف
        resolved_path = resolve_path(path)
        
        if not os.path.exists(resolved_path):
            return f"Log file not found: {path} (resolved to: {resolved_path})"
        
        try:
            with open(resolved_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[-5000:]
        except Exception as e:
            return f"Error reading log file: {str(e)}"
    except PermissionError as e:
        return f"Access denied: {str(e)}"
    except ValueError as e:
        return f"Invalid path: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

