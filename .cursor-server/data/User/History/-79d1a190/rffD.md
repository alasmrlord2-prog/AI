# 🔗 CRM + AAA Integration Guide

## ✅ ما تم إنجازه

### 1. 🎨 CRM Theme كامل
- ✅ تحديث `tailwind.config.js` بإضافة ألوان CRM:
  - `sw.primary`: #00A0E9
  - `sw.primaryDark`: #0081BA
  - `sw.accent`: #34D1BF
  - `sw.bg`: #F7F9FB
  - `sw.surface`: #FFFFFF
  - `sw.text`: #0A0A0A
  - `sw.textLight`: #4A4A4A
  - `sw.border`: #E5E9EF

- ✅ تحديث CRM Components:
  - `CRMSidebar.tsx` - يستخدم ألوان CRM الجديدة
  - `CRMHeader.tsx` - موجود
  - `app/crm/layout.tsx` - يستخدم ألوان CRM
  - `app/crm/page.tsx` - Dashboard محدث
  - `app/crm/tenants/page.tsx` - Tenant Cards محدثة

### 2. 🔐 AAA Theme كامل
- ✅ إضافة ألوان AAA في `tailwind.config.js`:
  - `swAuth.bg`: #FFFFFF
  - `swAuth.surface`: #FAFBFC
  - `swAuth.darkBg`: #0C1320
  - `swAuth.darkSurface`: #151E2E
  - `swAuth.primary`: #00A0E9
  - `swAuth.warning`: #F59E0B
  - `swAuth.danger`: #EF4444

- ✅ إنشاء AAA Components:
  - `components/aaa/AAASidebar.tsx` - Sidebar للـ AAA
  - `components/aaa/AAAHeader.tsx` - Header للـ AAA
  - `app/aaa/layout.tsx` - Layout للـ AAA

- ✅ إنشاء صفحات AAA:
  - `app/aaa/login/page.tsx` - صفحة تسجيل الدخول
  - `app/aaa/page.tsx` - Dashboard
  - `app/aaa/tokens/page.tsx` - إدارة Tokens
  - `app/aaa/sessions/page.tsx` - إدارة Sessions
  - `app/aaa/users/page.tsx` - إدارة Users
  - `app/aaa/audit/page.tsx` - Audit Logs

### 3. 🔗 ربط CRM مع AAA

#### عند إنشاء User في CRM:
1. ✅ User يتم إنشاؤه عبر `/api/identity/users`
2. ✅ User يمكنه تسجيل الدخول إلى AAA عبر `/aaa/login`
3. ✅ User يمكنه الوصول إلى Dashboard في `/aaa`
4. ✅ زر "Open AAA Dashboard" في صفحة Users في CRM

#### التدفق:
```
CRM → Create User → User Created → User can login to AAA → AAA Dashboard
```

### 4. 🌐 NGINX Configuration

تم إنشاء ملف `nginx-aaa.conf` لدعم AAA:
- Frontend على port 3000
- Backend API على port 8000
- WebSocket support
- Health check endpoint

## 📋 كيفية الاستخدام

### 1. تفعيل NGINX Config

```bash
# نسخ الملف
sudo cp nginx-aaa.conf /etc/nginx/sites-available/aaa.bankid-sy.com

# إنشاء symlink
sudo ln -sf /etc/nginx/sites-available/aaa.bankid-sy.com /etc/nginx/sites-enabled/

# اختبار وإعادة تحميل
sudo nginx -t
sudo systemctl reload nginx
```

### 2. الوصول إلى الأنظمة

- **CRM**: `https://crm.bankid-sy.com`
- **AAA**: `https://aaa.bankid-sy.com`
- **Agent Dashboard**: `https://agent.bankid-sy.com`

### 3. إنشاء User من CRM

1. افتح CRM Dashboard
2. اذهب إلى Tenants → Select Tenant → Users
3. اضغط "Add User"
4. بعد إنشاء User، يمكنك:
   - رؤية User في صفحة Users
   - الضغط على "Open AAA Dashboard" للدخول إلى AAA

### 4. تسجيل الدخول إلى AAA

1. افتح `/aaa/login`
2. استخدم نفس credentials التي تم إنشاؤها في CRM
3. بعد تسجيل الدخول، يمكنك:
   - عرض Tokens
   - إدارة Sessions
   - عرض Users
   - مراجعة Audit Logs

## 🎨 الألوان المستخدمة

### CRM Theme
```javascript
sw: {
  primary: '#00A0E9',      // أزرق رئيسي
  primaryDark: '#0081BA',  // أزرق داكن
  accent: '#34D1BF',       // أخضر فاتح
  bg: '#F7F9FB',          // خلفية
  surface: '#FFFFFF',      // سطح
  text: '#0A0A0A',        // نص
  textLight: '#4A4A4A',   // نص فاتح
  border: '#E5E9EF',      // حدود
}
```

### AAA Theme
```javascript
swAuth: {
  bg: '#FFFFFF',          // خلفية بيضاء
  surface: '#FAFBFC',     // سطح فاتح
  darkBg: '#0C1320',      // خلفية داكنة
  darkSurface: '#151E2E', // سطح داكن
  primary: '#00A0E9',     // أزرق رئيسي
  warning: '#F59E0B',     // تحذير
  danger: '#EF4444',      // خطر
}
```

## 🔐 Authentication Flow

1. User يتم إنشاؤه في CRM
2. User يحصل على credentials (email + password)
3. User يسجل الدخول إلى AAA
4. AAA يعيد JWT token
5. Token يُستخدم للوصول إلى:
   - AAA Dashboard
   - API endpoints
   - Protected resources

## 📝 ملاحظات مهمة

1. **Shared Backend**: CRM و AAA يستخدمان نفس Backend (port 8000)
2. **Shared Frontend**: يمكن استخدام نفس Frontend (port 3000) أو منفصل
3. **Authentication**: نفس نظام Authentication للأنظمة
4. **User Context**: عند فتح AAA من CRM، يتم حفظ user context

## 🚀 الخطوات التالية

- [ ] إضافة RBAC للتحكم في الوصول
- [ ] إضافة MFA للـ AAA
- [ ] تحسين UI/UX
- [ ] إضافة Analytics Dashboard
- [ ] إضافة Audit Logs كاملة

---

**آخر تحديث**: 2025-01-XX

