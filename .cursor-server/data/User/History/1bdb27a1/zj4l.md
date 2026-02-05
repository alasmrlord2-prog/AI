# 🎨 ShiftWave Dashboard Theme - Light + Dark Mode

## ✨ المميزات

- ✅ **Light Mode** (نوع 2) - فاتح، نظيف، قابل للاستخدام
- ✅ **Dark Mode** - داكن، احترافي
- ✅ **تبديل تلقائي** بين الوضعين
- ✅ **حفظ التفضيل** في localStorage
- ✅ **دعم System Preference** - يتبع إعدادات النظام تلقائياً
- ✅ **بدون Flash** - تطبيق فوري قبل render الصفحة

---

## 📦 الملفات المطلوبة

تم إنشاء/تحديث الملفات التالية:

1. **`tailwind.config.js`** - يستخدم CSS variables
2. **`app/globals.css`** - يحتوي على CSS variables للوضعين
3. **`components/ui/theme-toggle.tsx`** - زر التبديل بين الوضعين
4. **`app/theme-script.tsx`** - script لتطبيق الـ theme قبل render
5. **`app/layout.tsx`** - محدّث لدعم التبديل التلقائي
6. **`SHIFTWAVE_THEME_EXAMPLES.md`** - أمثلة استخدام كاملة

---

## 🚀 الاستخدام السريع

### 1. استخدام ThemeToggle Component

```tsx
import { ThemeToggle } from "@/components/ui/theme-toggle";

// في أي مكان في الـ UI
<ThemeToggle />
```

### 2. استخدام الألوان في Tailwind

```tsx
// الألوان تتغير تلقائياً بين Light/Dark
<div className="bg-sw-bg-card border border-sw-border text-sw-text">
  <p className="text-sw-text-soft">Secondary text</p>
  <p className="text-sw-text-muted">Muted text</p>
</div>

// Gradient Button (يعمل في الوضعين)
<button className="bg-gradient-to-r from-sw-blue to-sw-teal text-white">
  Click me
</button>
```

### 3. استخدام CSS Variables مباشرة

```css
.my-component {
  background: var(--sw-bg-card);
  color: var(--sw-text);
  border: 1px solid var(--sw-border);
}
```

---

## 🎯 الألوان الأساسية

### Brand Colors (مشتركة بين الوضعين)

| المتغير | القيمة | الاستخدام |
|---------|--------|-----------|
| `sw-blue` | `#1399FF` | الأزرار الرئيسية، الروابط |
| `sw-teal` | `#00D1CE` | العناصر الثانوية |
| `sw-blue-light` | `#4BB8FF` | حالات hover |
| `sw-teal-light` | `#2EE3E0` | تمييزات خفيفة |

### Background Colors (تتغير تلقائياً)

#### Light Mode
- `sw-bg`: `#F5F7FA` - خلفية الصفحة
- `sw-bg-card`: `#FFFFFF` - خلفية الكاردات
- `sw-bg-soft`: `#EEF1F5` - خلفية الأقسام
- `sw-bg-hover`: `#F0F4F8` - حالات hover
- `sw-bg-sidebar`: `#FFFFFF` - خلفية Sidebar

#### Dark Mode
- `sw-bg`: `#0A0F16` - خلفية الصفحة
- `sw-bg-card`: `#121C27` - خلفية الكاردات
- `sw-bg-soft`: `#0E1622` - خلفية الأقسام
- `sw-bg-hover`: `#182332` - حالات hover
- `sw-bg-sidebar`: `#0A1A2F` - خلفية Sidebar

### Text Colors (تتغير تلقائياً)

#### Light Mode
- `sw-text`: `#0A1A2F` - النص الرئيسي
- `sw-text-soft`: `#1F2937` - النص الثانوي
- `sw-text-muted`: `#6B7280` - النص المهمل

#### Dark Mode
- `sw-text`: `#FFFFFF` - النص الرئيسي
- `sw-text-soft`: `#C8D1E0` - النص الثانوي
- `sw-text-muted`: `#8A94A6` - النص المهمل

