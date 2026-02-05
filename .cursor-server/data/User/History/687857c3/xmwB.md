# 🔧 الإصلاحات - Fixes

## المشكلة: Failed to fetch في صفحة Login

### السبب:
الباك إند لا يعمل أو الـ URL خاطئ

### الحل:

#### 1. تثبيت Dependencies:
```bash
cd /home/ai/ai-agent/backend
sudo apt-get install -y python3-dev build-essential
pip install -r requirements.txt
```

#### 2. تشغيل الباك إند:
```bash
cd /home/ai/ai-agent/backend
./start_backend.sh
```

#### 3. التحقق من أن الباك إند يعمل:
```bash
curl http://localhost:8000/health
# يجب أن يعيد: {"status":"ok","service":"ai-backend"}
```

#### 4. إعداد Frontend Environment:
```bash
cd /home/ai/ai-agent/frontend
# إنشاء .env.local إذا لم يكن موجود
cat > .env.local << EOF
NEXT_PUBLIC_AGENT_API_URL=http://YOUR_SERVER_IP:8000
NEXT_PUBLIC_BACKEND_URL=http://YOUR_SERVER_IP:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://YOUR_SERVER_IP:8000
EOF

# استبدل YOUR_SERVER_IP بـ IP السيرفر (مثلاً: 18.184.134.108)
```

#### 5. إعادة تشغيل Frontend:
```bash
cd /home/ai/ai-agent/frontend
./restart_frontend.sh
```

---

## مشكلة: ModuleNotFoundError

### الحل:
```bash
cd /home/ai/ai-agent/backend
sudo apt-get install -y python3-dev build-essential
pip install -r requirements.txt
```

---

## مشكلة: Port already in use

### الحل:
```bash
# Backend
cd /home/ai/ai-agent/backend
./stop_backend.sh

# Frontend
cd /home/ai/ai-agent/frontend
./stop_frontend.sh
```

---

## ملاحظات:
- تأكد من أن الباك إند يعمل على نفس IP الذي يستخدمه الفرونت إند
- إذا كان الباك إند على localhost، استخدم نفس IP للسيرفر في .env.local
- تحقق من firewall أن البورت 8000 مفتوح

