# 🧪 Testing Guide - CRM, AAA, AI Agent Endpoints

## 📋 نظرة عامة

هذا الدليل يشرح كيفية اختبار جميع الـ endpoints في النظام.

---

## 🚀 الخطوات السريعة

### 1. تشغيل Backend

```bash
cd /home/ai/ai-agent
./backend-start.sh
```

انتظر حتى ترى:
```
✅ Backend is running!
   API: http://localhost:8000
   Docs: http://localhost:8000/docs
```

### 2. اختبار جميع الـ Endpoints

```bash
./test-all-endpoints.sh
```

هذا السكريبت يختبر:
- ✅ Health check
- ✅ Authentication endpoints
- ✅ CRM endpoints
- ✅ AAA/Identity endpoints
- ✅ Access/Policy endpoints
- ✅ Subscription endpoints
- ✅ AI Agent endpoints
- ✅ Dashboard endpoints

### 3. اختبار الـ Workflow الكامل (CRM → AAA → AI Agent)

```bash
./test-crm-aaa-workflow.sh
```

هذا السكريبت يختبر:
1. ✅ إنشاء Tenant
2. ✅ إنشاء Employee User
3. ✅ Employee Login
4. ✅ الوصول للـ AI Agent
5. ✅ التحقق من وجود AAA File

---

## 📝 الاختبار اليدوي

### 1. التحقق من Backend

```bash
curl http://localhost:8000/health
```

**النتيجة المتوقعة:**
```json
{"status":"healthy"}
```

### 2. فتح API Documentation

افتح المتصفح على:
```
http://localhost:8000/docs
```

هنا يمكنك رؤية جميع الـ endpoints واختبارها مباشرة.

---

## 🔐 اختبار Authentication

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

**النتيجة المتوقعة:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin"
  }
}
```

### حفظ Token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"
```

---

## 📊 اختبار CRM Endpoints

### إنشاء Tenant

```bash
curl -X POST http://localhost:8000/api/crm/tenants \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "شركة دجاجتي",
    "type": "company",
    "contact_email": "owner@dajajati.com",
    "contact_phone": "+963123456789",
    "subscription_plan": "AI_AGENT_PRO",
    "max_users": 10
  }'
```

### قائمة Tenants

```bash
curl http://localhost:8000/api/crm/tenants \
  -H "Authorization: Bearer $TOKEN"
```

### إنشاء User للـ Tenant

```bash
TENANT_ID="<paste-tenant-id-here>"

curl -X POST http://localhost:8000/api/crm/tenants/$TENANT_ID/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "email": "ahmed@dajajati.com",
    "password": "password123",
    "full_name": "Ahmed Ali",
    "role": "analyst",
    "permissions": ["ai.agent.chat", "logs.viewer"],
    "status": "active",
    "email_verified": true
  }'
```

### قائمة Users للـ Tenant

```bash
curl http://localhost:8000/api/crm/tenants/$TENANT_ID/users \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔐 اختبار AAA/Identity Endpoints

### Login عبر Identity API

```bash
curl -X POST http://localhost:8000/api/identity/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ahmed@dajajati.com",
    "password": "password123"
  }'
```

### قائمة Users

```bash
curl http://localhost:8000/api/identity/users \
  -H "Authorization: Bearer $TOKEN"
```

### قائمة Tenants

```bash
curl http://localhost:8000/api/identity/tenants \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔒 اختبار Access/AAA Endpoints

### التحقق من AAA File

```bash
USER_ID="<paste-user-id-here>"

curl http://localhost:8000/api/access/files/$TENANT_ID/$USER_ID \
  -H "Authorization: Bearer $TOKEN"
```

### التحقق من Permission

```bash
curl -X POST http://localhost:8000/api/access/permissions/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "permission": "ai.agent.chat"
  }'
```

---

## 🤖 اختبار AI Agent Endpoints

### Chat مع AI Agent

```bash
EMPLOYEE_TOKEN="<paste-employee-token-here>"

curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -d '{
    "message": "مرحبا، كيف الحال؟"
  }'
```

### Capabilities

```bash
curl http://localhost:8000/api/capabilities \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN"
```

---

## 📊 اختبار Dashboard

### Dashboard Stats

```bash
curl http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 التحقق من الـ Workflow

### السيناريو الكامل:

1. **إنشاء Tenant** → CRM
2. **إنشاء User** → CRM
3. **التحقق من AAA File** → AAA (يجب أن يكون موجود)
4. **Login** → Auth API
5. **الوصول للـ AI Agent** → Agent API

### سكريبت تلقائي:

```bash
./test-crm-aaa-workflow.sh
```

---

## ⚠️ Troubleshooting

### Backend لا يعمل

```bash
# تحقق من الحالة
docker ps | grep ai-backend

# شوف الـ logs
docker compose logs backend

# أعد التشغيل
./backend-restart.sh
```

### Endpoint يرجع 401 Unauthorized

- تأكد من أنك مررت الـ `Authorization: Bearer $TOKEN` header
- تأكد من أن الـ token صالح (لم ينتهي)
- جرب تسجيل الدخول مرة أخرى للحصول على token جديد

### Endpoint يرجع 403 Forbidden

- تأكد من أن المستخدم لديه الصلاحيات المطلوبة
- تأكد من وجود AAA file للمستخدم
- تأكد من أن Tenant و User نشطين

### AAA File غير موجود

- انتظر بضع ثوان بعد إنشاء User (للمعالجة التلقائية)
- تحقق من الـ logs:
  ```bash
  docker compose logs backend | grep -i "aaa\|event"
  ```

---

## 📚 Endpoints Reference

### CRM Endpoints
- `GET /api/crm/tenants` - قائمة Tenants
- `POST /api/crm/tenants` - إنشاء Tenant
- `GET /api/crm/tenants/{tenant_id}` - تفاصيل Tenant
- `GET /api/crm/tenants/{tenant_id}/users` - قائمة Users
- `POST /api/crm/tenants/{tenant_id}/users` - إنشاء User

### Identity/AAA Endpoints
- `POST /api/identity/login` - Login
- `GET /api/identity/users` - قائمة Users
- `GET /api/identity/tenants` - قائمة Tenants
- `GET /api/access/files/{tenant_id}/{user_id}` - AAA File
- `POST /api/access/permissions/check` - التحقق من Permission

### AI Agent Endpoints
- `POST /api/agent/chat` - Chat مع AI
- `GET /api/capabilities` - Capabilities
- `GET /api/dashboard/stats` - Dashboard Stats

---

## 🎯 Checklist

قبل الإنتاج، تأكد من:

- [ ] جميع الـ endpoints تعمل (استخدم `test-all-endpoints.sh`)
- [ ] الـ workflow الكامل يعمل (استخدم `test-crm-aaa-workflow.sh`)
- [ ] AAA files يتم إنشاؤها تلقائياً عند إنشاء Users
- [ ] Permissions تعمل بشكل صحيح
- [ ] Subscription features تعمل بشكل صحيح
- [ ] Multi-tenant isolation يعمل بشكل صحيح

---

**تم إنشاء هذا الدليل بواسطة:** Shiftwave Team  
**آخر تحديث:** 2024-01-15

