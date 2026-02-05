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

## المشاكل التي تم حلها

### 1. مشكلة اتصال Chat مع Ollama

**المشكلة:**
- كان الكود يستخدم `http://localhost:11434` كقيمة افتراضية
- في Docker، يجب استخدام `http://ollama:11434` (اسم الخدمة في docker-compose)
- كان يحدث خطأ 404 عند محاولة الاتصال

**الحل:**
- تم تعديل `core_llm.py` لاستخدام `get_settings()` من `app.core.config`
- الآن يستخدم متغير البيئة `OLLAMA_URL` من docker-compose.yml بشكل صحيح
- القيمة الافتراضية في config هي `http://localhost:11434` للعمل محلياً
- في Docker، يتم تعيينها تلقائياً إلى `http://ollama:11434`

**الملفات المعدلة:**
- `backend/app/agent/core_llm.py`: استخدام config بدلاً من os.getenv مباشرة

### 2. مشكلة قراءة الملفات - تقييد المسارات

**المشكلة:**
- كان الكود يحد قراءة الملفات فقط لمسار `/home/ai/`
- أي مسار نسبي كان يُحوّل تلقائياً إلى `/home/ai/...`
- هذا يمنع قراءة الملفات من أي مكان آخر على السيرفر

**الحل:**
- تم تعديل `read_file.py` للسماح بقراءة أي ملف من أي مسار مطلق على السيرفر
- المسارات النسبية الآن تُحوّل بناءً على مجلد العمل الحالي
- إضافة معالجة أفضل للأخطاء (Permission denied, etc.)
- يمكن الآن قراءة الملفات من أي مكان مثل `/etc/`, `/var/log/`, `/opt/`, إلخ

**الملفات المعدلة:**
- `backend/app/tools/read_file.py`: إزالة القيد على `/home/ai/` فقط

**ملاحظات الأمان:**
- يجب التأكد من صلاحيات الوصول للملفات الحساسة
- يمكن إضافة قائمة سوداء للمسارات المحظورة إذا لزم الأمر

### 3. مشكلة فحص حالة الخدمات

**المشكلة:**
- كان يعتمد فقط على `systemctl` الذي قد لا يكون متوفراً في جميع البيئات
- فشل في فحص الخدمات على سيرفرات لا تستخدم systemd
- خريطة أسماء العمليات كانت محدودة

**الحل:**
- تحسين `check_service.py` لاستخدام طرق متعددة للفحص:
  1. `systemctl` (إذا متوفر) - الطريقة الأساسية
  2. `psutil` للبحث في قائمة العمليات الجارية
  3. `pgrep` كبديل للبحث عن العمليات
  4. `ps aux` كحل أخير
- إضافة المزيد من أسماء الخدمات الشائعة في خريطة العمليات:
  - ollama, prometheus, grafana, loki, promtail
  - mariadb, mongodb, elasticsearch, kafka
  - وغيرها من الخدمات الشائعة

**الملفات المعدلة:**
- `backend/app/tools/check_service.py`: تحسين آلية الفحص وإضافة المزيد من أسماء الخدمات

**النتيجة:**
- يعمل الآن على أي سيرفر بغض النظر عن نظام إدارة الخدمات المستخدم
- يمكن فحص أي خدمة على السيرفر مباشرة

## الميزات المتاحة

### قراءة الملفات
- يمكن قراءة أي ملف على السيرفر من أي مسار بناءً على الإعدادات
- دعم المسارات المطلقة والنسبية
- معالجة أخطاء واضحة (ملف غير موجود، صلاحيات، إلخ)
- **إعدادات التحكم بالمسارات:**
  - `allowed_paths`: قائمة المسارات المسموحة (فارغة = السماح بكل المسارات)
  - `restricted_paths`: قائمة المسارات المحظورة (افتراضي: `/proc/kcore`, `/dev/mem`, `/sys/kernel`)
  - `base_path`: المسار الأساسي للعمل (افتراضي: المسار الحالي `/app` داخل container)

### فحص الخدمات
- فحص حالة أي خدمة على السيرفر
- يعمل مع systemd وبدونه
- دعم Docker containers (فحص containers مباشرة)
- دعم واسع لأسماء الخدمات الشائعة
- معلومات مفصلة عن العمليات (PID, CPU, Memory)

### Chat Agent
- اتصال صحيح مع Ollama في Docker
- دعم المحادثة بالعربية والإنجليزية
- استخدام الأدوات (tools) تلقائياً عند الحاجة

## إعدادات النظام

جميع الميزات تعمل بناءً على الإعدادات في `backend/app/memory/settings.json`:

```json
{
  "allow_read_file": true,
  "allowed_paths": [],  // فارغة = السماح بكل المسارات
  "restricted_paths": ["/proc/kcore", "/dev/mem"],  // مسارات محظورة
  "base_path": null  // null = استخدام المسار الحالي
}
```

### التحكم بالمسارات:
- **`allowed_paths`**: إذا كانت فارغة `[]`، يسمح بكل المسارات. إذا كانت محددة، يسمح فقط بالمسارات المحددة.
- **`restricted_paths`**: قائمة المسارات المحظورة دائماً (مثل `/proc/kcore`, `/dev/mem`).
- **`base_path`**: المسار الأساسي للعمل. داخل Docker container عادة `/app`.

### أمثلة:
- قراءة ملف من `/app/README.md` (داخل container)
- قراءة ملف من `/etc/nginx/nginx.conf` (إذا كان مسموح)
- فحص خدمة `ssh`, `docker`, `ollama`, إلخ
