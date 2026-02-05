# إدارة السيرفر على AWS

## 📋 السكريبتات المتوفرة

### 1. `shutdown_server.sh` - إيقاف السيرفر
إيقاف جميع الخدمات بشكل آمن وحفظ الإعدادات.

### 2. `startup_server.sh` - تشغيل السيرفر
تشغيل جميع الخدمات بعد إعادة تشغيل السيرفر مع استعادة الإعدادات.

### 3. `restart_server.sh` - إعادة تشغيل السيرفر
إيقاف ثم تشغيل جميع الخدمات.

---

## 🚀 الاستخدام السريع

### إيقاف السيرفر قبل إيقاف AWS Instance:
```bash
cd /home/ai/ai-agent
./shutdown_server.sh
```

### تشغيل السيرفر بعد إعادة تشغيل AWS Instance:
```bash
cd /home/ai/ai-agent
./startup_server.sh
```

### إعادة تشغيل السيرفر (بدون إيقاف AWS):
```bash
cd /home/ai/ai-agent
./restart_server.sh
```

---

## 📝 ما يفعله السكريبت

### عند الإيقاف (`shutdown_server.sh`):
1. ✅ يحفظ الإعدادات الحالية (IP, Hostname, Ports)
2. ✅ يوقف Backend بشكل آمن
3. ✅ يوقف Frontend
4. ✅ يتحقق من توقف جميع الخدمات
5. ✅ يحفظ كل شيء في `.server_config.json`

### عند التشغيل (`startup_server.sh`):
1. ✅ يقرأ الإعدادات المحفوظة
2. ✅ يكتشف IP الحالي تلقائياً
3. ✅ يتحقق من تغيير IP (إذا تغير)
4. ✅ يحرر المنافذ (8000, 3000)
5. ✅ يشغل Backend
6. ✅ يتحقق من أن Backend يعمل
7. ✅ يعرض معلومات السيرفر والـ URLs

---

## ⚙️ الإعدادات المحفوظة

يتم حفظ الإعدادات في `.server_config.json`:

```json
{
  "server_ip": "63.178.23.205",
  "hostname": "ip-172-31-20-228",
  "backend_port": 8000,
  "frontend_port": 3000,
  "shutdown_time": "2024-11-16T12:00:00Z",
  "last_startup_time": "2024-11-16T12:30:00Z"
}
```

---

## 🔄 سيناريو الاستخدام الكامل

### 1. قبل إيقاف AWS Instance:

```bash
# إيقاف جميع الخدمات وحفظ الإعدادات
cd /home/ai/ai-agent
./shutdown_server.sh

# الآن يمكنك إيقاف AWS Instance بأمان
```

### 2. بعد إعادة تشغيل AWS Instance:

```bash
# SSH إلى السيرفر
ssh user@your-server-ip

# تشغيل جميع الخدمات
cd /home/ai/ai-agent
./startup_server.sh
```

**النتيجة:**
- ✅ Backend يعمل على `http://YOUR_IP:8000`
- ✅ Frontend يحتاج تشغيل يدوي (أو يمكن إضافته للسكريبت)
- ✅ جميع الإعدادات محفوظة

---

## ⚠️ ملاحظات مهمة

### 1. IP Address
- إذا تغير IP السيرفر، ستحصل على تحذير
- إذا كنت تستخدم Domain، تأكد من تحديث DNS
- إذا كنت تستخدم IP مباشرة، قد تحتاج تحديث Frontend config

### 2. Frontend
- السكريبت لا يشغل Frontend تلقائياً
- شغّل Frontend يدوياً:
  ```bash
  cd /home/ai/ai-agent/frontend
  npm run dev  # للتطوير
  # أو
  npm run build && npm start  # للإنتاج
  ```

### 3. Environment Variables
- إذا كنت تستخدم `.env` files، تأكد من حفظها
- السكريبت لا يحفظ `.env` files تلقائياً

---

## 🔧 إضافة Frontend إلى السكريبت (اختياري)

إذا أردت إضافة Frontend تلقائياً، عدّل `startup_server.sh`:

```bash
# بعد Step 7، أضف:
echo "🌐 Step 8: Starting frontend..."
cd "$FRONTEND_DIR"
if [ -f "package.json" ]; then
    npm run dev > frontend.log 2>&1 &
    echo "   ✅ Frontend started"
else
    echo "   ⚠️  Frontend not found"
fi
cd "$SCRIPT_DIR"
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: IP تغير بعد إعادة التشغيل

**الحل:**
1. السكريبت سيعطيك تحذير
2. إذا كنت تستخدم Domain، حدث DNS:
   ```bash
   # مثال: تحديث DNS record
   # A record: your-domain.com -> NEW_IP
   ```
3. إذا كنت تستخدم IP مباشرة، حدث Frontend:
   ```bash
   # في frontend/.env.local
   NEXT_PUBLIC_AGENT_API_URL=http://NEW_IP:8000
   ```

### المشكلة: Backend لا يبدأ

**الحل:**
```bash
# تحقق من السجلات
tail -50 /home/ai/ai-agent/backend/backend.log

# تحقق من المنافذ
lsof -i:8000

# شغّل Backend يدوياً
cd /home/ai/ai-agent/backend
./start_backend.sh
```

### المشكلة: Ports محجوزة

**الحل:**
```bash
# تحرير المنافذ يدوياً
sudo lsof -ti:8000 | xargs sudo kill -9
sudo lsof -ti:3000 | xargs sudo kill -9

# ثم شغّل السكريبت مرة أخرى
./startup_server.sh
```

---

## 📊 Checklist بعد إعادة التشغيل

- [ ] ✅ Backend يعمل على port 8000
- [ ] ✅ يمكن الوصول إلى `http://YOUR_IP:8000/health`
- [ ] ✅ يمكن الوصول إلى `http://YOUR_IP:8000/docs`
- [ ] ✅ Frontend يعمل (إذا شغّلته)
- [ ] ✅ يمكن الوصول إلى `http://YOUR_IP:3000`
- [ ] ✅ جميع الخدمات تعمل بشكل صحيح

---

## 💡 نصائح

1. **استخدم Elastic IP على AWS:**
   - هذا يضمن أن IP لا يتغير
   - لا حاجة لتحديث DNS كل مرة

2. **استخدم Domain Name:**
   - أسهل في الإدارة
   - يمكن تحديث DNS بسهولة

3. **احفظ `.env` files:**
   - انسخ `.env` files قبل الإيقاف
   - أو استخدم AWS Secrets Manager

4. **راقب السجلات:**
   ```bash
   # Backend logs
   tail -f /home/ai/ai-agent/backend/backend.log
   
   # System logs
   journalctl -u your-service
   ```

---

## ✅ جاهز للاستخدام!

الآن يمكنك إيقاف وإعادة تشغيل السيرفر بأمان دون قلق! 🚀

