import os

def run(path):
    """
    قراءة أي ملف على السيرفر من أي مسار.
    
    المشكلة السابقة: كان الكود يحد المسارات فقط لـ /home/ai/
    الحل: السماح بقراءة أي ملف على السيرفر من أي مسار مطلق
    
    ملاحظات الأمان:
    - يجب التأكد من صلاحيات الوصول للملفات الحساسة
    - يمكن إضافة قائمة سوداء للمسارات المحظورة إذا لزم الأمر
    """
    try:
        path = path.strip()
        
        # إذا المسار ما بدأ بـ /، نحوله لمسار مطلق
        if not path.startswith('/'):
            # لو المسار يبدأ بـ ~/، نحوله لمسار مطلق
            if path.startswith('~/'):
                path = os.path.expanduser(path)
            elif path.startswith('home/'):
                # لو يبدأ بـ home/ بدون /، نضيف / في البداية
                path = '/' + path
            else:
                # لو المسار نسبي، نستخدم المسار الحالي للعمل كأساس
                # بدلاً من حصره في /home/ai/ فقط
                current_dir = os.getcwd()
                path = os.path.abspath(os.path.join(current_dir, path))
        
        # التأكد من وجود الملف
        if not os.path.exists(path):
            return f"[Errno 2] No such file or directory: '{path}'"
        
        # التأكد إنه ملف مش مجلد
        if os.path.isdir(path):
            return f"[Errno 21] Is a directory: '{path}'"
        
        # محاولة قراءة الملف
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content
        except PermissionError:
            return f"[Errno 13] Permission denied: '{path}'"
        except Exception as e:
            return f"Error reading file '{path}': {str(e)}"
            
    except Exception as e:
        return f"Error: {str(e)}"
