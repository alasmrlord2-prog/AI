# 🔧 Theme Debug Guide

## المشكلة: كل شيء يبقى غامق (داكن)

### الحل السريع:

1. **افتح Developer Console** (F12)
2. **شغّل هذا الكود**:

```javascript
// مسح localStorage
localStorage.removeItem('theme');

// إزالة class dark من html
document.documentElement.classList.remove('dark');

// إعادة تحميل الصفحة
location.reload();
```

### التحقق من الـ Theme:

```javascript
// تحقق من localStorage
console.log('Theme saved:', localStorage.getItem('theme'));

// تحقق من class dark
console.log('Has dark class:', document.documentElement.classList.contains('dark'));

// تحقق من CSS variables
const root = getComputedStyle(document.documentElement);
console.log('Background:', root.getPropertyValue('--sw-bg'));
console.log('Text:', root.getPropertyValue('--sw-text'));
```

### القيم المتوقعة:

**Light Mode:**
- `--sw-bg`: `#F5F7FA` (فاتح)
- `--sw-bg-card`: `#FFFFFF` (أبيض)
- `--sw-text`: `#0A1A2F` (داكن)

**Dark Mode:**
- `--sw-bg`: `#0A0F16` (داكن)
- `--sw-bg-card`: `#121C27` (داكن)
- `--sw-text`: `#FFFFFF` (فاتح)

### إذا لم يعمل:

1. **امسح Cache**:
   - Ctrl+Shift+R (Windows/Linux)
   - Cmd+Shift+R (Mac)

2. **تحقق من الـ HTML**:
   - يجب أن يكون `<html>` بدون class `dark` في Light mode
   - يجب أن يكون `<html class="dark">` في Dark mode

3. **تحقق من الـ CSS**:
   - افتح DevTools → Elements → Styles
   - تحقق من أن `--sw-bg` و `--sw-text` تتغير حسب الوضع

