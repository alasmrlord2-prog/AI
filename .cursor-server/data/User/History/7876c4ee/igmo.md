# 🌐 NGINX Setup - 3 مواقع منفصلة

## 📍 المواقع الثلاثة

1. **agent.bankid-sy.com** → الداشبورد الرئيسي (Agent Dashboard)
2. **crm.bankid-sy.com** → واجهة CRM (مستقلة)
3. **aaa.bankid-sy.com** → Backend API (AAA System)

---

## ✅ ملفات NGINX

### 1. agent.bankid-sy.com
**الملف:** `/etc/nginx/sites-available/ai-agent.bankid-sy.com`

```nginx
upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream frontend {
    server 127.0.0.1:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name ai-agent.bankid-sy.com;

    # Frontend (Dashboard)
    location / {
        proxy_pass http://frontend;
        # ... headers
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        # ... headers
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend;
        # ... headers
    }
}
```

### 2. crm.bankid-sy.com
**الملف:** `/etc/nginx/sites-available/crm.bankid-sy.com`

```nginx
upstream crm_frontend {
    server 127.0.0.1:3000;
    keepalive 32;
}

upstream aaa_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name crm.bankid-sy.com;

    # CRM Frontend
    location / {
        proxy_pass http://crm_frontend;
        # ... headers
    }

    # Backend API (shared)
    location /api {
        proxy_pass http://aaa_backend;
        # ... headers
    }

    # WebSocket
    location /ws {
        proxy_pass http://aaa_backend;
        # ... headers
    }

    # Health
    location /health {
        return 200 "crm ok\n";
    }
}
```

### 3. aaa.bankid-sy.com
**الملف:** `/etc/nginx/sites-available/aaa.bankid-sy.com`

```nginx
upstream aaa_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name aaa.bankid-sy.com;

    # Main API
    location / {
        proxy_pass http://aaa_backend;
        # ... headers
    }

    # WebSocket
    location /ws {
        proxy_pass http://aaa_backend;
        # ... headers
    }

    # Health
    location /health {
        return 200 "aaa ok\n";
    }
}
```

---

## 🔧 التطبيق

### 1. إنشاء الملفات

```bash
# في /etc/nginx/sites-available/
sudo nano crm.bankid-sy.com
sudo nano aaa.bankid-sy.com
```

### 2. إنشاء Symlinks

```bash
sudo ln -sf /etc/nginx/sites-available/crm.bankid-sy.com /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/aaa.bankid-sy.com /etc/nginx/sites-enabled/
```

### 3. اختبار وإعادة تحميل

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## ✅ التحقق

- ✅ `https://agent.bankid-sy.com` → الداشبورد الرئيسي
- ✅ `https://crm.bankid-sy.com` → واجهة CRM
- ✅ `https://aaa.bankid-sy.com` → Backend API

---

## 📝 ملاحظات

- جميع المواقع تستخدم نفس Backend (port 8000)
- CRM و Dashboard يستخدمان نفس Frontend (port 3000)
- Cloudflare يتعامل مع SSL
- كل موقع له Health check منفصل

