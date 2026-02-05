# 🗺️ كيف تصل لكل واجهة - How to Access Each Interface

## 🚀 البدء السريع

### 1. شغّل النظام

```bash
# تشغيل كل شيء
docker-compose up -d

# أو Backend فقط
cd backend && ./start.sh

# أو Frontend فقط
cd frontend && ./start.sh
```

### 2. أنشئ البيانات الأولية

```bash
cd backend
python scripts/setup_initial_data.py
```

### 3. سجّل دخول

افتح: **http://localhost:3000/login**

---

## 📍 الواجهات - URLs المباشرة

### 🔐 Authentication

| الواجهة | URL | الوظيفة |
|---------|-----|---------|
| **Login** | `http://localhost:3000/login` | تسجيل الدخول |

---

### 🏢 CRM Pages

| الواجهة | URL | الوظيفة |
|---------|-----|---------|
| **Tenants List** | `http://localhost:3000/crm/tenants` | قائمة Tenants |
| **Tenant Dashboard** | `http://localhost:3000/crm/tenants/{tenant_id}` | Dashboard شامل |
| **Users Management** | `http://localhost:3000/crm/tenants/{tenant_id}/users` | إدارة المستخدمين |
| **Subscription** | `http://localhost:3000/crm/tenants/{tenant_id}/subscription` | إدارة الاشتراكات |

---

### 🔐 IAM Pages

| الواجهة | URL | الوظيفة |
|---------|-----|---------|
| **Roles** | `http://localhost:3000/iam/roles` | إدارة الأدوار |
| **Permissions** | `http://localhost:3000/iam/permissions` | Permission Matrix |
| **Policies** | `http://localhost:3000/iam/policies` | Zanzibar Policies |
| **Access Control** | `http://localhost:3000/iam/access-control` | Access Testing |

---

## 🎯 خطوات الوصول التفصيلية

### 1️⃣ تسجيل الدخول

```
1. افتح المتصفح
2. اذهب إلى: http://localhost:3000/login
3. أدخل Email و Password
4. اضغط Login
```

**بعد تسجيل الدخول:**
- Token رح يتم حفظه تلقائياً
- رح يتم Redirect للـ Dashboard

---

### 2️⃣ الوصول لـ CRM

#### أ) قائمة Tenants

**الطريقة 1: من القائمة الجانبية**
```
Dashboard → CRM → Tenants
```

**الطريقة 2: مباشرة**
```
http://localhost:3000/crm/tenants
```

---

#### ب) Tenant Dashboard

**الطريقة 1: من قائمة Tenants**
```
1. اذهب إلى: /crm/tenants
2. اضغط على أي Tenant من القائمة
```

**الطريقة 2: مباشرة (تحتاج tenant_id)**
```
http://localhost:3000/crm/tenants/{tenant_id}
```

**كيف تحصل على tenant_id؟**
- من قائمة Tenants → اضغط على Tenant → شوف الـ URL
- أو من API: `GET /api/crm/tenants`

---

#### ج) إدارة المستخدمين

**الطريقة 1: من Dashboard**
```
1. اذهب إلى: /crm/tenants/{tenant_id}
2. اضغط على Tab "Users"
3. اضغط "View All Users"
```

**الطريقة 2: مباشرة**
```
http://localhost:3000/crm/tenants/{tenant_id}/users
```

---

#### د) إدارة الاشتراكات

**الطريقة 1: من Dashboard**
```
1. اذهب إلى: /crm/tenants/{tenant_id}
2. اضغط على Tab "Subscription"
3. اضغط "Manage Subscription"
```

**الطريقة 2: مباشرة**
```
http://localhost:3000/crm/tenants/{tenant_id}/subscription
```

---

### 3️⃣ الوصول لـ IAM

#### أ) إدارة الأدوار

**الطريقة 1: من القائمة الجانبية**
```
Dashboard → IAM → Roles
```

**الطريقة 2: مباشرة**
```
http://localhost:3000/iam/roles
```

---

#### ب) Permission Matrix

**الطريقة 1: من القائمة الجانبية**
```
Dashboard → IAM → Permissions
```

**الطريقة 2: مباشرة**
```
http://localhost:3000/iam/permissions
```

---

#### ج) Zanzibar Policies