### Status Colors (مشتركة)

- `sw-success`: `#10B981`
- `sw-warning`: `#F59E0B`
- `sw-danger`: `#EF4444`

---

## 🔧 كيفية عمل النظام

### 1. CSS Variables

جميع الألوان مخزنة في CSS variables في `globals.css`:

```css
:root {
  /* Light Mode Colors */
  --sw-bg: #F5F7FA;
  --sw-text: #0A1A2F;
  /* ... */
}

.dark {
  /* Dark Mode Colors */
  --sw-bg: #0A0F16;
  --sw-text: #FFFFFF;
  /* ... */
}
```

### 2. Tailwind Config

`tailwind.config.js` يستخدم CSS variables:

```js
colors: {
  "sw-bg": "var(--sw-bg)",
  "sw-text": "var(--sw-text)",
  // ...
}
```

### 3. Theme Script

`theme-script.tsx` يطبق الـ theme قبل render الصفحة (يمنع flash).

### 4. ThemeToggle Component

يحفظ التفضيل في localStorage ويطبق الـ theme فوراً.

---

## 📚 أمثلة الاستخدام

راجع ملف **`SHIFTWAVE_THEME_EXAMPLES.md`** للحصول على:
- Theme Toggle Button
- Sidebar component (Light + Dark)
- Card components (Light + Dark)
- Button components
- Chart containers
- Tables
- Input fields

---

## ⚠️ قواعد مهمة

1. **استخدم CSS variables دائماً** - لا تستخدم ألوان ثابتة
2. **استخدم Tailwind classes** - `bg-sw-bg-card`, `text-sw-text`, إلخ
3. **Shadows** - استخدم `shadow-sw-card` للـ Light و `dark:shadow-sw-card-dark` للـ Dark
4. **Gradient** - `bg-gradient-to-r from-sw-blue to-sw-teal` يعمل في الوضعين
5. **لا تخترع ألوان** - استخدم فقط ألوان ShiftWave

---

## 🔗 الخطوط

- **English**: Inter (يتم تحميله تلقائياً من Google Fonts)
- **Arabic**: Cairo (يتم تحميله تلقائياً من Google Fonts)

---

## 🎯 مثال كامل - Dashboard Layout

```tsx
import { ThemeToggle } from "@/components/ui/theme-toggle";

export default function Dashboard() {
  return (
    <div className="flex h-screen bg-sw-bg">
      {/* Sidebar */}
      <div className="w-64 bg-sw-bg-sidebar border-r border-sw-border">
        <div className="p-4 text-sw-text-strong font-semibold">
          SHIFTWAVE AI
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="h-14 bg-sw-bg-soft border-b border-sw-border flex items-center justify-between px-6">
          <h1 className="text-base font-semibold text-sw-text-strong">
            Dashboard
          </h1>
          <ThemeToggle />
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-sw-card bg-sw-bg-card border border-sw-border p-5 shadow-sw-card dark:shadow-sw-card-dark">
              <p className="text-xs text-sw-text-soft">Total Modules</p>
              <p className="mt-2 text-2xl font-bold text-sw-blue">31</p>
            </div>
            {/* More cards... */}
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## 📝 ملاحظات للمطور

> "التصميم هو ShiftWave theme، أي لون برا هالسيستم = مرفوض"

- كل component يتكيف تلقائياً مع Light/Dark mode
- استخدم الملفات المرفقة كمرجع عند بناء أي component جديد
- الألوان الأساسية (Blue, Teal) مشتركة بين الوضعين
- Backgrounds و Text colors تتغير تلقائياً

---

## 🎉 جاهز!

الآن عندك نظام Theme كامل يدعم Light + Dark mode مثل GitHub, Notion, Linear, Supabase!

**كل component يتكيف تلقائياً - لا حاجة لإعادة كتابة أي شيء!** 🚀
