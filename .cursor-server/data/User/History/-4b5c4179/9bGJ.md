# 📋 تعليمات النشر - ثلاث خدمات منفصلة

## 🎯 الهدف

إعداد ثلاث خدمات منفصلة تعمل بشكل مستقل:
- **AI-Agent** على `ai-agent.bankid-sy.com` (port 3000)
- **CRM** على `crm.bankid-sy.com` (port 3001)  
- **AAA** على `aaa.bankid-sy.com` (port 3002)

جميعها متصلة بنفس Backend على port 8000.

---

## ⚡ الخطوات السريعة

### على السيرفر:

```bash
# 1. الانتقال للمجلد
cd /home/ai/ai-agent

# 2. إعداد NGINX (يحتاج sudo)
./setup-all-services.sh

# 3. تشغيل Backend
cd backend
./start.sh

# 4. تشغيل Frontends (في terminal منفصل أو background)
cd ../frontend
./pm2-start.sh
```

---

## 📝 الخطوات التفصيلية

### 1. نسخ ملفات NGINX

```bash
sudo cp nginx-ai-agent-complete.conf /etc/nginx/sites-available/ai-agent.bankid-sy.com
sudo cp nginx-aaa-complete.conf /etc/nginx/sites-available/aaa.bankid-sy.com
sudo cp nginx-crm-complete.conf /etc/nginx/sites-available/crm.bankid-sy.com
```

### 2. تفعيل المواقع

```bash
sudo ln -sf /etc/nginx/sites-available/ai-agent.bankid-sy.com /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/aaa.bankid-sy.com /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/crm.bankid-sy.com /etc/nginx/sites-enabled/
```

### 3. اختبار وإعادة تحميل NGINX

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 4. تشغيل Backend

```bash
cd backend
./start.sh
```

**التحقق:**
```bash
curl http://localhost:8000/health
```

### 5. تشغيل Frontends

#### باستخدام PM2 (موصى به):

```bash
cd frontend
./pm2-start.sh
```

#### أو يدوياً (3 terminals):

```bash
# Terminal 1
cd frontend
./start-ai-agent.sh

# Terminal 2
cd frontend
./start-crm.sh

# Terminal 3
cd frontend
./start-aaa.sh
```

#### أو كل شيء مرة واحدة:

```bash
cd frontend
./start-all.sh
```

---

## ✅ التحقق من الخدمات

### التحقق من Frontends محلياً:

```bash
curl http://localhost:3000/health  # AI-Agent
curl http://localhost:3001/health  # CRM
curl http://localhost:3002/health  # AAA
```

### التحقق عبر NGINX:

```bash
curl http://ai-agent.bankid-sy.com/health
curl http://crm.bankid-sy.com/health
curl http://aaa.bankid-sy.com/health
```

---

## 🔍 مراقبة الخدمات

### Frontend Logs (PM2):

```bash
pm2 status
pm2 logs
pm2 logs ai-agent-frontend
pm2 logs crm-frontend
pm2 logs aaa-frontend
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

## 🛑 إيقاف الخدمات

### إيقاف Frontends:

```bash
# PM2
cd frontend
./pm2-stop.sh
# أو
pm2 stop all

# start-all.sh
cd frontend
./stop-all.sh
```

### إيقاف Backend:

```bash
cd backend
./stop.sh
```

---

## 🔧 Troubleshooting

### Port already in use:

```bash
# معرفة ما يستخدم الـ port
lsof -i :3000
lsof -i :3001
lsof -i :3002

# قتل العملية
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
lsof -ti:3002 | xargs kill -9
```

### NGINX issues:

```bash
# اختبار التكوين
sudo nginx -t

# عرض الأخطاء
sudo tail -f /var/log/nginx/error.log

# إعادة تحميل
sudo systemctl reload nginx

# إعادة تشغيل
sudo systemctl restart nginx
```

### Backend لا يعمل:

```bash
# التحقق من الحالة
curl http://localhost:8000/health

# عرض logs
cd backend
tail -f backend.log

# إعادة تشغيل
cd backend
./restart.sh
```

### CORS Errors:

تأكد من أن `backend/app/core/config.py` يحتوي على:
```python
CORS_ORIGINS = ["*"]
```

---

## 📊 حالة الخدمات

### التحقق من حالة PM2:

```bash
pm2 status
pm2 monit
```

### التحقق من حالة NGINX:

```bash
sudo systemctl status nginx
```

### التحقق من حالة Backend:

```bash
ps aux | grep uvicorn
```

---

## 🔄 إعادة التشغيل

### إعادة تشغيل كل شيء:

```bash
# Frontends
cd frontend
pm2 restart all

# Backend
cd backend
./restart.sh

# NGINX
sudo systemctl reload nginx
```

---

## 📚 المزيد من المعلومات

- **دليل شامل:** `COMPLETE_SETUP_GUIDE.md`
- **بدء سريع:** `QUICK_START.md`
- **ملخص الإعداد:** `SETUP_SUMMARY.md`

---

## ✅ Checklist النهائي

- [ ] ملفات NGINX منسوخة ومفعّلة
- [ ] NGINX تم إعادة تحميله
- [ ] Backend يعمل على port 8000
- [ ] AI-Agent frontend يعمل على port 3000
- [ ] CRM frontend يعمل على port 3001
- [ ] AAA frontend يعمل على port 3002
- [ ] جميع health checks تعمل
- [ ] يمكن الوصول للخدمات عبر الـ domains

---

**🎉 كل شيء جاهز!**

**آخر تحديث:** 2025-01-XX

