# AI Agent

## السكربتات

### Backend
- `start_backend.sh` - تشغيل Backend
- `restart_backend.sh` - إعادة تشغيل Backend
- `stop_backend.sh` - إيقاف Backend

### Frontend
- `start_frontend.sh` - تشغيل Frontend
- `restart_frontend.sh` - إعادة تشغيل Frontend
- `stop_frontend.sh` - إيقاف Frontend

## الاستخدام

```bash
# تشغيل Backend
./start_backend.sh

# تشغيل Frontend
./start_frontend.sh

# إعادة تشغيل
./restart_backend.sh
./restart_frontend.sh

# إيقاف
./stop_backend.sh
./stop_frontend.sh
```

## الدومين

- **الموقع**: http://ai-agent.bankid-sy.com
- **API**: http://ai-agent.bankid-sy.com/api

## ملاحظات

- تأكد من أن nginx يعمل على السيرفر
- تأكد من أن AWS Security Group يسمح بالمنفذ 80
- Cloudflare يجب أن يكون على "DNS only" (رمادي)
