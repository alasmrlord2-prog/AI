import os
from app.utils.path_resolver import resolve_path

def run(path):
    """
    قراءة أي ملف على السيرفر من أي مسار باستخدام نظام Path Resolver المحترف.
    
    يستخدم نظام Path Resolver المحمول الذي:
    - يكتشف جذر المشروع تلقائياً
    - يدعم Docker /app paths
    - يحمي من path traversal
    - يعمل في أي بيئة بدون إعداد
    
    يعمل داخل Docker container والـ host على حد سواء.
    """
    try:
        # استخدام نظام Path Resolver المحترف
        resolved_path = resolve_path(path)
        
        # التأكد من وجود الملف
        if not os.path.exists(resolved_path):
            return f"[Errno 2] No such file or directory: '{path}'\n💡 Tip: Resolved to '{resolved_path}'. Make sure the file exists."
        
        # التأكد إنه ملف مش مجلد
        if os.path.isdir(resolved_path):
            return f"[Errno 21] Is a directory: '{resolved_path}'\n💡 Tip: Use a file path, not a directory path."
        
        # محاولة قراءة الملف
        try:
            with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content
        except PermissionError:
            return f"[Errno 13] Permission denied: '{resolved_path}'\n💡 Tip: Check file permissions or run with appropriate user."
        except Exception as e:
            return f"Error reading file '{resolved_path}': {str(e)}"
            
    except PermissionError as e:
        return f"[Errno 13] Access denied: {str(e)}"
    except ValueError as e:
        return f"[Errno 22] Invalid argument: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
