# تعليمات إعادة تشغيل الخادم الخلفي

## المشكلة الحالية

الخادم الخلفي يعمل لكنه لا يستجيب. العملية القديمة (PID 1266039) تعمل كـ root ولا يمكن إيقافها بدون صلاحيات root.

## الحل

### الطريقة 1: إعادة التشغيل كـ root (موصى بها)

```bash
# 1. إيقاف جميع عمليات uvicorn
sudo pkill -9 -f uvicorn
sleep 3

# 2. التأكد من أن المنفذ 8000 فارغ
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || true
sleep 2

# 3. إعادة تشغيل الخادم
cd /home/ai/ai-agent/backend
sudo -u root python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# 4. التحقق من الحالة
sleep 5
curl http://localhost:8000/health
```

### الطريقة 2: استخدام منفذ مختلف مؤقتًا

```bash
# تشغيل على منفذ 8001
cd /home/ai/ai-agent/backend
python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > backend.log 2>&1 &

# تحديث nginx لاستخدام المنفذ 8001
# في nginx-ai-agent-complete.conf، غيّر:
# server 127.0.0.1:8000;
# إلى:
# server 127.0.0.1:8001;
```

### الطريقة 3: استخدام systemd service

إنشاء ملف service:

```bash
sudo nano /etc/systemd/system/ai-agent-backend.service
```

المحتوى:
```ini
[Unit]
Description=AI Agent Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/ai/ai-agent/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

ثم:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-agent-backend
sudo systemctl restart ai-agent-backend
sudo systemctl status ai-agent-backend
```

## التحقق من الحالة

```bash
# التحقق من Health
curl http://localhost:8000/health

# اختبار Chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'

# التحقق من العمليات
ps aux | grep uvicorn
```

## ملاحظات

- ✅ الكود يعمل بشكل صحيح (تم اختباره)
- ⚠️ يحتاج Ollama للردود الفعلية
- ⚠️ يحتاج صلاحيات root لإيقاف العملية القديمة

