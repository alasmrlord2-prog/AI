# 🔧 الإصلاحات - Fixes

## ❌ المشكلة: Failed to fetch في Login

**السبب:** الباك إند لا يعمل أو الـ URL خاطئ

**الحل:**
```bash
# 1. تثبيت dependencies
cd /home/ai/ai-agent/backend
sudo apt-get install -y python3-dev build-essential
pip install -r requirements.txt

# 2. تشغيل الباك إند
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