**الطريقة 1: من القائمة الجانبية**
```
Dashboard → IAM → Policies
```

**الطريقة 2: مباشرة**
```
http://localhost:3000/iam/policies
```

---

#### د) Access Control Testing

**الطريقة 1: من القائمة الجانبية**
```
Dashboard → IAM → Access Control
```

**الطريقة 2: مباشرة**
```
http://localhost:3000/iam/access-control
```

---

## 🔗 Navigation Flow

### من Login:
```
Login Page
  ↓
Dashboard (Home)
  ↓
CRM / IAM
```

### من CRM:
```
Tenants List
  ↓
Tenant Dashboard (Tabs)
  ↓
Users / Subscription Pages
```

### من IAM:
```
Roles → Permissions → Policies → Access Control
```

---

## 📱 مثال عملي كامل

### السيناريو: إدارة Tenant جديد

**الخطوة 1: تسجيل الدخول**
```
URL: http://localhost:3000/login
Email: admin@example.com
Password: [your password]
```

**الخطوة 2: الذهاب لـ CRM**
```
URL: http://localhost:3000/crm/tenants
أو: من القائمة الجانبية → CRM → Tenants
```

**الخطوة 3: اختيار Tenant**
```
من قائمة Tenants → اضغط على Tenant
URL: http://localhost:3000/crm/tenants/{tenant_id}
```

**الخطوة 4: استكشاف Dashboard**
```
- Overview Tab: نظرة عامة
- Users Tab: عرض المستخدمين
- Subscription Tab: حالة الاشتراك
- Usage Tab: الاستهلاك
- Audit Tab: سجل العمليات
- Incidents Tab: الحوادث
```

**الخطوة 5: إدارة المستخدمين**
```
من Dashboard → Users Tab → "View All Users"
URL: http://localhost:3000/crm/tenants/{tenant_id}/users
```

**الخطوة 6: إدارة الاشتراك**
```
من Dashboard → Subscription Tab → "Manage Subscription"
URL: http://localhost:3000/crm/tenants/{tenant_id}/subscription
```

---

## 🔧 Troubleshooting

### لا أستطيع الوصول للصفحة؟

1. **تحقق من Docker:**
   ```bash
   docker-compose ps
   ```

2. **تحقق من Logs:**
   ```bash
   docker-compose logs frontend
   docker-compose logs backend
   ```

3. **تحقق من Authentication:**
   - افتح Developer Tools (F12)
   - Application → Local Storage
   - تحقق من وجود `auth_token`

### الصفحة فارغة؟

1. **تحقق من Console:**
   - F12 → Console
   - شوف الأخطاء

2. **تحقق من Network:**
   - F12 → Network
   - شوف API Calls

3. **تحقق من Backend:**
   ```bash
   curl http://localhost:8000/health
   ```

---

## 📊 API Endpoints

### Identity
- `POST /api/identity/login` - تسجيل الدخول
- `GET /api/identity/users` - قائمة المستخدمين
- `GET /api/identity/tenants` - قائمة Tenants

### CRM
- `GET /api/crm/tenants` - قائمة Tenants
- `GET /api/crm/tenants/{id}/dashboard` - Dashboard
- `GET /api/crm/tenants/{id}/users` - المستخدمين
- `GET /api/crm/tenants/{id}/usage` - الاستهلاك

### Subscription
- `GET /api/subscription/plans` - الخطط
- `GET /api/subscription/tenants/{id}/subscription` - حالة الاشتراك

### Access
- `GET /api/access/roles` - الأدوار
- `GET /api/access/permissions` - الصلاحيات

### Policy
- `GET /api/policy/relations` - Relations
- `POST /api/policy/check` - التحقق من Relation

**API Docs:** http://localhost:8000/docs

---

## 🎯 Quick Reference

### بعد تسجيل الدخول:

```
CRM Tenants → /crm/tenants
Tenant Dashboard → /crm/tenants/{id}
Users → /crm/tenants/{id}/users
Subscription → /crm/tenants/{id}/subscription

IAM Roles → /iam/roles
IAM Permissions → /iam/permissions
IAM Policies → /iam/policies
IAM Access Control → /iam/access-control
```

---

**آخر تحديث:** 2025-01-XX

