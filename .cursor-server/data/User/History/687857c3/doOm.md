# 🔧 الإصلاحات - Fixes

## ❌ Failed to fetch

**الحل:**
```bash
# 1. تحقق من الباك إند
curl http://localhost:8000/health

# 2. إعداد Frontend .env.local (استبدل 18.184.134.108 بـ IP سيرفرك)
cd /home/ai/ai-agent/frontend
cat > .env.local << 'EOF'
NEXT_PUBLIC_AGENT_API_URL=http://18.184.134.108:8000
NEXT_PUBLIC_BACKEND_URL=http://18.184.134.108:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://18.184.134.108:8000
EOF

# 3. إعادة تشغيل Frontend
./restart_frontend.sh

# 4. إذا استمرت المشكلة، أعد تشغيل الباك إند (CORS محدّث)
cd /home/ai/ai-agent/backend
./restart_backend.sh
```

---

## ❌ Agent Error: Connection refused to Ollama / 404 Not Found

**التحقق من حالة Ollama:**
```bash
# 1. تحقق من أن Ollama container يعمل
docker ps | grep ollama
# يجب أن ترى container اسمه "ollama" و status "Up"

# 2. تحقق من أن Ollama يستجيب
curl http://localhost:11434/api/tags
# يجب أن يعيد JSON مع قائمة الـ models

# 3. تحقق من أن الـ model محمّل
curl http://localhost:11434/api/tags | grep "llama3.2:1b"
# إذا لم يظهر، الـ model غير محمّل
```

**الحل:**
```bash
# 1. إذا كان container متوقف، شغله:
docker start ollama

# 2. إذا لم يكن موجود، أنشئ واحد جديد:
docker run -d -p 11434:11434 --name ollama ollama/ollama

# 3. انتظر 5 ثواني حتى يبدأ Ollama:
sleep 5

# 4. تحميل الـ model (مهم جداً!):
curl -X POST http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name":"llama3.2:1b"}'
# هذا قد يستغرق بضع دقائق حسب سرعة الإنترنت

# 5. تحقق من أن الـ model تم تحميله:
curl http://localhost:11434/api/tags
# يجب أن ترى "llama3.2:1b" في القائمة

# 6. جرّب الـ Agent:
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
# إذا عمل، ستحصل على رد من الـ Agent
```

---

## ❌ AttributeError: 'Settings' object has no attribute 'router'

**تم الإصلاح!** ✅

---

## ❌ Agent Error: name 'e' is not defined / ModuleNotFoundError: No module named 'tools'

**تم الإصلاح!** ✅

المشكلة كانت في:
1. `agent_core.py` - تم تحديث import من `llm` إلى `llm_text`
2. جميع الملفات - تم تحديث imports من `tools.` إلى `app.tools.`:
   - `think_and_act.py`
   - `agent_core.py`
   - `chat.py` (من `agent.` إلى `app.agent.`)
   - `prometheus.py`
   - `monitor.py`
   - `tools.py`
   - `filesystem.py`
   - `security.py`
   - `approvals.py`

**الحل:**
```bash
cd /home/ai/ai-agent/backend
./restart_backend.sh
```

---

## ❌ ModuleNotFoundError

```bash
cd /home/ai/ai-agent/backend
sudo apt-get install -y python3-dev build-essential
pip install -r requirements.txt
```

---

## ❌ Port already in use

```bash
cd /home/ai/ai-agent/backend && ./stop_backend.sh
cd /home/ai/ai-agent/frontend && ./stop_frontend.sh
```

---

## ⚠️ React Hydration Error (Browser Extension)

**السبب:** Browser extension (مثل Grammarly/QuillBot) يضيف attributes للـ HTML

**الحل:** تم إصلاحه بإضافة `suppressHydrationWarning` للـ Textarea component.

**إذا استمرت المشكلة:**
- هذا الخطأ غير مؤثر على عمل التطبيق
- يمكن تجاهله أو تعطيل الـ extension في المتصفح

