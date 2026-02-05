# دليل اختبار نظام الموافقات

## 📋 المتطلبات

1. ✅ Backend يعمل على `http://localhost:8000`
2. ✅ Frontend يعمل على `http://localhost:3000`
3. ✅ لديك حسابين:
   - حساب عادي (مستخدم عادي)
   - حساب Admin أو DevOps (مشرف)

---

## 🔧 الخطوة 1: إعداد النظام

### 1.1 تفعيل نظام الموافقات

1. سجل دخول بحساب **Admin**
2. اذهب إلى صفحة **Settings**
3. فعّل الخيارات التالية:
   - ✅ **Allow Shell**: `true`
   - ✅ **Require Approval**: أضف `run_shell` إلى القائمة

**أو من خلال API:**
```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "allow_shell": true,
    "require_approval": ["run_shell"]
  }'
```

---

## 🧪 الخطوة 2: اختبار كحساب عادي

### 2.1 إنشاء طلب موافقة

**الطريقة 1: من خلال صفحة Tools**
Z

1. سجل دخول بحساب **مستخدم عادي** (ليس Admin)
2. اذهب إلى صفحة **Tools**
3. في قسم "Run Shell"، اكتب الأمر:
   ```
   ls -la
   ```
4. اضغط على زر **"⚡ Execute"**

**النتيجة المتوقعة:**
```
⚠️ Error: run_shell disabled from settings
أو
{
  "status": "pending",
  "action_id": "action_1234567890",
  "message": "Action requires approval"
}
```

**الطريقة 2: من خلال Agent Console**

1. اذهب إلى صفحة **Agent Console**
2. اكتب:
   ```
   اعرض الملفات في المجلد الحالي
   ```
3. اضغط على **"تشغيل"**

**النتيجة المتوقعة:**
```
⚠️ هذا الأمر يتطلب موافقة من المشرف
طلب الموافقة رقم: action_1234567890
```

**الطريقة 3: من خلال API مباشرة**

```bash
# احصل على token للمستخدم العادي أولاً
TOKEN="<user_token>"

# أرسل طلب تنفيذ أمر
curl -X POST http://localhost:8000/api/tools/run_shell \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "ls -la"}'
```

**الرد المتوقع:**
```json
{
  "status": "pending",
  "action_id": "action_1234567890",
  "message": "Action requires approval"
}
```

---

## 👨‍💼 الخطوة 3: اختبار كحساب مشرف

### 3.1 عرض طلبات الموافقة

**الطريقة 1: من خلال الواجهة**

1. سجل دخول بحساب **Admin** أو **DevOps**
2. اذهب إلى صفحة **Approvals**
3. يجب أن ترى الطلب في قسم **"⏳ Pending"**

**معلومات الطلب:**
```
🔔 run_shell - user@example.com

Arguments:
{
  "cmd": "ls -la"
}

Reason: Requires approval

Created: [التاريخ والوقت]

[✅ Approve]  [❌ Reject]
```

**الطريقة 2: من خلال API**

```bash
# احصل على token للمشرف
ADMIN_TOKEN="<admin_token>"

# احصل على قائمة الطلبات
curl -X GET http://localhost:8000/api/pending-actions \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**الرد المتوقع:**
```json
{
  "actions": [
    {
      "id": "action_1234567890",
      "user_email": "user@example.com",
      "tool_name": "run_shell",
      "tool_args": {"cmd": "ls -la"},
      "status": "pending",
      "created_at": "2024-11-16T12:00:00Z"
    }
  ]
}
```

---

### 3.2 الموافقة على الطلب

**الطريقة 1: من خلال الواجهة**

1. في صفحة **Approvals**
2. اضغط على زر **"✅ Approve"** بجانب الطلب
3. انتظر قليلاً
4. يجب أن ينتقل الطلب إلى قسم **"📋 Completed"**

**النتيجة المتوقعة:**
```
✅ run_shell - user@example.com (approved)

Approved by admin@example.com at [التاريخ والوقت]

Execution Result:
total 48
drwxr-xr-x 2 user user 4096 Nov 16 12:00 .
...
```

**الطريقة 2: من خلال API**

```bash
# الموافقة على الطلب
curl -X POST http://localhost:8000/api/pending-actions/action_1234567890/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**الرد المتوقع:**
```json
{
  "status": "approved",
  "action": {
    "id": "action_1234567890",
    "status": "approved",
    "approved_by": "admin@example.com",
    "approved_at": "2024-11-16T12:05:00Z",
    "execution_result": "total 48\n..."
  }
}
```

---

### 3.3 رفض الطلب (اختبار)

**لاختبار الرفض:**

1. أنشئ طلب موافقة جديد (كرر الخطوة 2)
2. في صفحة **Approvals**
3. اضغط على زر **"❌ Reject"**
4. أدخل سبب الرفض (مثل: "اختبار النظام")
5. اضغط OK

