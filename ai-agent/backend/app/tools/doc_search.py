import os
from app.utils.path_resolver import resolve_path

def run(query):
    """
    البحث في ملفات التوثيق باستخدام نظام Path Resolver المحترف.
    """
    results = []
    
    try:
        # استخدام نظام Path Resolver - يدعم /app/docs و docs/ و ./docs
        docs_path = resolve_path("docs")
    except (PermissionError, ValueError):
        # Fallback: جرب مسارات بديلة
        try:
            docs_path = resolve_path("/app/docs")
        except:
            docs_path = os.path.join(os.getcwd(), "docs")
            if not os.path.exists(docs_path):
                return "لا يوجد مجلد docs في المشروع."

    if not os.path.exists(docs_path):
        return f"لا يوجد مجلد docs في: {docs_path}"

    for root, dirs, files in os.walk(docs_path):
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    text = file.read()
                if query.lower() in text.lower():
                    results.append({"file": path, "match": query})
            except:
                continue
    
    return results if results else "لا يوجد نتائج مطابقة."
