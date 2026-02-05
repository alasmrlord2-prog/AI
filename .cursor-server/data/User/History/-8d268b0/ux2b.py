import os
from app.utils.helpers import load_settings

def run(path):
    """
    قراءة أي ملف على السيرفر من أي مسار بناءً على الإعدادات.
    
    يستخدم الإعدادات من SettingsModel للتحكم بالمسارات:
    - allowed_paths: قائمة المسارات المسموحة (فارغة = السماح بكل المسارات)
    - restricted_paths: قائمة المسارات المحظورة
    - base_path: المسار الأساسي للعمل
    
    يعمل داخل Docker container والـ host على حد سواء.
    """
    try:
        # تحميل الإعدادات
        settings = load_settings()
        
        path = path.strip()
        original_path = path
        
        # إذا المسار ما بدأ بـ /، نحوله لمسار مطلق
        if not path.startswith('/'):
            # لو المسار يبدأ بـ ~/، نحوله لمسار مطلق
            if path.startswith('~/'):
                path = os.path.expanduser(path)
            elif path.startswith('home/'):
                # لو يبدأ بـ home/ بدون /، نضيف / في البداية
                path = '/' + path
            else:
                # لو المسار نسبي، نستخدم base_path من الإعدادات أو المسار الحالي
                if settings.base_path:
                    base = settings.base_path
                else:
                    base = os.getcwd()
                path = os.path.abspath(os.path.join(base, path))
        
        # التحقق من المسارات المحظورة
        if settings.restricted_paths:
            for restricted in settings.restricted_paths:
                if path.startswith(restricted) or restricted in path:
                    return f"[Errno 13] Access denied: Path '{path}' is restricted by settings"
        
        # التحقق من المسارات المسموحة (إذا كانت محددة)
        if settings.allowed_paths:
            allowed = False
            for allowed_path in settings.allowed_paths:
                if path.startswith(allowed_path):
                    allowed = True
                    break
            if not allowed:
                return f"[Errno 13] Access denied: Path '{path}' is not in allowed_paths. Allowed paths: {', '.join(settings.allowed_paths[:3])}..."
        
        # التأكد من وجود الملف
        if not os.path.exists(path):
            # محاولة البحث في المسارات البديلة
            if not original_path.startswith('/'):
                # محاولة في المسار الحالي
                current_dir = os.getcwd()
                alt_path = os.path.abspath(os.path.join(current_dir, original_path))
                if os.path.exists(alt_path) and os.path.isfile(alt_path):
                    path = alt_path
                else:
                    return f"[Errno 2] No such file or directory: '{path}'\n💡 Tip: Current directory is '{current_dir}'. Try a relative path from here."
            else:
                return f"[Errno 2] No such file or directory: '{path}'"
        
        # التأكد إنه ملف مش مجلد
        if os.path.isdir(path):
            return f"[Errno 21] Is a directory: '{path}'\n💡 Tip: Use a file path, not a directory path."
        
        # محاولة قراءة الملف
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content
        except PermissionError:
            return f"[Errno 13] Permission denied: '{path}'\n💡 Tip: Check file permissions or run with appropriate user."
        except Exception as e:
            return f"Error reading file '{path}': {str(e)}"
            
    except Exception as e:
        return f"Error: {str(e)}"
