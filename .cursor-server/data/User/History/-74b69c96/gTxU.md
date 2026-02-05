# 🎯 CRM Setup Guide

## ✅ ما تم إنجازه

تم إنشاء واجهة CRM مستقلة تماماً عن الداشبورد الرئيسي بنفس هوية Shiftwave:

### المكونات الجديدة:

1. **Layout مستقل** (`/app/crm/layout.tsx`)
   - Sidebar خاص بالـ CRM
   - Header خاص بالـ CRM
   - تصميم منفصل تماماً عن الداشبورد

2. **صفحة Login** (`/app/crm/login/page.tsx`)
   - تصميم احترافي بنفس هوية Shiftwave
   - Gradient background
   - Authentication check

3. **صفحات CRM محدثة:**
   - `/crm` - Dashboard الرئيسي
   - `/crm/tenants` - قائمة Tenants
   - `/crm/tenants/[tenantId]` - Tenant Dashboard مع Tabs

4. **Components خاصة:**
   - `CRMSidebar.tsx` - Sidebar خاص بالـ CRM
   - `CRMHeader.tsx` - Header خاص بالـ CRM

## 🔧 إعداد NGINX

### الخطوات:

1. **انسخ ملف الإعداد:**
```bash
sudo cp nginx-crm.conf /etc/nginx/conf.d/crm.conf
```

2. **عدّل المسارات حسب بيئتك:**
   - إذا كنت تستخدم Cloudflare، احذف سطور SSL
   - إذا كنت تستخدم Let's Encrypt، عدّل مسارات الشهادات

3. **اختبر الإعداد:**
```bash
sudo nginx -t
```

4. **أعد تحميل NGINX:**
```bash
sudo systemctl reload nginx
```

### DNS Configuration

تأكد من أن DNS Record مضبوط في Cloudflare:

```
Type: A
Name: crm
Content: 52.59.234.129
Proxy: ON (الغمامة البرتقالية)
```

## 🎨 التصميم

الواجهة تستخدم نفس هوية Shiftwave:

- **الألوان الأساسية:**
  - Primary: `#00A0E9` (sw-blue)
  - Accent: `#34D1BF` (sw-teal)
  - Background: `#F7F9FB` (Light) / `#0F172A` (Dark)

- **الخطوط:**
  - English: Inter
  - Arabic: Cairo

- **التصميم:**
  - Clean SaaS style
  - Cards مع borders ناعمة
  - Hover effects
  - Responsive design

## 🔐 Authentication

- الواجهة تتحقق من وجود `auth_token` في localStorage
- إذا لم يكن موجود، يتم التوجيه إلى `/crm/login`
- يجب إضافة Role-based access control في Backend للتحقق من `crm_admin` role

## 📝 ملاحظات

- الواجهة مستقلة تماماً عن الداشبورد الرئيسي
- يمكن الوصول إليها من `https://crm.bankid-sy.com`
- جميع الصفحات تستخدم نفس Layout الخاص بالـ CRM
- التصميم متجاوب ويعمل على جميع الأجهزة

## 🚀 الخطوات التالية

1. إضافة Role-based access control في Backend
2. إضافة Create User functionality
3. إضافة صفحات إضافية (Analytics, Audit Logs, etc.)
4. إضافة Middleware للتحقق من الصلاحيات

