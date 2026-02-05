# نظام الموافقات - مثال عملي

## نظرة عامة

نظام الموافقات يسمح للمستخدمين بتنفيذ عمليات حساسة على النظام بعد الحصول على موافقة من المشرفين (Admin/DevOps).

## سيناريو المثال

### الخطوة 1: المستخدم يطلب تنفيذ أمر shell

**المستخدم:** يريد تنفيذ أمر `ls -la` على النظام

**من خلال Agent Console:**
```
المستخدم: "اعرض الملفات في المجلد الحالي"
```

**أو من خلال Tools Page:**
- يذهب إلى صفحة Tools
- يكتب الأمر: `ls -la`
- يضغط على "Execute"

### الخطوة 2: النظام يتحقق من الإعدادات

النظام يتحقق من:
1. هل `run_shell` مفعّل في الإعدادات؟ (`allow_shell: true`)
2. هل `run_shell` يتطلب موافقة؟ (`require_approval: ["run_shell"]`)
3. هل المستخدم لديه صلاحية الموافقة؟ (Admin/DevOps فقط)

### الخطوة 3: إنشاء طلب موافقة

إذا كان الأمر يتطلب موافقة والمستخدم ليس لديه صلاحية الموافقة:

```json
{
  "status": "pending",
  "action_id": "action_123456",
  "message": "Action requires approval"
}
```

يتم إنشاء طلب موافقة في قاعدة البيانات:

```json
{
  "id": "action_123456",
  "user_email": "user@example.com",
  "tool_name": "run_shell",
  "tool_args": {
    "cmd": "ls -la"
  },
  "reason": "Requires approval",
  "status": "pending",
  "created_at": "2024-11-16T12:00:00Z"
}
```

### الخطوة 4: المشرف يرى الطلب

**المشرف (Admin/DevOps):**
1. يذهب إلى صفحة **Approvals**
2. يرى الطلب في قائمة "Pending Actions"
3. يرى التفاصيل:
   - المستخدم: `user@example.com`
   - الأمر: `run_shell`
   - المعاملات: `{"cmd": "ls -la"}`
   - الوقت: `2024-11-16 12:00:00`

### الخطوة 5: المشرف يقرر

#### الخيار 1: الموافقة ✅

المشرف يضغط على زر **"Approve"**

**ما يحدث:**
1. يتم تحديث حالة الطلب إلى `approved`
2. يتم تنفيذ الأمر: `ls -la`
3. يتم حفظ النتيجة في `execution_result`
4. يتم إرسال إشعار للمستخدم

**النتيجة:**
```json
{
  "status": "approved",
  "action": {
    "id": "action_123456",
    "status": "approved",
    "approved_by": "admin@example.com",
    "approved_at": "2024-11-16T12:05:00Z",
    "execution_result": "total 48\ndrwxr-xr-x 2 user user 4096 Nov 16 12:00 .\n..."
  }
}
```

#### الخيار 2: الرفض ❌

المشرف يضغط على زر **"Reject"**

**ما يحدث:**
1. يطلب النظام سبب الرفض (اختياري)
2. يتم تحديث حالة الطلب إلى `rejected`
3. يتم حفظ سبب الرفض
4. يتم إرسال إشعار للمستخدم

**النتيجة:**
```json
{
  "status": "rejected",
  "action": {
    "id": "action_123456",
    "status": "rejected",
    "approved_by": "admin@example.com",
    "approved_at": "2024-11-16T12:05:00Z",
    "rejection_reason": "Command not allowed for security reasons"
  }
}
```

## مثال عملي كامل

### السيناريو: حذف ملف

**1. المستخدم يطلب:**
```
المستخدم: "احذف الملف test.txt"
```

**2. Agent يحدد أنه يحتاج `run_shell` مع الأمر:**
```bash
rm test.txt
```

**3. النظام يتحقق:**
- ✅ `allow_shell: true`
- ✅ `require_approval: ["run_shell"]`
- ❌ المستخدم ليس Admin/DevOps

