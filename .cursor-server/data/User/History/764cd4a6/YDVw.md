# 🎨 ShiftWave Dashboard Theme - Usage Examples

هذا الملف يحتوي على أمثلة جاهزة لاستخدام ShiftWave Theme في الـ components.

---

## 📋 Table of Contents

1. [Sidebar Component](#sidebar-component)
2. [Card Components](#card-components)
3. [Button Components](#button-components)
4. [Chart Container](#chart-container)
5. [Top Bar](#top-bar)
6. [Input Fields](#input-fields)
7. [Tables](#tables)

---

## 🔹 Sidebar Component

### Sidebar Container

```tsx
// Sidebar Container
<div className="h-screen w-64 bg-sw-bg-sidebar border-r border-sw-border flex flex-col">
  {/* Sidebar Header */}
  <div className="h-14 flex items-center px-4 border-b border-sw-border">
    <span className="text-sm font-semibold text-sw-text-strong">
      SHIFTWAVE AI
    </span>
  </div>

  {/* Sidebar Content */}
  <div className="flex-1 overflow-y-auto sidebar-scroll px-3 py-4">
    {/* Active Menu Item */}
    <button className="w-full mt-2 flex items-center justify-between rounded-sw-btn bg-sw-gradient text-white text-xs font-semibold px-3 py-2.5 shadow-sw-soft">
      <span className="flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        Dashboard
      </span>
    </button>

    {/* Normal Menu Item */}
    <button className="w-full mt-2 flex items-center rounded-sw-btn px-3 py-2.5 text-xs text-[#6F819C] hover:bg-sw-bg-hover transition-colors">
      <span className="flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Agent Console
      </span>
    </button>

    {/* Another Normal Menu Item */}
    <button className="w-full mt-2 flex items-center rounded-sw-btn px-3 py-2.5 text-xs text-[#6F819C] hover:bg-sw-bg-hover transition-colors">
      <span className="flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Monitoring
      </span>
    </button>
  </div>
</div>
```

---

## 🔹 Card Components

### Default Dashboard Card

```tsx
// Default Card
<div className="rounded-sw-card bg-sw-bg-card border border-sw-border p-5 shadow-sm">
  <p className="text-xs text-sw-text-soft font-medium">Total Modules</p>
  <p className="mt-2 text-2xl font-bold text-sw-primary">31</p>
  <p className="mt-1 text-xs text-sw-text-muted">Active features</p>
</div>
```

### Card with Secondary Value

```tsx
// Card with Secondary Value
<div className="rounded-sw-card bg-sw-bg-card border border-sw-border p-5 shadow-sm">
  <p className="text-xs text-sw-text-soft font-medium">System Health</p>
  <p className="mt-2 text-2xl font-bold text-sw-primary">98%</p>
  <p className="mt-1 text-xs text-sw-secondary">+2.5% from last week</p>
</div>
```

### Card with Icon

```tsx
// Card with Icon
<div className="rounded-sw-card bg-sw-bg-card border border-sw-border p-5 shadow-sm hover:bg-sw-bg-hover transition-colors">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-xs text-sw-text-soft font-medium">CPU Usage</p>
      <p className="mt-2 text-2xl font-bold text-sw-primary">45%</p>
    </div>
    <div className="w-12 h-12 rounded-full bg-sw-primary/10 flex items-center justify-center">
      <svg className="w-6 h-6 text-sw-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    </div>
  </div>
</div>
```

---

## 🔹 Button Components

### Primary Button (Gradient)

```tsx
// Primary Button with Gradient
<button className="rounded-sw-btn bg-sw-gradient px-5 py-2.5 text-xs font-semibold text-white shadow-sw-soft hover:opacity-90 transition-opacity">
  Run Analysis
</button>
```

### Secondary Button (Outline)

```tsx
// Secondary Button
<button className="rounded-sw-btn border border-sw-primary text-sw-primary px-5 py-2.5 text-xs font-medium hover:bg-sw-bg-hover transition-colors">
  View Logs
</button>
```

### Danger Button

```tsx
// Danger Button
<button className="rounded-sw-btn bg-sw-danger text-white px-5 py-2.5 text-xs font-semibold hover:opacity-90 transition-opacity">
  Delete
</button>
```

### Button with Icon

```tsx
// Button with Icon
<button className="rounded-sw-btn bg-sw-gradient px-5 py-2.5 text-xs font-semibold text-white shadow-sw-soft hover:opacity-90 transition-opacity flex items-center gap-2">
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
  Add New
</button>
```

---

## 🔹 Chart Container

### Chart Card

```tsx
// Chart Container
<div className="rounded-sw-card bg-sw-bg-card border border-sw-border p-5">
  <div className="flex items-center justify-between mb-4">
    <h3 className="text-xs font-semibold text-sw-text-soft">
      CPU Trend
    </h3>
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-1.5">
        <div className="w-2 h-2 rounded-full bg-sw-primary"></div>
        <span className="text-xs text-sw-text-muted">CPU</span>
      </div>
      <div className="flex items-center gap-1.5">
        <div className="w-2 h-2 rounded-full bg-sw-secondary"></div>
        <span className="text-xs text-sw-text-muted">Memory</span>
      </div>
    </div>
  </div>
  
  {/* Chart Area */}
  <div className="h-48 bg-sw-bg-card-dark rounded-md p-3">
    {/* Place your chart library here (Chart.js, Recharts, etc.) */}
    <div className="h-full flex items-center justify-center text-sw-text-muted text-xs">
      Chart Component
    </div>
  </div>
</div>
```

### Chart Colors Reference

```tsx
// Chart Line Colors
const chartColors = {
  cpu: "#1399FF",        // sw-primary
  memory: "#00D1CE",     // sw-secondary
  network: "#4BB8FF",    // sw-primary-light
  disk: "#4AD1C8",       // sw-secondary-light
};
```

---

## 🔹 Top Bar

### Top Navigation Bar

```tsx
// Top Bar
<div className="h-14 bg-sw-bg-soft border-b border-sw-border flex items-center justify-between px-6">
  <div>
    <h1 className="text-base font-semibold text-sw-text-strong">
      Dashboard
    </h1>
    <p className="text-xs text-sw-text-muted mt-0.5">
      Cyber Intelligence • Automation • Observability
    </p>
  </div>
  
  <div className="flex items-center gap-3">
    <button className="rounded-sw-btn border border-sw-border bg-sw-bg-card px-3 py-1.5 text-xs text-sw-text-soft hover:bg-sw-bg-hover transition-colors">
      Settings
    </button>
    <div className="w-8 h-8 rounded-full bg-sw-primary/20 flex items-center justify-center">
      <span className="text-xs font-semibold text-sw-primary">U</span>
    </div>
  </div>
</div>
```

---

## 🔹 Input Fields

### Text Input

```tsx
// Text Input
<input
  type="text"
  className="w-full rounded-md bg-sw-bg-card-dark border border-sw-border px-3 py-2 text-sm text-sw-text placeholder-sw-text-muted focus:outline-none focus:ring-2 focus:ring-sw-primary focus:border-transparent"
  placeholder="Enter search query..."
/>
```

### Textarea

```tsx
// Textarea
<textarea
  className="w-full rounded-md bg-sw-bg-card-dark border border-sw-border px-3 py-2 text-sm text-sw-text placeholder-sw-text-muted focus:outline-none focus:ring-2 focus:ring-sw-primary focus:border-transparent resize-none"
  rows={4}
  placeholder="Enter description..."
/>
```

### Select Dropdown

```tsx
// Select Dropdown
<select className="w-full rounded-md bg-sw-bg-card-dark border border-sw-border px-3 py-2 text-sm text-sw-text focus:outline-none focus:ring-2 focus:ring-sw-primary focus:border-transparent">
  <option value="">Select option...</option>
  <option value="1">Option 1</option>
  <option value="2">Option 2</option>
</select>
```

---

## 🔹 Tables

### Table Component

```tsx
// Table
<div className="rounded-sw-card bg-sw-bg-card border border-sw-border overflow-hidden">
  <table className="w-full">
    {/* Table Header */}
    <thead className="bg-sw-bg-hover">
      <tr>
        <th className="px-4 py-3 text-left text-xs font-semibold text-sw-text-soft uppercase tracking-wider">
          Name
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-sw-text-soft uppercase tracking-wider">
          Status
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-sw-text-soft uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </thead>
    
    {/* Table Body */}
    <tbody className="divide-y divide-sw-border">
      <tr className="bg-sw-bg-card hover:bg-sw-bg-hover transition-colors">
        <td className="px-4 py-3 text-sm text-sw-text">
          Agent #1
        </td>
        <td className="px-4 py-3">
          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-sw-success/20 text-sw-success">
            Active
          </span>
        </td>
        <td className="px-4 py-3">
          <button className="text-xs text-sw-primary hover:text-sw-primary-light">
            View
          </button>
        </td>
      </tr>
      
      <tr className="bg-sw-bg-card hover:bg-sw-bg-hover transition-colors">
        <td className="px-4 py-3 text-sm text-sw-text">
          Agent #2
        </td>
        <td className="px-4 py-3">
          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-sw-warning/20 text-sw-warning">
            Warning
          </span>
        </td>
        <td className="px-4 py-3">
          <button className="text-xs text-sw-primary hover:text-sw-primary-light">
            View
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## 🎨 Color Usage Guidelines

### Primary Colors
- Use `sw-primary` (#1399FF) for main actions, links, and important values
- Use `sw-primary-light` (#4BB8FF) for hover states
- Use `sw-primary-dark` (#0D6BD0) for pressed/active states

### Secondary Colors
- Use `sw-secondary` (#00D1CE) for secondary highlights and complementary elements
- Use `sw-secondary-light` (#2EE3E0) for lighter accents

### Backgrounds
- Use `sw-bg` (#0A0F16) for main page background
- Use `sw-bg-card` (#121C27) for card backgrounds
- Use `sw-bg-card-dark` (#101621) for nested elements
- Use `sw-bg-hover` (#182332) for hover states

### Text Colors
- Use `sw-text` (#FFFFFF) for primary text
- Use `sw-text-soft` (#C8D1E0) for secondary text
- Use `sw-text-muted` (#8A94A6) for muted/disabled text
- Use `sw-text-strong` (#E4EBF5) for emphasized text

### Status Colors
- Use `sw-success` (#10B981) for success states
- Use `sw-warning` (#F59E0B) for warning states
- Use `sw-danger` (#EF4444) for error/danger states

---

## 📝 Notes

1. **Always use the theme colors** - لا تستخدم ألوان خارج النظام
2. **Consistent spacing** - استخدم نظام المسافات الموحد (xxs, xs, sm, md, lg, xl, 2xl)
3. **Border radius** - استخدم `rounded-sw-card` للكاردات و `rounded-sw-btn` للأزرار
4. **Gradient** - استخدم `bg-sw-gradient` للأزرار الرئيسية فقط
5. **Dark mode only** - الداشبورد داكنة دائماً، استخدم `dark` class في HTML

---

## 🚀 Quick Start

```tsx
// Example: Complete Dashboard Layout
<div className="flex h-screen bg-sw-bg">
  {/* Sidebar */}
  <Sidebar />
  
  {/* Main Content */}
  <div className="flex-1 flex flex-col">
    {/* Top Bar */}
    <TopBar />
    
    {/* Dashboard Content */}
    <div className="flex-1 overflow-y-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card />
        <Card />
        <Card />
        <Card />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartContainer />
        <ChartContainer />
      </div>
    </div>
  </div>
</div>
```

---

**Remember:** هذا الـ design system، لا تلعب بالألوان من راسك! 🎨

