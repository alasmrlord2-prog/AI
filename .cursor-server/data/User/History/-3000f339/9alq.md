# 🔄 إعادة تشغيل Backend مطلوبة

## 📊 الوضع الحالي:

✅ **الكود جاهز:**
- Identity router يمكن استيراده
- CRM router يمكن استيراده
- email-validator مثبت

❌ **Backend يحتاج إعادة تشغيل:**
- Backend الحالي لا يحتوي على identity/crm routes
- هناك processين من uvicorn يعملان على port 8000

## 🔧 الحل:

قم بتشغيل الأوامر التالية **كـ root**:

```bash
# 1. إيقاف جميع عمليات uvicorn على port 8000
sudo pkill -f 'uvicorn.*8000'

# 2. الانتقال إلى مجلد Backend
cd /home/ai/ai-agent/backend

# 3. إعادة تشغيل Backend
sudo /usr/local/bin/python3.11 /usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

أو استخدم script إعادة التشغيل إذا كان موجوداً:

```bash
cd /home/ai/ai-agent/backend
sudo ./restart.sh
```

## ✅ بعد إعادة التشغيل:

1. **التحقق من Health:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

2. **التحقق من Routes:**
   ```bash
   curl -s http://127.0.0.1:8000/openapi.json | python3 -c "import json, sys; data = json.load(sys.stdin); paths = [p for p in data['paths'].keys() if '/api/identity' in p or '/api/crm' in p]; print(f'Found {len(paths)} routes')"
   ```

3. **اختبار Login:**
   ```bash
   curl -X POST http://crm.bankid-sy.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@example.com","password":"admin123"}'
   ```

## 📋 Routes المتوقعة بعد إعادة التشغيل:

### Identity Routes:
- `/api/identity/login`
- `/api/identity/api-tokens`
- `/api/identity/api-tokens/{token_id}`
- `/api/identity/sessions`
- `/api/identity/users`
- `/api/identity/tenants`
- وغيرها...

### CRM Routes:
- `/api/crm/tenants`
- `/api/crm/tenants/{tenant_id}/users`
- `/api/crm/tenants/{tenant_id}/dashboard`
- `/api/crm/tenants/{tenant_id}/audit-logs`
- وغيرها...

## 🎯 النتيجة المتوقعة:

بعد إعادة التشغيل:
- ✅ CRM سيعمل بشكل كامل
- ✅ AAA سيعمل بشكل كامل
- ✅ جميع الـ API endpoints ستكون متاحة
- ✅ Login في CRM و AAA سيعمل

