# 🚀 كيف تشغل نظام CRM + AAA

## الخطوات السريعة

### 1. شغّل Backend

```bash
cd /home/ai/ai-agent/backend
./start.sh
```

أو:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend رح يكون على: http://localhost:8000

---

### 2. شغّل Frontend

```bash
cd /home/ai/ai-agent/frontend
./start.sh
```

أو:

```bash
npm run dev
```

✅ Frontend رح يكون على: http://localhost:3000

---

### 3. أنشئ البيانات الأولية

```bash
cd /home/ai/ai-agent/backend
python scripts/setup_initial_data.py
```

هذا الـ Script رح يسألك:
- Email للـ Admin
- Password للـ Admin
- اسم الـ Tenant

ورح ينشئ:
- ✅ Tenant
- ✅ Admin User
- ✅ 3 Plans (Basic, Pro, Enterprise)
- ✅ Subscription
- ✅ Roles و Permissions

---

### 4. سجّل دخول

1. افتح: http://localhost:3000/login
2. استخدم الـ Email و Password اللي أدخلتهم

---

### 5. استخدم النظام

#### CRM:
- **قائمة Tenants**: http://localhost:3000/crm/tenants
- **Dashboard**: http://localhost:3000/crm/tenants/{tenant_id}

#### IAM:
- **Roles**: http://localhost:3000/iam/roles
- **Permissions**: http://localhost:3000/iam/permissions
- **Policies**: http://localhost:3000/iam/policies
- **Access Control**: http://localhost:3000/iam/access-control

---

## 🔧 إذا في مشاكل

### Backend ما بيشتغل؟

```bash
# شوف إذا الـ Port مشغول
lsof -i :8000

# شوف الـ Logs
cd /home/ai/ai-agent/backend
tail -f logs/app.log
```

### Frontend ما بيشتغل؟

```bash
# شوف إذا الـ Port مشغول
lsof -i :3000

# إعادة تثبيت
cd /home/ai/ai-agent/frontend
rm -rf node_modules
npm install
```

### قاعدة البيانات؟

```bash
# تأكد من إنها موجودة
psql -U postgres -l

# أنشئها إذا ما موجودة
createdb ai_agent_db
```

---

## 📚 وثائق إضافية

- [دليل البدء الكامل](./CRM_AAA_START_GUIDE.md)
- [Architecture](./backend/CRM_AAA_ARCHITECTURE.md)
- [API Docs](./backend/CRM_AAA_QUICK_START.md)

---

**جاهز! 🎉**

