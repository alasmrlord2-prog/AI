# CRM + IAM Frontend Documentation

## 📁 البنية الكاملة

```
frontend/app/
├── crm/                          ✅ CRM Management
│   └── tenants/
│       ├── page.tsx              ✅ قائمة Tenants
│       └── [tenantId]/
│           ├── page.tsx          ✅ Dashboard مع Tabs
│           ├── users/
│           │   └── page.tsx     ✅ إدارة المستخدمين
│           └── subscription/
│               └── page.tsx      ✅ إدارة الاشتراكات
│
└── iam/                          ✅ IAM / AAA UI
    ├── roles/
    │   └── page.tsx             ✅ إدارة الأدوار
    ├── permissions/
    │   └── page.tsx              ✅ Permission Matrix
    ├── policies/
    │   └── page.tsx              ✅ Zanzibar Policies
    └── access-control/
        └── page.tsx              ✅ Access Testing Tool
```

---

## 🔗 API Wrappers

تم إضافة API wrappers في `lib/api.ts`:

### CRM API
```typescript
import { crmApi } from "@/lib/api";

// Tenants
crmApi.listTenants(limit, offset)
crmApi.getTenantDashboard(tenantId)
crmApi.getTenantSummary(tenantId)

// Users
crmApi.getTenantUsers(tenantId)

// Departments & Projects
crmApi.getTenantDepartments(tenantId)
crmApi.getTenantProjects(tenantId, departmentId?)

// Usage & Analytics
crmApi.getTenantUsage(tenantId, days)

// Incidents & Audit
crmApi.getTenantIncidents(tenantId, limit, offset)
crmApi.getTenantAuditLogs(tenantId, options)
```

### Identity API
```typescript
import { identityApi } from "@/lib/api";

// Users
identityApi.createUser(userData)
identityApi.getUser(userId)
identityApi.updateUser(userId, userData)

// Tenants
identityApi.createTenant(tenantData)
identityApi.getTenant(tenantId)
identityApi.updateTenant(tenantId, tenantData)

// Sessions
identityApi.getSessions(userId)
identityApi.revokeSession(sessionId)

// API Tokens
identityApi.createApiToken(tokenData)
identityApi.listApiTokens(userId, tenantId?)
identityApi.revokeApiToken(tokenId, userId)
```

### Subscription API
```typescript
import { subscriptionApi } from "@/lib/api";

// Plans
subscriptionApi.getPlans()
subscriptionApi.getPlan(planId)

// Subscriptions
subscriptionApi.getSubscriptionStatus(tenantId)

// Usage
subscriptionApi.getUsage(subscriptionId, resourceType?)
subscriptionApi.checkUsageLimit(subscriptionId, resourceType, amount)
```

### Access API
```typescript
import { accessApi } from "@/lib/api";

// Roles
accessApi.getRoles()
accessApi.createRole(roleData)

// Permissions
accessApi.getPermissions()

// User Roles
accessApi.getUserRoles(userId, tenantId?)
accessApi.assignRole(userRoleData)
```

### Policy API
```typescript
import { policyApi } from "@/lib/api";

// Relations
policyApi.getRelations(options)
policyApi.createRelationTuple(tupleData)
policyApi.checkRelation(checkData)

// Rules
policyApi.getPolicyRules(tenantId?)
policyApi.createPolicyRule(ruleData)
```

---

## 📄 الصفحات

### 1. CRM - Tenants List
**Path:** `/crm/tenants`

**الميزات:**
- قائمة جميع Tenants
- Search و Filter
- Pagination
- عرض حالة الاشتراك
- عرض عدد المستخدمين
- Navigation إلى Tenant Dashboard

---

### 2. CRM - Tenant Dashboard
**Path:** `/crm/tenants/[tenantId]`

**الميزات:**
- Overview Tab: نظرة عامة + Subscription Status + Users Summary + Recent Activity
- Users Tab: رابط إلى صفحة Users
- Subscription Tab: رابط إلى صفحة Subscription
- Usage Analytics Tab: رسوم بيانية للاستهلاك
- Audit Logs Tab: سجل العمليات
- Incidents Tab: الحوادث

---

### 3. CRM - Users Management
**Path:** `/crm/tenants/[tenantId]/users`

**الميزات:**
- قائمة المستخدمين مع تفاصيل
- عرض Sessions النشطة
- عرض API Tokens
- Last Login Info (IP + Location)
- Revoke Sessions
- MFA Status

---

### 4. CRM - Subscription Management
**Path:** `/crm/tenants/[tenantId]/subscription`

**الميزات:**
- Current Subscription Details
- Usage & Limits (مع Progress Bars)
- Available Plans
- Upgrade/Downgrade (قريباً)
- Days Until Expiry Warning

---

### 5. IAM - Roles
**Path:** `/iam/roles`

**الميزات:**
- قائمة الأدوار
- Search
- Create Role Modal
- عرض Permissions لكل Role
- System Roles vs Custom Roles

---

### 6. IAM - Permissions
**Path:** `/iam/permissions`

**الميزات:**
- Permission Matrix Table
- Filter by Resource
- Filter by Action
- Search
- عرض Status (Active/Inactive)

---

### 7. IAM - Policies
**Path:** `/iam/policies`

**الميزات:**
- Relation Tuples Tab: عرض جميع العلاقات
- Policy Rules Tab: عرض القواعد
- Create Relation Tuple
- Create Policy Rule
- عرض Priority و Status

---

### 8. IAM - Access Control Testing
**Path:** `/iam/access-control`

**الميزات:**
- Relation Check: اختبار العلاقات (Zanzibar-style)
- Permission Check: اختبار الصلاحيات
- عرض النتائج مع التفاصيل
- عرض Matched Tuples
- عرض Paths (للعلاقات غير المباشرة)

---

## 🎨 Components المستخدمة

جميع الصفحات تستخدم:
- `Sidebar` - من `@/components/layout/Sidebar`
- `Header` - من `@/components/layout/Header`
- `Card`, `CardHeader`, `CardTitle`, `CardContent` - من `@/components/ui/card`
- `Button` - من `@/components/ui/button`
- `Input` - من `@/components/ui/input`

---

## 🚀 الاستخدام

### Navigation
```typescript
import { useRouter } from "next/navigation";

const router = useRouter();
router.push("/crm/tenants");
router.push(`/crm/tenants/${tenantId}`);
router.push(`/iam/roles`);
```

### Fetching Data
```typescript
import { crmApi } from "@/lib/api";

useEffect(() => {
  const fetchData = async () => {
    try {
      const data = await crmApi.getTenantDashboard(tenantId);
      setDashboard(data);
    } catch (error) {
      console.error("Error:", error);
    }
  };
  fetchData();
}, [tenantId]);
```

---

## 📝 ملاحظات

1. **Authentication**: جميع الصفحات تتطلب Authentication (يتم التحقق تلقائياً عبر `apiRequest`)

2. **Error Handling**: يتم معالجة الأخطاء في `apiRequest` wrapper

3. **Auto-refresh**: معظم الصفحات تعمل Auto-refresh كل 30 ثانية

4. **Responsive**: جميع الصفحات Responsive (Mobile + Desktop)

5. **Loading States**: جميع الصفحات تعرض Loading states

---

## 🔄 التوسعات المستقبلية

- [ ] Create/Edit Tenant Modal
- [ ] Create/Edit User Modal
- [ ] Role Details Page
- [ ] Permission Assignment UI
- [ ] Graph Visualization للـ Relations
- [ ] Advanced Filtering
- [ ] Export Data (CSV/JSON)
- [ ] Bulk Operations

---

**آخر تحديث:** 2025-01-XX

