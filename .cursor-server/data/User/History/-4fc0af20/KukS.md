# دليل الاتصال بالـ Backend - Backend Connection Guide

## 🔍 كيفية التحقق من الاتصال

### 1. تحقق من عنوان الـ Backend
الصفحات الآن تعرض عنوان الـ Backend المتوقع في:
- صفحة **Visualization**: في أعلى الصفحة
- صفحة **Monitor**: في رسالة التحذير إذا لم تكن هناك بيانات

### 2. العناوين الافتراضية
النظام يحاول الاتصال بالترتيب التالي:
1. `NEXT_PUBLIC_AGENT_API_URL` (إذا كان موجوداً)
2. `NEXT_PUBLIC_BACKEND_URL` (إذا كان موجوداً)
3. `http://ai-agent.bankid-sy.com` (إذا كان hostname يحتوي على bankid-sy.com)
4. `http://{hostname}:8000` (إذا كان hostname ليس localhost)
5. `http://localhost:8000` (الافتراضي)

### 3. التحقق من أن الـ Backend يعمل

#### في Terminal:
```bash
# تحقق من أن الـ Backend يعمل
curl http://localhost:8000/api/monitor

# أو
curl http://localhost:8000/api/visualization/network-map
```

#### في Browser:
افتح:
- `http://localhost:8000/api/monitor`
- `http://localhost:8000/api/visualization/network-map`

يجب أن ترى JSON response.

### 4. إصلاح المشاكل الشائعة

#### المشكلة: "لا توجد بيانات"
**الحلول:**
1. تأكد من أن الـ Backend يعمل:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. تحقق من CORS settings في الـ Backend:
   ```python
   # يجب أن يكون CORS مُعد للسماح بالطلبات من Frontend
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # أو قائمة محددة
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. تحقق من أن الـ API endpoints موجودة:
   - `/api/monitor`
   - `/api/visualization/network-map`
   - `/api/visualization/architecture`
   - `/api/visualization/metrics`

#### المشكلة: Timeout
**الحل:**
- Timeout الآن 15 ثانية للـ monitor
- Timeout 10 ثوان للـ visualization
- إذا كان الـ Backend بطيئاً جداً، الصفحات تعمل بدون بيانات

#### المشكلة: CORS Error
**الحل:**
تأكد من إعداد CORS في الـ Backend كما هو موضح أعلاه.

### 5. متغيرات البيئة

أنشئ ملف `.env.local` في مجلد `frontend`:
```env
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

أو في production:
```env
NEXT_PUBLIC_AGENT_API_URL=http://ai-agent.bankid-sy.com
NEXT_PUBLIC_BACKEND_URL=http://ai-agent.bankid-sy.com
```

### 6. Debugging

افتح Developer Console (F12) وسترى:
- `[API] GET http://localhost:8000/api/monitor (timeout: 15000ms)`
- أي أخطاء في الاتصال

### 7. التحقق من الـ API Endpoints

#### Monitor:
```bash
curl http://localhost:8000/api/monitor
```

#### Visualization:
```bash
curl http://localhost:8000/api/visualization/network-map
curl http://localhost:8000/api/visualization/architecture
curl http://localhost:8000/api/visualization/metrics
```

### 8. نصائح

1. **الصفحات تعمل حتى بدون بيانات**: إذا كان الـ Backend بطيئاً، الصفحات تفتح وتعمل بدون بيانات
2. **إعادة المحاولة**: كل صفحة لديها زر "إعادة المحاولة" إذا لم تكن هناك بيانات
3. **Auto-retry**: الصفحات تحاول جلب البيانات كل 15 ثانية تلقائياً
4. **Logging**: افتح Console لرؤية تفاصيل الاتصال

## ✅ الخلاصة

- الصفحات تعمل حتى بدون بيانات
- Timeout محسّن (15 ثانية للـ monitor، 10 ثوان للـ visualization)
- رسائل واضحة عن حالة الاتصال
- أزرار إعادة المحاولة
- Auto-retry كل 15 ثانية

إذا استمرت المشكلة، تحقق من:
1. ✅ الـ Backend يعمل
2. ✅ CORS مُعد بشكل صحيح
3. ✅ الـ API endpoints موجودة
4. ✅ العنوان الصحيح في Console

