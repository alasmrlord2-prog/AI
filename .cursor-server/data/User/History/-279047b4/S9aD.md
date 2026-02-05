# حل المشاكل - Troubleshooting Guide

## 🔧 المشاكل الشائعة والحلول

### 1. Ollama Model Not Found

**المشكلة:**
```
Ollama connection failed: Model 'llama3.2:1b' not found
```

**الحل:**
```bash
# تحميل النموذج
curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3.2:1b"}'

# أو استخدام Ollama CLI
ollama pull llama3.2:1b

# التحقق من النماذج المتاحة
curl http://localhost:11434/api/tags
```

**ملاحظة:** التحميل قد يستغرق بضع دقائق حسب سرعة الإنترنت.

---

### 2. Read File - File Not Found

**المشكلة:**
```
[Errno 2] No such file or directory: '/app/main.py'
```

**الحل:**
- استخدم المسار الصحيح:
  - `app/main.py` (مسار نسبي)
  - `/home/ai/ai-agent/backend/app/main.py` (مسار مطلق)
- أو استخدم مسار نسبي من المجلد الحالي

**أمثلة:**
```bash
# ✅ صحيح
app/main.py
backend/app/main.py
/home/ai/ai-agent/backend/app/main.py

# ❌ خاطئ
/app/main.py  # هذا للمسار داخل Docker container فقط
```

---

### 3. Chrome Extension Errors

**المشكلة:**
```
chrome-extension://invalid/:1 Failed to load resource: net::ERR_FAILED
quillbot-content.js errors
```

**الحل:**
- هذه الأخطاء من Chrome Extensions (مثل QuillBot)
- **ليست مشكلة في الكود**
- يمكن تجاهلها أو تعطيل الـ Extensions

---

### 4. Run Shell Requires Approval

**المشكلة:**
```json
{
  "error": {
    "status": "pending",
    "action_id": "action_...",
    "message": "Action requires approval"
  }
}
```

**الحل:**
- هذا **سلوك طبيعي** في DevOps Mode
- العمليات الخطيرة تحتاج موافقة
- اذهب إلى صفحة Approvals في Dashboard
- أو غيّر Agent Mode إلى "Root" في Settings

---

### 5. Backend لا يبدأ

**المشكلة:**
```
Port 8000 is already in use
```

**الحل:**
```bash
cd /home/ai/ai-agent/backend
./stop.sh
./start.sh
```

---

### 6. Frontend لا يبدأ

**المشكلة:**
```
Port 3000 is already in use
```

**الحل:**
```bash
cd /home/ai/ai-agent/frontend
./stop.sh
./start.sh
```

---

### 7. Permission Denied للـ pending_actions.json

**المشكلة:**
```
[Errno 13] Permission denied: 'memory/pending_actions.json'
```

**الحل:**
```bash
cd /home/ai/ai-agent/backend
sudo chmod 777 memory/
touch memory/pending_actions.json
chmod 666 memory/pending_actions.json
```

---

### 8. Backend Logs Permission Denied

**المشكلة:**
```
./start.sh: line 34: /tmp/backend.log: Permission denied
```

**الحل:**
- تم إصلاح هذه المشكلة في السكربت
- الـ logs الآن في `backend/backend.log`
- إذا استمرت المشكلة:
```bash
touch /home/ai/ai-agent/backend/backend.log
chmod 666 /home/ai/ai-agent/backend/backend.log
```

---

## 🔍 التحقق من الحالة

### Backend
```bash
# Health Check
curl http://localhost:8000/health

# Permissions API
curl http://localhost:8000/api/permissions/list

# Logs
tail -f /home/ai/ai-agent/backend/backend.log
```

### Frontend
```bash
# افتح المتصفح
http://localhost:3000

# Logs
tail -f /tmp/frontend.log
```

### Ollama
```bash
# التحقق من الحالة
curl http://localhost:11434/api/tags

# النماذج المتاحة
ollama list
```

---

## 📝 Logs Locations

- **Backend**: `/home/ai/ai-agent/backend/backend.log`
- **Frontend**: `/tmp/frontend.log`
- **Ollama Pull**: `/tmp/ollama_pull.log`

---

## 🆘 إذا لم تحل المشكلة

1. تحقق من الـ logs
2. تأكد من أن كل الخدمات تعمل
3. راجع الوثائق:
   - `HOW_TO_RUN.md`
   - `backend/README.md`
   - `frontend/README.md`

---

## ✅ Checklist

قبل الإبلاغ عن مشكلة، تأكد من:

- [ ] Backend يعمل (`curl http://localhost:8000/health`)
- [ ] Frontend يعمل (`http://localhost:3000`)
- [ ] Ollama يعمل (`curl http://localhost:11434/api/tags`)
- [ ] النموذج محمّل (`ollama list`)
- [ ] الـ logs لا تحتوي على أخطاء خطيرة

