# ⚡ Quick Reference - مرجع سريع

## 🚀 التشغيل السريع

```bash
# تشغيل كل شيء
docker-compose up -d

# إعداد البيانات
cd backend && python scripts/setup_initial_data.py

# تسجيل الدخول
# http://localhost:3000/login
```

---

## 📍 URLs المباشرة

### Frontend
- Login: `http://localhost:3000/login`
- CRM Tenants: `http://localhost:3000/crm/tenants`
- IAM Roles: `http://localhost:3000/iam/roles`

### Backend
- API: `http://localhost:8000/api`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

## 🔧 السكربتات

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

## 🐳 Docker Commands

```bash
docker-compose up -d          # تشغيل
docker-compose down            # إيقاف
docker-compose restart         # إعادة تشغيل
docker-compose logs -f         # Logs
docker-compose ps              # الحالة
```

---

## 📡 API Endpoints الرئيسية

```
POST   /api/identity/login
GET    /api/crm/tenants
GET    /api/crm/tenants/{id}/dashboard
GET    /api/subscription/plans
GET    /api/access/roles
```

---

**للمزيد:** راجع `README.md` و `HOW_TO_ACCESS.md`