**النتيجة المتوقعة:**
```
❌ run_shell - user@example.com (rejected)

Rejected by admin@example.com at [التاريخ والوقت]

Reason: اختبار النظام
```

**من خلال API:**
```bash
curl -X POST http://localhost:8000/api/pending-actions/action_1234567890/reject \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "اختبار النظام"}'
```

---

## ✅ قائمة التحقق من الاختبار

### اختبارات أساسية:

- [ ] ✅ إنشاء طلب موافقة من حساب عادي
- [ ] ✅ عرض الطلب في صفحة Approvals (كـ Admin)
- [ ] ✅ الموافقة على الطلب
- [ ] ✅ رفض الطلب
- [ ] ✅ رؤية النتيجة بعد الموافقة
- [ ] ✅ رؤية سبب الرفض بعد الرفض

### اختبارات متقدمة:

- [ ] ✅ اختبار مع عدة طلبات في نفس الوقت
- [ ] ✅ اختبار مع أوامر مختلفة (ls, cat, echo, etc.)
- [ ] ✅ اختبار مع حساب DevOps (يجب أن يعمل مثل Admin)
- [ ] ✅ اختبار مع حساب Viewer (يجب أن لا يستطيع إنشاء طلبات)

---

## 🐛 استكشاف الأخطاء

### المشكلة: لا أرى طلبات الموافقة

**الحل:**
1. تأكد أنك سجلت دخول بحساب **Admin** أو **DevOps**
2. تأكد أن `require_approval` يحتوي على `run_shell`
3. تأكد أن `allow_shell` مفعّل
4. تحقق من ملف `memory/pending_actions.json`

### المشكلة: الطلب لا يتم تنفيذه بعد الموافقة

**الحل:**
1. تحقق من سجلات الـ backend: `tail -f backend.log`
2. تأكد أن الأمر صحيح
3. تحقق من صلاحيات المستخدم في النظام

### المشكلة: المستخدم يستطيع تنفيذ الأوامر مباشرة

**الحل:**
1. تأكد أن `require_approval` يحتوي على `run_shell`
2. تأكد أن المستخدم ليس Admin/DevOps
3. تحقق من الإعدادات في صفحة Settings

---

## 📝 سيناريو اختبار كامل

### السيناريو: حذف ملف

1. **المستخدم العادي:**
   ```
   يطلب: "احذف الملف test.txt"
   ```

2. **النظام:**
   ```
   يرد: "Action requires approval"
   يخلق طلب موافقة: action_7890123456
   ```

3. **المشرف:**
   ```
   يرى الطلب في Approvals
   يقرر: موافقة أو رفض
   ```

4. **إذا موافقة:**
   ```
   يتم تنفيذ: rm test.txt
   النتيجة: "تم حذف الملف بنجاح"
   ```

5. **إذا رفض:**
   ```
   السبب: "حذف الملفات يتطلب موافقة خاصة"
   ```

---

## 🔍 فحص الملفات

### فحص طلبات الموافقة المحفوظة:

```bash
# عرض ملف طلبات الموافقة
cat /home/ai/ai-agent/backend/memory/pending_actions.json
```

### فحص سجلات الـ backend:

```bash
# عرض آخر 50 سطر من السجلات
tail -50 /home/ai/ai-agent/backend/backend.log

# متابعة السجلات مباشرة
tail -f /home/ai/ai-agent/backend/backend.log
```

---

## 💡 نصائح للاختبار

1. **ابدأ بسيط:** جرب أمر `ls -la` أولاً
2. **اختبر الرفض:** رفض بعض الطلبات لاختبار النظام
3. **اختبر عدة طلبات:** أنشئ عدة طلبات في نفس الوقت
4. **اختبر الأدوار:** جرب مع حسابات مختلفة (Admin, DevOps, Developer, Viewer)
5. **راقب السجلات:** راقب `backend.log` أثناء الاختبار

---

## ✅ النتيجة النهائية

بعد اكتمال الاختبار، يجب أن:

1. ✅ المستخدمون العاديون لا يستطيعون تنفيذ الأوامر مباشرة
2. ✅ المشرفون يرون جميع الطلبات في صفحة Approvals
3. ✅ المشرفون يستطيعون الموافقة أو الرفض
4. ✅ النتائج تُحفظ وتُعرض بشكل صحيح
5. ✅ النظام يعمل بسلاسة

---

## 🎯 اختبار سريع (5 دقائق)

```bash
# 1. أنشئ طلب موافقة
curl -X POST http://localhost:8000/api/tools/run_shell \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "echo test"}'

# 2. احصل على قائمة الطلبات (كـ Admin)
curl -X GET http://localhost:8000/api/pending-actions \
  -H "Authorization: Bearer <admin_token>"

# 3. وافق على الطلب
curl -X POST http://localhost:8000/api/pending-actions/<action_id>/approve \
  -H "Authorization: Bearer <admin_token>"
```

---

**جاهز للاختبار! 🚀**

