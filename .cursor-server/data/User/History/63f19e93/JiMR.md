# إصلاح مشكلة قاعدة البيانات - Database Fix

## المشكلة / Problem

الـ CRM router يعمل الآن ✅، لكن هناك مشكلة في الاتصال بقاعدة البيانات:
```
password authentication failed for user "aiagent"
```

## الحل / Solution

### الحل السريع: إعادة إنشاء قاعدة البيانات

```bash
cd /home/ai/ai-agent
./recreate-database.sh
```

**تحذير:** هذا سيحذف جميع البيانات الموجودة في قاعدة البيانات!

### الحل اليدوي:

```bash
# 1. إيقاف الخدمات
docker compose stop backend postgres

# 2. حذف الـ volume
docker compose down postgres
docker volume rm ai-agent_postgres_data

# 3. إعادة تشغيل PostgreSQL
docker compose up -d postgres

# 4. انتظر حتى يكون جاهزاً (30-60 ثانية)
sleep 30

# 5. إعادة تشغيل Backend
docker compose up -d backend

# 6. التحقق
curl http://localhost:8000/api/crm/tenants
```

## التحقق من الإصلاح / Verification

بعد إعادة إنشاء قاعدة البيانات:

1. **Health Check:**
```bash
curl http://localhost:8000/health
# يجب أن يعيد: {"status":"ok","service":"ai-backend"}
```

2. **CRM Endpoint:**
```bash
curl http://localhost:8000/api/crm/tenants
# يجب أن يعيد JSON (وليس error)
```

3. **إذا كان هناك migrations:**
```bash
# قد تحتاج لتشغيل migrations
docker compose exec backend alembic upgrade head
# أو
docker compose exec backend python -m app.db.migrate
```

## ملاحظات / Notes

- ✅ **الـ CRM router يعمل الآن!** المشكلة فقط في قاعدة البيانات
- بعد إعادة إنشاء قاعدة البيانات، قد تحتاج لإعادة إنشاء البيانات الأولية
- إذا كان لديك بيانات مهمة، احفظها قبل إعادة الإنشاء

## الخطوات التالية / Next Steps

1. شغل `./recreate-database.sh`
2. إذا كان هناك migrations، شغلها
3. أنشئ البيانات الأولية إذا لزم الأمر
4. اختبر الـ frontend

## الحالة الحالية / Current Status

| المكون | الحالة |
|--------|--------|
| CRM Router | ✅ مسجل (9 routes) |
| Backend | ✅ يعمل |
| Database | ❌ يحتاج إعادة إنشاء |

بعد إعادة إنشاء قاعدة البيانات، كل شيء سيعمل! 🎉

