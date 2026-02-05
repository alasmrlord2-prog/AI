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

**الحل:**
```bash
# 1. تحقق من حالة Ollama
docker ps -a | grep ollama

# 2. شغله أو أنشئ واحد جديد:
docker start ollama || (docker rm -f ollama && docker run -d -p 11434:11434 --name ollama ollama/ollama)

# 3. تحقق:
sleep 5 && curl http://localhost:11434/api/tags

# 4. تحميل Model (إذا كان 404):
docker exec -it ollama ollama pull llama3.2:1b

# أو إذا لم يكن docker exec متاح:
curl -X POST http://localhost:11434/api/pull -d '{"name":"llama3.2:1b"}'

# 5. إعداد .env
cd /home/ai/ai-agent/backend
echo "OLLAMA_URL=http://localhost:11434" >> .env

# 6. إعادة تشغيل
./restart_backend.sh
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

