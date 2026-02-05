# ⚡ Quick Start Guide - ثلاث خدمات منفصلة

## 🚀 البدء السريع (3 خطوات)

### 1️⃣ إعداد NGINX

```bash
./setup-all-services.sh
```

هذا السكربت سيقوم بـ:
- نسخ ملفات NGINX إلى `/etc/nginx/sites-available/`
- تفعيل المواقع
- اختبار التكوين
- إعادة تحميل NGINX

---

### 2️⃣ تشغيل Backend

```bash
cd backend
./start.sh
```

**التحقق:**
```bash
curl http://localhost:8000/health
```

---

### 3️⃣ تشغيل Frontends

#### الطريقة الأسهل (PM2):

```bash
cd frontend
./pm2-start.sh
```

#### أو يدوياً:

```bash
cd frontend
./start-all.sh
```

---

## ✅ التحقق من الخدمات

```bash
# Health checks
curl http://ai-agent.bankid-sy.com/health
curl http://crm.bankid-sy.com/health
curl http://aaa.bankid-sy.com/health
```

---

## 🎯 URLs

| الخدمة | URL |
|--------|-----|
| **AI-Agent** | http://ai-agent.bankid-sy.com |
| **CRM** | http://crm.bankid-sy.com |
| **AAA** | http://aaa.bankid-sy.com |

---

## 🛑 إيقاف الخدمات

### إيقاف Frontends:

```bash
# إذا استخدمت PM2
cd frontend
./pm2-stop.sh

# أو
pm2 stop all

# إذا استخدمت start-all.sh
cd frontend
./stop-all.sh
```

### إيقاف Backend:

```bash
cd backend
./stop.sh
```

---

## 📝 Logs

### Frontend Logs (PM2):
```bash
pm2 logs
```

### Frontend Logs (start-all.sh):
```bash
tail -f /tmp/frontend-ai-agent.log
tail -f /tmp/frontend-crm.log
tail -f /tmp/frontend-aaa.log
```

### Backend Logs:
```bash
cd backend
tail -f backend.log
```

### NGINX Logs:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## 🔧 Troubleshooting

### Port already in use:
```bash
# Kill process on port
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
lsof -ti:3002 | xargs kill -9
```

### NGINX issues:
```bash
# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx
```

---

**للمزيد من التفاصيل:** راجع `COMPLETE_SETUP_GUIDE.md`

