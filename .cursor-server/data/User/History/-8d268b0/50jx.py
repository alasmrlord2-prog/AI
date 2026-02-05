import os

def run(path):
    try:
        path = path.strip()
        # إذا المسار ما بدأ بـ /، نحوله لمسار مطلق
        if not path.startswith('/'):
            # لو المسار يبدأ بـ home/ أو ~/، نحوله لمسار مطلق
            if path.startswith('home/'):
                path = '/' + path
            elif path.startswith('~/'):
                path = os.path.expanduser(path)
            else:
                # لو المسار نسبي، نضيف /home/ai/ كمسار أساسي
                path = os.path.join('/home/ai', path.lstrip('/'))
        
        # التأكد من وجود الملف
        if not os.path.exists(path):
            return f"[Errno 2] No such file or directory: '{path}'"
        
        # التأكد إنه ملف مش مجلد
        if os.path.isdir(path):
            return f"[Errno 21] Is a directory: '{path}'"
        
        return open(path, 'r', encoding='utf-8', errors='ignore').read()
    except Exception as e:
        return str(e)
