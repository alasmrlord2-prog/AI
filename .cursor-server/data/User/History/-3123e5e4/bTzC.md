# إصلاح Frontend - Frontend Fix

## المشكلة:
Frontend يحاول الاتصال بـ `localhost:8000` لكن Backend على سيرفر بعيد (`3.79.231.29:8000`)

## الحل:

### 1. تحديث `.env.local`:
تم تحديث الملف ليشير إلى IP السيرفر الصحيح:
```
NEXT_PUBLIC_BACKEND_URL=http://3.79.231.29:8000
NEXT_PUBLIC_AGENT_API_URL=http://3.79.231.29:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://3.79.231.29:8000/ws/chat
```

### 2. إعادة تشغيل Frontend:
**مهم جداً:** في Next.js، environment variables تُقرأ عند بدء الـ dev server. يجب إعادة تشغيله بعد تغيير `.env.local`:

```bash
# أوقف الـ dev server الحالي (Ctrl+C)
# ثم:
cd /home/ai/ai-agent/frontend
npm run dev
```

### 3. التحقق من الاتصال:

بعد إعادة التشغيل، افتح Browser Console وتحقق من:
- لا توجد WebSocket errors
- API calls تذهب إلى `http://3.79.231.29:8000` وليس `localhost:8000`

### 4. اختبار سريع:

في Browser Console:
```javascript
// تحقق من environment variables
console.log('API URL:', process.env.NEXT_PUBLIC_AGENT_API_URL);
console.log('WS URL:', process.env.NEXT_PUBLIC_AGENT_WS_URL);

// اختبر API مباشرة
fetch('http://3.79.231.29:8000/api/settings')
  .then(r => r.json())
  .then(console.log);
```

### 5. إذا استمرت المشكلة:

#### أ) تحقق من Firewall:
```bash
# على السيرفر
sudo ufw status
# تأكد أن port 8000 مفتوح
sudo ufw allow 8000/tcp
```

#### ب) تحقق من Backend accessibility:
```bash
# من السيرفر نفسه
curl http://3.79.231.29:8000/api/settings

# من خارج السيرفر (من جهاز آخر)
curl http://3.79.231.29:8000/api/settings
```

#### ج) تحقق من CORS:
Backend يجب أن يسمح بـ origin الخاص بالـ frontend. في `backend/app/main.py`:
```python
origins = [
    "http://localhost:3000",
    "http://3.79.231.29:3000",  # Frontend IP
    "http://63.178.23.205:3000",  # إذا كان Frontend على IP مختلف
    "*",  # Development only
]
```

### 6. ملاحظات:

- **Development:** استخدم IP السيرفر في `.env.local`
- **Production:** استخدم domain name إذا كان متاحاً
- **WebSocket:** يجب أن يكون `ws://` وليس `http://`
- **HTTPS:** إذا كان Frontend على HTTPS، يجب أن يكون Backend على HTTPS أيضاً (أو استخدام reverse proxy)

## حالة Backend الحالية:
✅ Backend شغال على `http://3.79.231.29:8000`
✅ Container status: Running
✅ API يرد: `/api/settings` يعمل

## الخطوة التالية:
1. أعد تشغيل Frontend dev server
2. افتح Browser Console
3. جرّب إرسال رسالة
4. تحقق من Network tab في DevTools

