# مسارات الاختبار - Test Paths

## 📁 مسارات لاختبار Read File

### مسارات Backend (موجودة)
```bash
# ملفات Backend
app/main.py
app/core/config.py
app/core/permissions.py
app/models/settings.py
app/api/tools.py
app/api/permissions.py
app/tools/read_file.py
app/tools/run_shell.py

# ملفات الإعدادات
memory/settings.json
memory/pending_actions.json
backend.log

# ملفات المشروع
README.md
HOW_TO_RUN.md
TROUBLESHOOTING.md
requirements.txt
```

### مسارات النظام (للاختبار)
```bash
# ملفات النظام العامة
/etc/hosts
/etc/resolv.conf
/etc/os-release
/etc/passwd
/etc/group

# ملفات Logs
/var/log/syslog
/var/log/auth.log
/var/log/dpkg.log

# ملفات Network
/etc/network/interfaces
/etc/hostname

# ملفات Docker (إن وجدت)
/etc/docker/daemon.json
/var/lib/docker/containers/
```

### مسارات Frontend (إن وجدت)
```bash
# من Backend يمكن قراءة Frontend
../frontend/package.json
../frontend/README.md
../frontend/next.config.ts
../frontend/app/layout.tsx
```

## 🔒 مسارات لاختبار Security Scans

### Repository Scan
```bash
# مسارات المستودع
/home/ai/ai-agent/backend
/home/ai/ai-agent/frontend
/home/ai/ai-agent

# ملفات Config
/home/ai/ai-agent/docker-compose.yml
/home/ai/ai-agent/.env
/home/ai/ai-agent/backend/.env
```

### Infrastructure Scan
```bash
# ملفات Infrastructure
/etc/nginx/nginx.conf
/etc/apache2/apache2.conf
/etc/ssh/sshd_config
/etc/mysql/my.cnf
/etc/postgresql/*/postgresql.conf

# Docker Configs
/home/ai/ai-agent/docker-compose.yml
/home/ai/ai-agent/docker-compose.prod.yml
```

### Network Scan
```bash
# Network configurations
/etc/network/interfaces
/etc/netplan/*.yaml
/etc/hosts
/etc/resolv.conf
```

### System Scan
```bash
# System files
/etc/passwd
/etc/shadow (قد يحتاج permissions)
/etc/group
/etc/sudoers
/var/log/auth.log
/var/log/syslog
```

### Docker Scan
```bash
# Docker files
/etc/docker/daemon.json
/var/lib/docker/
/home/ai/ai-agent/docker-compose.yml
/home/ai/ai-agent/backend/Dockerfile
/home/ai/ai-agent/frontend/Dockerfile
```

## 🧪 أمثلة اختبار سريعة

### 1. اختبار Read File

```bash
# Backend file
curl -X POST http://localhost:8000/api/tools/read_file \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"path": "app/main.py"}'

# System file
curl -X POST http://localhost:8000/api/tools/read_file \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"path": "/etc/hosts"}'

# Project file
curl -X POST http://localhost:8000/api/tools/read_file \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"path": "/home/ai/ai-agent/README.md"}'
```

### 2. اختبار Security Scans

```bash
# Repository Scan
curl -X POST http://localhost:8000/api/security/scan_repo \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"path": "/home/ai/ai-agent/backend", "max_files": 100}'

# Infrastructure Scan
curl -X POST http://localhost:8000/api/security/scan_infra \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"path": "/home/ai/ai-agent"}'

# Network Scan
curl -X POST http://localhost:8000/api/security/scan_network \
  -H "Authorization: Bearer YOUR_TOKEN"

# System Scan
curl -X POST http://localhost:8000/api/security/scan_system \
  -H "Authorization: Bearer YOUR_TOKEN"

# Docker Scan
curl -X POST http://localhost:8000/api/security/scan_docker \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ⚠️ مسارات محظورة (Restricted)

هذه المسارات محظورة افتراضياً في Settings:

```bash
/proc/kcore      # Kernel core
/dev/mem         # Memory device
/sys/kernel      # Kernel sysfs
```

## ✅ مسارات آمنة للاختبار

### Backend Files
```bash
app/main.py
app/core/permissions.py
app/models/settings.py
backend.log
memory/settings.json
README.md
```

### System Files (قراءة فقط)
```bash
/etc/hosts
/etc/os-release
/etc/passwd
/etc/group
/var/log/syslog
```

### Project Files
```bash
/home/ai/ai-agent/README.md
/home/ai/ai-agent/HOW_TO_RUN.md
/home/ai/ai-agent/TROUBLESHOOTING.md
/home/ai/ai-agent/docker-compose.yml
```

## 🎯 اختبارات موصى بها

### 1. اختبار Read File
```bash
# ✅ يجب أن يعمل
app/main.py
/etc/hosts
README.md

# ⚠️ قد يحتاج permissions
/etc/shadow
/var/log/auth.log
```

### 2. اختبار Security Scans
```bash
# ✅ Repository Scan
/home/ai/ai-agent/backend

# ✅ Infrastructure Scan  
/home/ai/ai-agent

# ✅ Network Scan
(لا يحتاج path)

# ✅ System Scan
(لا يحتاج path)
```

### 3. اختبار Permissions
```bash
# التحقق من الصلاحيات
curl "http://localhost:8000/api/permissions/validate?action=security.scan"
curl "http://localhost:8000/api/permissions/validate?action=tool.read_file"
curl "http://localhost:8000/api/permissions/validate?action=tool.run_shell"
```

## 📝 ملاحظات

1. **مسارات نسبية**: تعمل من المجلد الحالي (`/home/ai/ai-agent/backend`)
2. **مسارات مطلقة**: تعمل من جذر النظام
3. **Permissions**: بعض الملفات قد تحتاج صلاحيات خاصة
4. **Security**: المسارات الحساسة محظورة افتراضياً

