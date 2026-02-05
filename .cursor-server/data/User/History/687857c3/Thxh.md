# 🔧 الإصلاحات - Fixes

## ❌ Failed to fetch في Login

**الحل:**
```bash
cd /home/ai/ai-agent/backend
sudo apt-get install -y python3-dev build-essential
pip install -r requirements.txt
./start_backend.sh

cd /home/ai/ai-agent/frontend
cat > .env.local << 'EOF'
NEXT_PUBLIC_AGENT_API_URL=http://18.184.134.108:8000
NEXT_PUBLIC_BACKEND_URL=http://18.184.134.108:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://18.184.134.108:8000
EOF
./restart_frontend.sh
```

---

## ❌ Agent Error: Connection refused to Ollama

**السبب:** Ollama غير مشغل أو الـ URL خاطئ

**الحل:**
```bash
# 1. تشغيل Ollama
docker run -d -p 11434:11434 --name ollama ollama/ollama

# أو إذا كان مشغل على السيرفر:
# تحقق من أن Ollama يعمل
curl http://localhost:11434/api/tags

# 2. إعداد OLLAMA_URL في backend/.env
cd /home/ai/ai-agent/backend
echo "OLLAMA_URL=http://localhost:11434" >> .env

# 3. إعادة تشغيل الباك إند
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

