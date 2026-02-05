# 🚀 دليل الوصول لـ CRM وإنشاء مستخدم جديد

## 📍 الجزء الأول: الوصول لـ CRM

### الطريقة 1: من المتصفح مباشرة

```
1. افتح المتصفح
2. اذهب إلى: http://localhost:3000/login
3. سجّل دخول (إذا لم تكن مسجل دخول)
4. بعد تسجيل الدخول، اذهب إلى: http://localhost:3000/crm/tenants
```

### الطريقة 2: من القائمة الجانبية

```
1. بعد تسجيل الدخول
2. من القائمة الجانبية (Sidebar) → اضغط على "CRM"
3. ثم اضغط على "Tenants"
```

### الطريقة 3: من Dashboard

```
1. بعد تسجيل الدخول → Dashboard الرئيسي
2. ابحث عن رابط "CRM" أو "Tenants"
3. اضغط عليه
```

---

## 👤 الجزء الثاني: إنشاء مستخدم جديد

### الطريقة 1: من API مباشرة (الأسرع)

#### باستخدام curl:

```bash
curl -X POST http://localhost:8000/api/identity/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "اسم المستخدم الكامل",
    "tenant_id": "TENANT_UUID_HERE"
  }'
```

#### باستخدام Python:

```python
import requests

url = "http://localhost:8000/api/identity/users"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}
data = {
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "اسم المستخدم الكامل",
    "tenant_id": "TENANT_UUID_HERE"  # اختياري
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### باستخدام JavaScript/Frontend:

```javascript
import { identityApi } from '@/lib/api';

const createUser = async () => {
  try {
    const user = await identityApi.createUser({
      email: "newuser@example.com",
      password: "SecurePass123!",
      full_name: "اسم المستخدم الكامل",
      tenant_id: "TENANT_UUID_HERE"  // اختياري
    });
    console.log("User created:", user);
  } catch (error) {
    console.error("Error:", error);
  }
};
```

---

### الطريقة 2: من Swagger/API Docs

```
1. افتح: http://localhost:8000/docs
2. ابحث عن: POST /api/identity/users
3. اضغط على "Try it out"
4. أدخل البيانات:
   - email: newuser@example.com
   - password: SecurePass123!
   - full_name: اسم المستخدم الكامل
   - tenant_id: (اختياري) UUID للـ Tenant
5. اضغط "Execute"
```

---

### الطريقة 3: من Terminal/Backend Script

#### إنشاء ملف Python:

```python
# create_user.py
from app.core.database import SessionLocal
from app.identity import service as identity_service
from app.identity import schemas

db = SessionLocal()

try:
    user_data = schemas.UserCreate(
        email="newuser@example.com",
        password="SecurePass123!",
        full_name="اسم المستخدم الكامل",
        tenant_id=None  # أو UUID للـ Tenant
    )
    
    user = identity_service.IdentityService.create_user(db, user_data)
    print(f"User created: {user.email} (ID: {user.id})")
finally:
    db.close()
```

#### تشغيله:

```bash
cd /home/ai/ai-agent/backend
python create_user.py
```

---

## 📋 البيانات المطلوبة لإنشاء مستخدم

### البيانات الإلزامية:

- **email**: البريد الإلكتروني (يجب أن يكون فريد)
- **password**: كلمة المرور (8 أحرف على الأقل)

### البيانات الاختيارية:

- **full_name**: الاسم الكامل
- **tenant_id**: UUID للـ Tenant (إذا كنت تريد ربط المستخدم بـ Tenant معين)

---

## 🔗 ربط المستخدم بـ Tenant

بعد إنشاء المستخدم، يمكنك ربطه بـ Tenant:

### من API:

```bash
curl -X POST "http://localhost:8000/api/identity/tenants/{tenant_id}/users?user_id={user_id}&role=member" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### من Frontend:

```javascript
import { identityApi } from '@/lib/api';

await identityApi.addUserToTenant(tenantId, userId, 'member');
```

---

## 📝 مثال كامل: من Login إلى إنشاء مستخدم

### الخطوة 1: تسجيل الدخول

```
1. افتح: http://localhost:3000/login
2. أدخل:
   - Email: admin@example.com
   - Password: admin123
3. اضغط "تسجيل الدخول"
```

### الخطوة 2: الوصول لـ CRM

```
1. بعد تسجيل الدخول
2. اذهب إلى: http://localhost:3000/crm/tenants
3. أو من القائمة الجانبية → CRM → Tenants
```

### الخطوة 3: الحصول على Tenant ID

```
1. من صفحة Tenants
2. اضغط على أي Tenant
3. شوف الـ URL: /crm/tenants/{tenant_id}
4. انسخ الـ tenant_id
```

### الخطوة 4: إنشاء مستخدم جديد

#### من Browser Console (F12):

```javascript
// احصل على Token من localStorage
const token = localStorage.getItem('auth_token');

// أنشئ المستخدم
fetch('http://localhost:8000/api/identity/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    email: 'newuser@example.com',
    password: 'SecurePass123!',
    full_name: 'اسم المستخدم الكامل',
    tenant_id: 'TENANT_ID_HERE'  // من الخطوة 3
  })
})
.then(res => res.json())
.then(data => {
  console.log('User created:', data);
  
  // ربط المستخدم بـ Tenant
  const userId = data.id;
  fetch(`http://localhost:8000/api/identity/tenants/TENANT_ID_HERE/users?user_id=${userId}&role=member`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  .then(res => res.json())
  .then(data => console.log('User added to tenant:', data));
});
```

---

## 🎯 Quick Commands

### إنشاء مستخدم سريع من Terminal:

```bash
# احصل على Token أولاً (من Login)
TOKEN="YOUR_TOKEN_HERE"

# أنشئ المستخدم
curl -X POST http://localhost:8000/api/identity/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "email": "user@example.com",
    "password": "Pass123!",
    "full_name": "User Name"
  }'
```

---

## ✅ التحقق من إنشاء المستخدم

### من API:

```bash
curl http://localhost:8000/api/identity/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### من Frontend:

```javascript
import { identityApi } from '@/lib/api';

const users = await identityApi.getUser(userId);
console.log(users);
```

### من CRM:

```
1. اذهب إلى: /crm/tenants/{tenant_id}/users
2. شوف قائمة المستخدمين
```

---

## 🔧 Troubleshooting

### خطأ: "Email already exists"

**الحل:** استخدم email مختلف

### خطأ: "Authentication required"

**الحل:** تأكد من إرسال Token في Header:
```
Authorization: Bearer YOUR_TOKEN
```

### خطأ: "Password too short"

**الحل:** كلمة المرور يجب أن تكون 8 أحرف على الأقل

### لا أستطيع الوصول لـ CRM؟

1. **تحقق من تسجيل الدخول:**
   - افتح Developer Tools (F12)
   - Application → Local Storage
   - تحقق من وجود `auth_token`

2. **تحقق من Backend:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **تحقق من Frontend:**
   ```bash
   curl http://localhost:3000
   ```

---

## 📚 مراجع إضافية

- **API Docs:** http://localhost:8000/docs
- **HOW_TO_ACCESS.md:** دليل الوصول لجميع الواجهات
- **CRM_AAA_START_GUIDE.md:** دليل البدء الكامل

---

**آخر تحديث:** 2025-01-XX

