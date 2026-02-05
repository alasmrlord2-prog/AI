# 🔧 الإصلاحات - Fixes

## ❌ Failed to fetch

**السبب:** الباك إند لا يعمل أو الـ URL خاطئ

**الحل:**
```bash
# 1. تحقق من أن الباك إند يعمل
curl http://localhost:8000/health
# يجب أن يعيد: {"status":"ok","service":"ai-backend"}

# 2. إذا لم يعمل، شغله:
cd /home/ai/ai-agent/backend
./start_backend.sh

# 3. إعداد Frontend .env.local (استبدل 18.184.134.108 بـ IP سيرفرك)
cd /home/ai/ai-agent/frontend
cat > .env.local << 'EOF'
NEXT_PUBLIC_AGENT_API_URL=http://18.184.134.108:8000
NEXT_PUBLIC_BACKEND_URL=http://18.184.134.108:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://18.184.134.108:8000
EOF

# 4. إعادة تشغيل Frontend
./restart_frontend.sh
```

---

## ❌ Agent Error: Connection refused to Ollama

**الحل:**
```bash
# 1. تحقق من حالة Ollama
docker ps -a | grep ollama

# 2. شغله أو أنشئ واحد جديد:
docker start ollama || (docker rm -f ollama && docker run -d -p 11434:11434 --name ollama ollama/ollama)

# 3. تحقق:
sleep 5 && curl http://localhost:11434/api/tags

# 4. إعداد .env
cd /home/ai/ai-agent/backend
echo "OLLAMA_URL=http://localhost:11434" >> .env

# 5. إعادة تشغيل
./restart_backend.sh
```

---

## ❌ AttributeError: 'Settings' object has no attribute 'router'

**تم الإصلاح!** ✅

إذا استمرت المشكلة:
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

