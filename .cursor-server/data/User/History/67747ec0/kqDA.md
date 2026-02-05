# 🔧 حل مشاكل الـ Ports والـ Docker

## المشكلة
الـ ports 3000, 3001, 3002 لا تزال مستخدمة من قبل `next-server` processes.

## الحل السريع

### 1. قتل جميع الـ processes على الـ ports:
```bash
cd /home/ai/ai-agent
./KILL_ALL_PORTS.sh
```

### 2. ثم تشغيل الخدمات:
```bash
# إذا كنت root:
docker compose up -d postgres ollama backend frontend-dashboard frontend-crm frontend-aaa

# أو إذا لم تكن root:
sudo docker compose up -d postgres ollama backend frontend-dashboard frontend-crm frontend-aaa
```

## حل مشكلة Docker Permissions

إذا ظهرت رسالة "permission denied" مع Docker:

### الحل 1: إضافة المستخدم إلى docker group
```bash
sudo usermod -aG docker $USER
newgrp docker  # أو logout/login
```

### الحل 2: استخدام sudo
```bash
sudo docker compose up -d ...
```

### الحل 3: تعديل صلاحيات Docker socket (غير موصى به للأمان)
```bash
sudo chmod 666 /var/run/docker.sock
```

## التحقق من الحالة

```bash
# فحص الـ ports
ss -tlnp | grep -E ':(3000|3001|3002)'

# فحص الـ containers
docker ps

# فحص الـ logs
docker compose logs -f
```

## إذا استمرت المشكلة

1. إعادة تشغيل Docker:
```bash
sudo systemctl restart docker
```

2. قتل جميع الـ processes يدوياً:
```bash
pkill -9 -f "next-server"
pkill -9 -f "next"
for port in 3000 3001 3002; do
    fuser -k ${port}/tcp 2>/dev/null || true
    lsof -ti:${port} | xargs kill -9 2>/dev/null || true
done
```

3. إعادة تشغيل النظام (آخر حل):
```bash
sudo reboot
```

