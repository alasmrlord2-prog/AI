# 🚀 Quick Start - CRM + AAA

## خطوات البدء السريع

### 1. تشغيل Backend

```bash
cd /home/ai/ai-agent/backend
./start.sh
# أو
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend يعمل على: http://localhost:8000

---

### 2. تشغيل Frontend

```bash
cd /home/ai/ai-agent/frontend
./start.sh
# أو
npm run dev
```

✅ Frontend يعمل على: http://localhost:3000

---

### 3. إعداد البيانات الأولية

```bash
cd /home/ai/ai-agent/backend
python scripts/setup_initial_data.py
```

هذا الـ Script سينشئ:
- ✅ Tenant جديد
- ✅ Admin User
- ✅ 3 Plans (Basic, Pro, Enterprise)
- ✅ Subscription للـ Tenant
- ✅ Default Roles (owner, admin, member, viewer)
- ✅ Default Permissions

---

### 4. تسجيل الدخول

1. افتح: http://localhost:3000/login
2. استخدم البيانات اللي أنشأتها في الخطوة 3

---

### 5. الوصول للصفحات

#### CRM:
- http://localhost:3000/crm/tenants
- http://localhost:3000/crm/tenants/{tenant_id}

#### IAM:
- http://localhost:3000/iam/roles
- http://localhost:3000/iam/permissions
- http://localhost:3000/iam/policies
- http://localhost:3000/iam/access-control

---

## 📚 الوثائق الكاملة

- [دليل البدء الكامل](./CRM_AAA_START_GUIDE.md)
- [Architecture Docs](./backend/CRM_AAA_ARCHITECTURE.md)
- [API Quick Start](./backend/CRM_AAA_QUICK_START.md)
- [Frontend Docs](./frontend/CRM_IAM_FRONTEND.md)

---

## ⚡ Troubleshooting

### Backend لا يعمل؟
```bash
# تحقق من الـ Port
lsof -i :8000

# تحقق من الـ Logs
cd /home/ai/ai-agent/backend
tail -f logs/app.log
```

### Frontend لا يعمل؟
```bash
# تحقق من الـ Port
lsof -i :3000

# إعادة تثبيت
cd /home/ai/ai-agent/frontend
rm -rf node_modules
npm install
```

### مشاكل قاعدة البيانات؟
```bash
# تأكد من أن قاعدة البيانات موجودة
psql -U postgres -l

# إنشاء قاعدة البيانات
createdb ai_agent_db
```

---

**جاهز للاستخدام! 🎉**

