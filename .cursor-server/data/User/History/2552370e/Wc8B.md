# إصلاح مشكلة الاتصال في Docker - Docker Connection Fix

## 🔍 المشكلة (The Problem)

الـ Frontend والـ Backend يعملان في Docker containers منفصلة:
- **Frontend**: `ai-agent-frontend-prod` على port 3000
- **Backend**: `ai-agent-backend-prod` على port 8000

المشكلة: عندما يفتح المستخدم الصفحة من المتصفح (Browser):
- المتصفح يعمل على الـ **Host** (الجهاز الفعلي)
- الكود JavaScript يعمل في **المتصفح** (client-side)
- المتصفح يحاول الاتصال بالـ Backend

## ✅ الحل (The Solution)

تم إصلاح `lib/api.ts` لاستخدام نفس `hostname` الذي فتح منه المستخدم الصفحة:

```typescript
// إذا فتحت من: http://localhost:3000
// سيحاول الاتصال بـ: http://localhost:8000

// إذا فتحت من: http://172.31.20.228:3000
// سيحاول الاتصال بـ: http://172.31.20.228:8000

// إذا فتحت من: http://ai-agent.bankid-sy.com:3000
// سيحاول الاتصال بـ: http://ai-agent.bankid-sy.com:8000
```

## 🔧 كيفية التحقق (How to Verify)

### 1. افتح Developer Console (F12)
ستجد رسائل مثل:
```
[API] GET http://YOUR_HOSTNAME:8000/api/monitor (timeout: 15000ms)
```

### 2. تحقق من عنوان الـ Backend
في صفحة Monitor أو Visualization، ستجد:
```
Backend URL: http://YOUR_HOSTNAME:8000/api/monitor
```

### 3. اختبر الاتصال مباشرة
في Terminal (على الـ Host، ليس داخل Docker):
```bash
# إذا كنت على نفس الجهاز
curl http://localhost:8000/api/monitor

# إذا كنت على جهاز آخر
curl http://YOUR_SERVER_IP:8000/api/monitor
```

## 🐳 Docker Network

الـ Containers في نفس الشبكة (`ai-agent-network`):
- يمكن للـ containers الاتصال ببعضها باستخدام أسماء الـ services
- لكن **المتصفح** (Browser) لا يمكنه استخدام أسماء الـ services
- المتصفح يحتاج إلى **IP أو hostname** من الـ Host

## 📝 ملاحظات مهمة

### 1. Environment Variables
في `docker-compose.prod.yml`:
```yaml
environment:
  - NEXT_PUBLIC_AGENT_API_URL=${NEXT_PUBLIC_AGENT_API_URL:-http://ai-agent.bankid-sy.com}
```

هذا يعمل فقط إذا:
- تم تعيين المتغير عند بناء الـ image
- أو إذا كان المستخدم يفتح من `ai-agent.bankid-sy.com`

### 2. Runtime Detection
الكود الآن يكتشف تلقائياً:
- إذا فتحت من `localhost` → يستخدم `localhost:8000`
- إذا فتحت من IP → يستخدم `IP:8000`
- إذا فتحت من domain → يستخدم `domain:8000`

### 3. CORS
تأكد من أن الـ Backend يسمح بالطلبات من:
- `http://localhost:3000`
- `http://YOUR_IP:3000`
- `http://ai-agent.bankid-sy.com:3000`

في `backend/app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # أو قائمة محددة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 إعادة بناء الـ Frontend (Rebuild Frontend)

إذا قمت بتغيير الكود، يجب إعادة بناء الـ Frontend:

```bash
cd /home/ai/ai-agent
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

أو إعادة تشغيل الـ container:
```bash
docker-compose -f docker-compose.prod.yml restart frontend
```

## ✅ التحقق من أن كل شيء يعمل

### 1. تحقق من الـ Containers
```bash
docker ps | grep ai-agent
```

يجب أن ترى:
- `ai-agent-frontend-prod` (Up)
- `ai-agent-backend-prod` (Up, healthy)

### 2. تحقق من الـ Backend
```bash
curl http://localhost:8000/health
# أو
curl http://YOUR_IP:8000/health
```

### 3. افتح الصفحة
افتح في المتصفح:
- `http://localhost:3000` (إذا كنت على نفس الجهاز)
- `http://YOUR_IP:3000` (إذا كنت على جهاز آخر)

### 4. افتح Developer Console (F12)
- ابحث عن رسائل `[API]`
- تحقق من عنوان الـ Backend المستخدم
- إذا كان هناك أخطاء، ستظهر في Console

## 🔍 Troubleshooting

### المشكلة: "Failed to fetch"
**الحل:**
1. تحقق من أن الـ Backend يعمل: `docker ps | grep backend`
2. تحقق من الـ logs: `docker logs ai-agent-backend-prod`
3. تحقق من CORS settings في الـ Backend

### المشكلة: "CORS error"
**الحل:**
1. تأكد من أن CORS middleware مُعد في الـ Backend
2. تأكد من أن `allow_origins` يحتوي على origin الصحيح

### المشكلة: "Connection refused"
**الحل:**
1. تحقق من أن port 8000 مفتوح: `netstat -tuln | grep 8000`
2. تحقق من firewall rules
3. تحقق من أن الـ Backend container يعمل

### المشكلة: البيانات لا تظهر
**الحل:**
1. افتح Console (F12) وابحث عن أخطاء
2. اضغط زر "إعادة المحاولة" في الصفحة
3. تحقق من أن الـ API endpoints موجودة في الـ Backend

## 📊 الخلاصة

✅ **تم إصلاح المشكلة:**
- الكود الآن يستخدم `window.location.hostname` تلقائياً
- يعمل مع localhost, IP, أو domain
- لا حاجة لتغيير environment variables

✅ **الخطوات التالية:**
1. إعادة بناء الـ Frontend (إذا لزم الأمر)
2. فتح الصفحة من المتصفح
3. التحقق من Console للأخطاء
4. استخدام زر "إعادة المحاولة" إذا لزم الأمر

🎉 **الآن يجب أن يعمل كل شيء!**

