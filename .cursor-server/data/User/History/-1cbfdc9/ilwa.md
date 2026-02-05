# 🚀 ابدأ من هنا - START HERE

## ⚡ 3 خطوات للبدء

### 1️⃣ شغّل النظام

```bash
docker-compose up -d
```

### 2️⃣ أنشئ البيانات الأولية

```bash
cd backend
python scripts/setup_initial_data.py
```

### 3️⃣ سجّل دخول

افتح: **http://localhost:3000/login**

---

## 📍 الواجهات - URLs المباشرة

### 🔐 تسجيل الدخول
**http://localhost:3000/login**

### 🏢 CRM
- **قائمة Tenants**: http://localhost:3000/crm/tenants
- **Dashboard**: http://localhost:3000/crm/tenants/{tenant_id}
- **Users**: http://localhost:3000/crm/tenants/{tenant_id}/users
- **Subscription**: http://localhost:3000/crm/tenants/{tenant_id}/subscription

### 🔐 IAM
- **Roles**: http://localhost:3000/iam/roles
- **Permissions**: http://localhost:3000/iam/permissions
- **Policies**: http://localhost:3000/iam/policies
- **Access Control**: http://localhost:3000/iam/access-control

---

## 🔧 السكربتات (6 فقط)

```bash
# Backend
./backend/start.sh
./backend/stop.sh
./backend/restart.sh

# Frontend
./frontend/start.sh
./frontend/stop.sh
./frontend/restart.sh
```

---

## 📚 الملفات المرجعية

- **README.md** - الدليل الشامل
- **HOW_TO_ACCESS.md** - كيف تصل لكل واجهة
- **DOCKER_SETUP.md** - دليل Docker
- **COMPLETE_GUIDE.md** - دليل كامل

---

**جاهز! 🎉**

