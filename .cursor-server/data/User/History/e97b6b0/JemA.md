# Quick Start - Running Migrations

## ✅ الطريقة الأسهل (باستخدام Docker)

```bash
cd /home/ai/ai-agent

# 1. تأكد أن PostgreSQL يعمل
docker-compose ps postgres

# 2. شغّل migrations من داخل backend container
docker-compose exec -T backend alembic upgrade head
```

## 🔧 إذا فشلت الطريقة الأولى

### الطريقة البديلة 1: استخدام localhost

```bash
cd /home/ai/ai-agent/backend

# استخدم localhost بدلاً من postgres (لأنك على الـ host)
export DATABASE_URL="postgresql://aiagent:aiagent123@localhost:5432/ai_agent_db"

# شغّل migrations
python3 -m alembic upgrade head
```

### الطريقة البديلة 2: إنشاء script

```bash
cd /home/ai/ai-agent/backend

cat > run_migrations.sh << 'EOF'
#!/bin/bash
export DATABASE_URL="postgresql://aiagent:aiagent123@localhost:5432/ai_agent_db"
python3 -m alembic upgrade head
EOF

chmod +x run_migrations.sh
./run_migrations.sh
```

## 🐛 حل المشاكل الشائعة

### مشكلة: "psycopg2 not installed"

**الحل:**
```bash
# تثبيت psycopg2-binary
pip3 install psycopg2-binary

# أو داخل Docker
docker-compose exec backend pip install psycopg2-binary
```

### مشكلة: "Connection refused"

**التحقق:**
```bash
# تحقق أن PostgreSQL يعمل
docker-compose ps postgres

# اختبر الاتصال
docker-compose exec postgres psql -U aiagent -d ai_agent_db -c "SELECT 1;"
```

### مشكلة: "Database does not exist"

**إنشاء قاعدة البيانات:**
```bash
docker-compose exec postgres psql -U aiagent -c "CREATE DATABASE ai_agent_db;"
```

## 📋 التحقق من النجاح

```bash
# تحقق من الجداول المنشأة
docker-compose exec postgres psql -U aiagent -d ai_agent_db -c "\dt"

# تحقق من revision الحالي
docker-compose exec -T backend alembic current
```

## 🚀 بعد نجاح Migrations

```bash
# أعد تشغيل backend
docker-compose restart backend

# تحقق من logs
docker-compose logs backend | tail -20
```

