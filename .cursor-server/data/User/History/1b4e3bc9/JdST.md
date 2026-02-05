# دليل الربط بين Backend و Frontend

## 🔗 الربط بين Backend و Frontend

### 1. **في Docker (Local Development)**

#### Backend:
- **URL**: `http://backend:8000` (داخل Docker network)
- **Port**: `8000`
- **Service Name**: `backend`

#### Frontend:
- **URL**: `http://localhost:3000` (من المتصفح)
- **Port**: `3000`
- **Service Name**: `frontend-dashboard`

#### كيف يعمل الربط:
1. **Client-side (من المتصفح)**:
   - Frontend يستخدم relative URLs: `/api/chat`
   - Next.js rewrites يوجه `/api/*` إلى `http://backend:8000/api/*`
   - هذا يحل مشاكل CORS تلقائياً

2. **Server-side (من Next.js server)**:
   - يستخدم `BACKEND_URL` environment variable
   - أو `http://backend:8000` كـ default (Docker service name)

### 2. **في Production**

#### Environment Variables:

**Backend (.env أو docker-compose.yml)**:
```bash
CORS_ORIGINS=["*"]  # أو قائمة محددة من الـ origins
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_BACKEND_URL=http://ai-agent.bankid-sy.com:8000
BACKEND_URL=http://backend:8000  # للـ server-side فقط
```

### 3. **Endpoints المهمة**

#### Chat API:
- **Endpoint**: `POST /api/chat`
- **Request**: `{ "message": "your message" }`
- **Response**: `{ "reply": "agent response", "session_id": "..." }`

#### Dashboard Endpoints:
- `/api/incidents/stats/today` - إحصائيات الحوادث اليوم
- `/api/security/threat-detection/summary?hours=24` - ملخص التهديدات
- `/api/security/hardening/status` - حالة التحصين
- `/api/alerts/behavior/?resolved=false&hours=24` - تنبيهات السلوك
- `/api/monitor` - مراقبة النظام
- `/api/visualization/network-map` - خريطة الشبكة
- `/api/visualization/architecture` - البنية المعمارية
- `/api/visualization/metrics` - المقاييس

### 4. **مشاكل شائعة وحلولها**

#### مشكلة: CORS Error
**الحل**: 
- تأكد من أن `CORS_ORIGINS` في Backend يحتوي على origin الـ Frontend
- أو استخدم `["*"]` للسماح بكل الـ origins (في development فقط)

#### مشكلة: Connection Refused
**الحل**:
- تأكد من أن Backend يعمل: `curl http://localhost:8000/health`
- تأكد من أن Docker network يعمل: `docker network ls`
- تأكد من أن الـ services في نفس الـ network

#### مشكلة: Agent لا يرد
**الحل**:
- تأكد من أن Ollama يعمل: `curl http://localhost:11434/api/tags`
- تأكد من أن الموديل موجود: `ollama list`
- تحقق من logs: `docker logs ai-backend`

### 5. **التحقق من الربط**

#### Test Backend:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/
```

#### Test Frontend:
```bash
curl http://localhost:3000/
```

#### Test API:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

### 6. **ملاحظات مهمة**

1. **Authentication**: معظم الـ endpoints تسمح بـ guest access في development
2. **Error Handling**: جميع الـ endpoints ترجع fallback responses عند الفشل
3. **Agent**: الـ Agent دائماً يرد، حتى لو فشل شيء (مع رسالة خطأ واضحة)
4. **Logging**: جميع الأخطاء تُسجل في logs للمساعدة في التصحيح

