# 🔧 NGINX Configuration Fix

## المشاكل التي تم إصلاحها

### 1. ❌ Login Timeout
**المشكلة**: Frontend كان يستدعي `/api/auth/login` لكن Backend endpoint هو `/api/identity/login`

**الحل**: 
- ✅ تحديث `app/crm/login/page.tsx` لاستخدام `/api/identity/login`
- ✅ إضافة timeout handling (10 ثواني)
- ✅ تحسين error messages

### 2. ❌ 403 Forbidden للخطوط (Fonts)
**المشكلة**: NGINX كان يرفض طلبات الخطوط (`geist-latin.woff2`)

**الحل**: 
- ✅ إضافة location block خاص للخطوط في `nginx-crm-complete.conf`
- ✅ إضافة `Access-Control-Allow-Origin` header
- ✅ إضافة caching للخطوط

### 3. ❌ WebSocket Connection Failed
**المشكلة**: HMR (Hot Module Replacement) WebSocket connections كانت تفشل

**الحل**:
- ✅ إضافة location block خاص لـ `/_next/webpack-hmr`
- ✅ إعداد WebSocket headers بشكل صحيح
- ✅ زيادة timeout للـ WebSocket connections

## 📋 خطوات التطبيق

### 1. تحديث NGINX Configuration

```bash
# نسخ الملف الجديد
sudo cp nginx-crm-complete.conf /etc/nginx/sites-available/crm.bankid-sy.com

# أو تحديث الملف الموجود
sudo nano /etc/nginx/sites-available/crm.bankid-sy.com
```

### 2. اختبار وإعادة تحميل NGINX

```bash
# اختبار التكوين
sudo nginx -t

# إذا كان كل شيء صحيح، أعد تحميل NGINX
sudo systemctl reload nginx
```

### 3. التحقق من Backend

تأكد أن Backend يعمل على port 8000:

```bash
# تحقق من حالة Backend
curl http://localhost:8000/health

# أو
curl http://localhost:8000/api/identity/login -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"test"}'
```

### 4. التحقق من Frontend

تأكد أن Frontend يعمل على port 3000:

```bash
# تحقق من Frontend
curl http://localhost:3000/health
```

## 🔍 Troubleshooting

### إذا استمرت مشكلة Login Timeout:

1. **تحقق من Backend logs**:
```bash
# إذا كان Backend يعمل في Docker
docker logs <backend-container-name>

# أو إذا كان يعمل مباشرة
tail -f /path/to/backend/logs
```

2. **تحقق من NGINX logs**:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

3. **تحقق من Firewall**:
```bash
# تأكد أن port 8000 و 3000 مفتوحة
sudo ufw status
```

### إذا استمرت مشكلة 403 للخطوط:

1. **تحقق من permissions**:
```bash
# تأكد أن NGINX يمكنه قراءة ملفات Frontend
sudo chown -R www-data:www-data /path/to/frontend/.next
```

2. **تحقق من CORS**:
- تأكد أن `Access-Control-Allow-Origin` موجود في response headers

### إذا استمرت مشكلة WebSocket:

1. **تحقق من NGINX version**:
```bash
nginx -v
# يجب أن يكون 1.3+ لدعم WebSocket
```

2. **تحقق من proxy headers**:
- تأكد أن `Upgrade` و `Connection` headers موجودة

## 📝 ملاحظات

- **Timeout**: تم تعيين timeout إلى 10 ثواني للـ login requests
- **Caching**: الخطوط يتم cache لمدة سنة
- **WebSocket**: HMR WebSocket connections لها timeout طويل (24 ساعة)

## ✅ التحقق النهائي

بعد تطبيق التغييرات:

1. ✅ افتح `https://crm.bankid-sy.com/login`
2. ✅ جرب تسجيل الدخول
3. ✅ تحقق من Console - يجب ألا يكون هناك أخطاء
4. ✅ تحقق من Network tab - يجب أن تكون جميع الطلبات ناجحة

---

**آخر تحديث**: 2025-01-XX

