# دليل حل المشاكل - Troubleshooting Guide

## المشاكل الشائعة وحلولها

### 1. خطأ "Failed to fetch" أو "خطأ بالاتصال مع السيرفر"

**السبب:**
- Backend غير شغال
- Port 8000 غير متاح
- CORS issues

**الحل:**

1. **تحقق من Backend:**
```bash
cd /home/ai/ai-agent/backend
docker compose -f backend-compose.yml ps
```

2. **شغّل Backend:**
```bash
cd /home/ai/ai-agent/backend
docker compose -f backend-compose.yml up -d --build
```

3. **تحقق من الـ logs:**
```bash
docker compose -f backend-compose.yml logs -f
```

4. **اختبر Backend مباشرة:**
```bash
curl http://localhost:8000/api/settings
# أو من داخل الكونتينر:
docker exec -it agent-core curl http://localhost:8000/api/settings
```

### 2. خطأ WebSocket Connection Failed

**السبب:**
- WebSocket server غير شغال
- Port 8000 غير متاح
- URL خاطئ

**الحل:**

1. **تحقق من WebSocket URL في `.env.local`:**
```bash
cd /home/ai/ai-agent/frontend
cat .env.local
```

يجب أن يكون:
```
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://localhost:8000/ws/chat
```

2. **للإنتاج (على السيرفر):**
```
NEXT_PUBLIC_AGENT_API_URL=http://3.79.231.29:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://3.79.231.29:8000/ws/chat
```

3. **تحقق من أن Backend يستمع على Port 8000:**
```bash
netstat -tlnp | grep 8000
# أو
ss -tlnp | grep 8000
```

### 3. CORS Errors

**السبب:**
- Backend لا يسمح بالـ origin الخاص بالـ frontend

**الحل:**

1. **تحقق من `backend/app/main.py`:**
```python
origins = [
    "http://localhost:3000",
    "http://3.79.231.29:3000",  # Production
    "*",  # Development only
]
```

2. **أعد تشغيل Backend:**
```bash
docker compose -f backend-compose.yml restart
```

### 4. Frontend لا يتصل بالـ Backend

**السبب:**
- Environment variables غير صحيحة
- Backend على IP مختلف

**الحل:**

1. **حدّث `.env.local`:**
```bash
cd /home/ai/ai-agent/frontend
cat > .env.local << EOF
NEXT_PUBLIC_BACKEND_URL=http://3.79.231.29:8000
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8000
NEXT_PUBLIC_AGENT_WS_URL=ws://localhost:8000/ws/chat
EOF
```

2. **أعد تشغيل Frontend:**
```bash
cd /home/ai/ai-agent/frontend
npm run dev
```

### 5. Docker Container لا يشتغل

**السبب:**
- Docker daemon غير شغال
- Port conflict
- Image build failed

**الحل:**

1. **تحقق من Docker:**
```bash
sudo systemctl status docker
# أو
docker ps
```

2. **أعد بناء Image:**
```bash
cd /home/ai/ai-agent/backend
docker compose -f backend-compose.yml build --no-cache
docker compose -f backend-compose.yml up -d
```

3. **تحقق من الـ logs:**
```bash
docker compose -f backend-compose.yml logs
```

### 6. File Explorer لا يعمل

**السبب:**
- `file_explorer.py` غير موجود
- Path validation فاشل

**الحل:**

1. **تحقق من الملف:**
```bash
ls -la /home/ai/ai-agent/backend/app/tools/file_explorer.py
```

2. **اختبر File Explorer API:**
```bash
curl "http://localhost:8000/api/fs/list?path="
```

### 7. Settings لا تحفظ

**السبب:**
- Permissions على `memory/settings.json`
- Backend لا يكتب الملف

**الحل:**

1. **تحقق من Permissions:**
```bash
ls -la /home/ai/ai-agent/backend/app/memory/
```

2. **اختبر Settings API:**
```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"allow_shell": true}'
```

## خطوات التشخيص السريع

1. **Backend شغال؟**
   ```bash
   curl http://localhost:8000/api/settings
   ```

2. **WebSocket يعمل؟**
   - افتح Browser DevTools → Network → WS
   - تحقق من connection status

3. **Frontend يقرأ Environment Variables؟**
   - افتح Browser Console
   - اطبع: `process.env.NEXT_PUBLIC_AGENT_API_URL`

4. **CORS Issues؟**
   - افتح Browser DevTools → Console
   - ابحث عن CORS errors

## نصائح إضافية

- استخدم `docker compose logs -f` لمتابعة الـ logs
- استخدم Browser DevTools Network tab لمراقبة Requests
- تحقق من Firewall rules إذا كان Backend على سيرفر بعيد
- استخدم `curl` لاختبار APIs مباشرة قبل اختبار Frontend