**4. يتم إنشاء طلب موافقة:**
```json
{
  "id": "action_789012",
  "user_email": "developer@example.com",
  "tool_name": "run_shell",
  "tool_args": {"cmd": "rm test.txt"},
  "status": "pending",
  "created_at": "2024-11-16T12:10:00Z"
}
```

**5. المشرف يرى الطلب في صفحة Approvals:**
```
⏳ Pending Actions (1)

🔔 run_shell - developer@example.com
Arguments:
{
  "cmd": "rm test.txt"
}
Created: 11/16/2024, 12:10:00 PM

[✅ Approve]  [❌ Reject]
```

**6. المشرف يقرر الموافقة:**
- يضغط على "Approve"
- يتم تنفيذ الأمر
- النتيجة تظهر في "Completed Actions"

**7. المستخدم يرى النتيجة:**
- في Agent Console: "تم تنفيذ الأمر بنجاح"
- أو في Tools Page: النتيجة تظهر في output area

## API Endpoints

### 1. تنفيذ أمر shell (يتطلب موافقة)
```http
POST /api/tools/run_shell
Authorization: Bearer <token>
Content-Type: application/json

{
  "cmd": "ls -la"
}
```

**الرد إذا كان يتطلب موافقة:**
```json
{
  "status": "pending",
  "action_id": "action_123456",
  "message": "Action requires approval"
}
```

### 2. الحصول على قائمة طلبات الموافقة
```http
GET /api/pending-actions
Authorization: Bearer <admin_token>
```

**الرد:**
```json
{
  "actions": [
    {
      "id": "action_123456",
      "user_email": "user@example.com",
      "tool_name": "run_shell",
      "tool_args": {"cmd": "ls -la"},
      "status": "pending",
      "created_at": "2024-11-16T12:00:00Z"
    }
  ]
}
```

### 3. الموافقة على طلب
```http
POST /api/pending-actions/{action_id}/approve
Authorization: Bearer <admin_token>
```

**الرد:**
```json
{
  "status": "approved",
  "action": {
    "id": "action_123456",
    "status": "approved",
    "execution_result": "...",
    "executed_at": "2024-11-16T12:05:00Z"
  }
}
```

### 4. رفض طلب
```http
POST /api/pending-actions/{action_id}/reject
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "reason": "Command not allowed"
}
```

**الرد:**
```json
{
  "status": "rejected",
  "action": {
    "id": "action_123456",
    "status": "rejected",
    "rejection_reason": "Command not allowed"
  }
}
```

## الإعدادات

في صفحة **Settings**، يمكنك التحكم في:

1. **Allow Shell**: تفعيل/تعطيل تنفيذ الأوامر
2. **Require Approval**: قائمة الأدوات التي تتطلب موافقة

مثال:
```json
{
  "allow_shell": true,
  "require_approval": ["run_shell", "read_file"]
}
```

## الأدوار والصلاحيات

- **Admin**: يمكنه الموافقة/الرفض على جميع الطلبات
- **DevOps**: يمكنه الموافقة/الرفض على جميع الطلبات
- **Developer**: يمكنه إنشاء طلبات موافقة فقط
- **Viewer**: لا يمكنه إنشاء طلبات موافقة

## ملاحظات أمنية

1. جميع الطلبات تُسجّل في قاعدة البيانات
2. يمكن تتبع من وافق/رفض ومتى
3. النتائج تُحفظ للتدقيق
4. فقط Admin/DevOps يمكنهم الموافقة/الرفض

## مثال على استخدام curl

### إنشاء طلب موافقة:
```bash
curl -X POST http://localhost:8000/api/tools/run_shell \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "ls -la"}'
```

### الموافقة على طلب:
```bash
curl -X POST http://localhost:8000/api/pending-actions/action_123456/approve \
  -H "Authorization: Bearer <admin_token>"
```

### رفض طلب:
```bash
curl -X POST http://localhost:8000/api/pending-actions/action_123456/reject \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Not allowed"}'
```

