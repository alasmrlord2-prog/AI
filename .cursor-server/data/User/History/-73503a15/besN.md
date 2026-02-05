# ⚡ حل سريع لمشكلة 502 Bad Gateway

## 🎯 المشكلة

```
HTTP 502: خطأ في السيرفر (Endpoint: /api/chat)
```

**السبب:** Backend لا يعمل أو لا يستجيب.

---

## 🚀 الحل في 3 خطوات

### الخطوة 1: التحقق من الحالة

```bash
cd /home/ai/ai-agent/backend
./check-backend.sh
```

---

### الخطوة 2: إصلاح Backend

#### إذا كان container لا يعمل:

```bash
cd /home/ai/ai-agent/backend
./start-fixed.sh
```

#### إذا كان container يعمل لكن لا يستجيب:

```bash
cd /home/ai/ai-agent/backend
./restart-fixed.sh
```

---

### الخطوة 3: التحقق

```bash
# انتظر 5-10 ثواني ثم
curl http://localhost:8000/health
```

إذا رأيت `{"status":"ok",...}` فالمشكلة حُلت! ✅

---

## 🔄 إذا لم يعمل

### جرب إعادة البناء:

```bash
cd /home/ai/ai-agent/backend

# إيقاف
docker-compose down

# إعادة بناء
docker-compose build --no-cache backend

# البدء
docker-compose up -d backend postgres

# انتظر 10 ثواني
sleep 10

# التحقق
curl http://localhost:8000/health
```

---

## 🆘 حل بديل: تشغيل Backend بدون Docker

إذا استمرت المشاكل مع Docker:

```bash
cd /home/ai/ai-agent/backend
./start-backend-direct.sh
```

**ملاحظة:** يحتاج Python و PostgreSQL مثبتين.

---

## 📝 Checklist

- [ ] Backend container يعمل
- [ ] `curl http://localhost:8000/health` يعمل
- [ ] NGINX configuration صحيح
- [ ] NGINX تم إعادة تحميله

---

## 📚 للمزيد

- **دليل شامل:** `502_ERROR_FIX.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`

---

**آخر تحديث:** 2025-01-XX

