# 🔧 إعدادات NGINX - SHIFTWAVE AI Platform

## 📋 البنية النهائية

النظام يتكون من **ثلاث واجهات منفصلة تماماً**:

### 1. Dashboard (واجهة المستخدم العادي)
- **Port:** 3000
- **Domain:** `ai-agent.bankid-sy.com` أو `dashboard.bankid-sy.com`
- **الوظيفة:** واجهة المستخدم العادي للدخول واستخدام النظام
- **NGINX Config:** `nginx-dashboard.conf`

### 2. CRM (واجهة إدارة Tenants/Users/Subscriptions)
- **Port:** 3001
- **Domain:** `crm.bankid-sy.com`
- **الوظيفة:** واجهة إدارة منفصلة تماماً عن Dashboard
  - إنشاء Tenants
  - إدارة Users
  - إدارة Subscriptions
  - إدارة Plans
  - Roles & Policies
- **NGINX Config:** `nginx-crm.conf`

### 3. AAA (واجهة إدارة Authentication/Authorization/Accounting)
- **Port:** 3002
- **Domain:** `aaa.bankid-sy.com`
- **الوظيفة:** واجهة إدارة AAA منفصلة تماماً
  - إدارة Sessions
  - إدارة Tokens
  - إدارة Roles
  - إدارة Policies
  - Audit Logs
- **NGINX Config:** `nginx-aaa.conf`

---

## 🚀 التثبيت والإعداد

### الخطوة 1: نسخ ملفات NGINX

```bash
sudo ./setup-all-services.sh
```

هذا السكربت سيقوم بـ:
- نسخ `nginx-dashboard.conf` → `/etc/nginx/sites-available/ai-agent.bankid-sy.com`
- نسخ `nginx-crm.conf` → `/etc/nginx/sites-available/crm.bankid-sy.com`
- نسخ `nginx-aaa.conf` → `/etc/nginx/sites-available/aaa.bankid-sy.com`
- تفعيل المواقع
- اختبار التكوين
- إعادة تحميل NGINX

### الخطوة 2: تشغيل Backend

```bash
cd backend
./start.sh
```

### الخطوة 3: تشغيل Frontends

```bash
cd frontend
./pm2-start.sh
```

أو:

```bash
./start-all.sh
```

---

## 📡 URLs النهائية

### Dashboard
- **URL:** http://ai-agent.bankid-sy.com
- **Port:** 3000
- **Backend API:** http://localhost:8000

### CRM
- **URL:** http://crm.bankid-sy.com
- **Port:** 3001
- **Backend API:** http://localhost:8000

### AAA
- **URL:** http://aaa.bankid-sy.com
- **Port:** 3002
- **Backend API:** http://localhost:8000

---

## 🔍 التحقق من الحالة

### فحص NGINX

```bash
# اختبار التكوين
sudo nginx -t

# عرض المواقع المفعلة
ls -la /etc/nginx/sites-enabled/

# عرض حالة NGINX
sudo systemctl status nginx

# عرض الـ logs
sudo tail -f /var/log/nginx/dashboard-access.log
sudo tail -f /var/log/nginx/crm-access.log
sudo tail -f /var/log/nginx/aaa-access.log
```

### فحص Frontends

```bash
# باستخدام PM2
pm2 status
pm2 logs

# أو فحص البورتات مباشرة
netstat -tlnp | grep -E '3000|3001|3002'
```

---

## 🛠️ استكشاف الأخطاء

### مشكلة: NGINX لا يعمل

```bash
# إعادة تحميل NGINX
sudo systemctl reload nginx

# أو إعادة التشغيل
sudo systemctl restart nginx

# فحص الأخطاء
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### مشكلة: Frontend لا يعمل على البورت المحدد

```bash
# إيقاف جميع Frontends
cd frontend
./stop-all.sh

# إعادة التشغيل
./pm2-start.sh

# أو فحص البورتات المستخدمة
lsof -i :3000
lsof -i :3001
lsof -i :3002
```

### مشكلة: 502 Bad Gateway

هذا يعني أن NGINX لا يستطيع الوصول إلى Frontend:

1. تأكد أن Frontend يعمل على البورت الصحيح:
   ```bash
   curl http://localhost:3000
   curl http://localhost:3001
   curl http://localhost:3002
   ```

2. تأكد من إعدادات NGINX:
   ```bash
   sudo cat /etc/nginx/sites-available/ai-agent.bankid-sy.com
   ```

3. تأكد من أن Backend يعمل:
   ```bash
   curl http://localhost:8000/health
   ```

---

## 📝 ملاحظات مهمة

1. **كل واجهة منفصلة تماماً:**
   - Dashboard لا يحتوي على CRM أو AAA
   - CRM واجهة إدارة منفصلة
   - AAA واجهة إدارة منفصلة

2. **جميع الواجهات تتصل بنفس Backend:**
   - Backend على port 8000
   - جميع الواجهات تستخدم `/api/` للوصول إلى Backend

3. **البنية النظيفة:**
   - كل خدمة لها ملف NGINX منفصل
   - كل خدمة تعمل على بورت منفصل
   - كل خدمة لها logs منفصلة

---

## ✅ التحقق النهائي

بعد الإعداد، تأكد من:

- [ ] Dashboard يعمل على http://ai-agent.bankid-sy.com
- [ ] CRM يعمل على http://crm.bankid-sy.com
- [ ] AAA يعمل على http://aaa.bankid-sy.com
- [ ] Backend يعمل على http://localhost:8000
- [ ] جميع الـ logs تعمل بشكل صحيح
- [ ] لا توجد أخطاء في NGINX

---

**تم إنشاء هذا الملف تلقائياً - آخر تحديث: $(date)**

