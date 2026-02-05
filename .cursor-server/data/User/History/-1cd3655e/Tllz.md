# 🎨 Brand Identity System - AI Dashboard

## نظرة عامة

نظام هوية بصرية كامل ومنظم للمنصة، يضمن التناسق والاحترافية في جميع المكونات.

---

## 🎨 1. نظام الألوان (Color System)

### Primary Colors
- **Primary**: `indigo-500` (#6366f1) - اللون الأساسي للعلامة التجارية
- **Primary Hover**: `indigo-600` - عند التمرير
- **Primary Active**: `indigo-700` - عند الضغط

### Status Colors
- **Success**: أخضر للعمليات الناجحة
- **Warning**: أصفر/برتقالي للتحذيرات
- **Error/Destructive**: أحمر للأخطاء
- **Info**: أزرق للمعلومات

### Neutral Colors
- **Background**: `slate-900` - الخلفية الرئيسية
- **Card**: `slate-900` - خلفية الكروت
- **Text Primary**: `white` - النص الأساسي
- **Text Secondary**: `slate-300` - النص الثانوي
- **Text Muted**: `slate-400` - النص الخافت
- **Border**: `slate-800/50` - الحدود

---

## 🔤 2. نظام الخطوط (Typography)

### Font Families
- **Sans**: Geist Sans (العناوين والنصوص)
- **Mono**: Geist Mono (الكود)

### Font Weights
- Light: 300
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700
- Extrabold: 800
- Black: 900

### Font Sizes
- h1: 2.25rem (36px)
- h2: 1.875rem (30px)
- h3: 1.5rem (24px)
- h4: 1.25rem (20px)
- h5: 1.125rem (18px)
- h6: 1rem (16px)
- Body: 1rem (16px)

### Letter Spacing
- Tight: -0.025em (للعناوين)
- Normal: 0 (للنصوص)
- Wide: 0.025em (للأحرف الكبيرة)

---

## 📏 3. نظام المسافات (Spacing System)

نظام قائم على 8px:

- **Micro**: 8px (0.5rem)
- **Small**: 16px (1rem)
- **Normal**: 24px (1.5rem)
- **Medium**: 32px (2rem)
- **Large**: 48px (3rem)
- **X-Large**: 64px (4rem)

---

## 🖼️ 4. نظام الأيقونات (Icon System)

### Icon Library
استخدام **Lucide React** للأيقونات

### Icon Sizes
- **Small**: 16px (1rem)
- **Medium**: 20px (1.25rem)
- **Large**: 24px (1.5rem)
- **X-Large**: 32px (2rem)

### Icon Style
- Outline style (موحد)
- نفس السماكة
- نفس الـ roundness

---

## 🧱 5. نظام المكونات (Component System)

### Buttons
- **Border Radius**: `rounded-lg` (8px)
- **Padding**: `px-4 py-2`
- **Transition**: `duration-200`
- **Shadow**: `shadow-sm` → `shadow-md` عند hover

### Cards
- **Border Radius**: `rounded-xl` (12px)
- **Padding**: `py-6 px-6`
- **Border**: `border-slate-800/50`
- **Shadow**: `shadow-sm` → `shadow-md` عند hover

### Input Fields
- **Border Radius**: `rounded-lg`
- **Border**: `border-slate-700`
- **Focus Ring**: `ring-2 ring-indigo-500`

---

## 🎯 6. نظام التفاعل (Interaction States)

### Hover States
- تغيير اللون تدريجياً
- إضافة shadow
- تغيير opacity

### Active States
- `scale(0.98)` عند الضغط
- لون أغمق

### Focus States
- Ring بارز
- لون `indigo-500`

### Disabled States
- `opacity-50`
- `cursor-not-allowed`

---

## 📜 7. نظام السكرول (Scrollbar System)

### Sidebar Scrollbar
- **Width**: 6px
- **Color**: `slate-700`
- **Border Radius**: `rounded-full`
- **Hover**: أفتح قليلاً

### Main Content Scrollbar
- **Width**: 8px
- **Color**: `slate-600`
- **Border Radius**: `rounded-md`

---

## 🎨 8. Sidebar Design

### Structure
- **Width**: 256px (w-64)
- **Background**: `slate-900`
- **Border**: `border-slate-800/50`

### Navigation Items
- **Active**: `bg-indigo-500 text-white`
- **Hover**: `bg-slate-800/50 text-white`
- **Default**: `text-slate-300`
- **Icons**: `text-slate-400` → `text-white` عند hover

### Group Headers
- **Font Size**: 10px
- **Font Weight**: Bold
- **Color**: `slate-500`
- **Uppercase**: Yes
- **Tracking**: Wider

### Scrollable
- Sidebar يحتوي على scroll تلقائي عند الحاجة
- استخدام `sidebar-scroll` class

---

## ✅ Best Practices

1. **استخدم نظام المسافات الموحد** - دائماً استخدم 8px multiples
2. **الألوان من النظام** - لا تستخدم ألوان عشوائية
3. **الخطوط موحدة** - استخدم Font weights المحددة
4. **التفاعلات متسقة** - نفس duration و easing
5. **الأيقونات من Lucide** - لا تخلط مكتبات مختلفة

---

## 📝 Usage Examples

### Button
```tsx
<Button variant="default">Primary Action</Button>
<Button variant="outline">Secondary Action</Button>
<Button variant="ghost">Tertiary Action</Button>
```

### Card
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Sidebar Item
```tsx
<Link href="/path" className="px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/50">
  <Icon className="w-4 h-4" />
  <span>Label</span>
</Link>
```

---

## 🚀 التوسع المستقبلي

النظام قابل للتوسع بسهولة:
- إضافة ألوان جديدة في `globals.css`
- إضافة مكونات جديدة تتبع نفس النظام
- تحديث الألوان من مكان واحد

---

**تم التحديث**: نظام الهوية البصرية الكامل مع Sidebar قابل للتمرير ✨

