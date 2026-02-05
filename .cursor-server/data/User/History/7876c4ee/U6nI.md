# إعداد Nginx مباشرة على السيرفر

## تثبيت Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

## إنشاء ملف الإعداد

```bash
sudo nano /etc/nginx/sites-available/ai-agent.bankid-sy.com
```

## محتوى ملف الإعداد

يمكنك نسخ الملف الجاهز:

```bash
sudo cp /home/ai/ai-agent/nginx-config.txt /etc/nginx/sites-available/ai-agent.bankid-sy.com
```

أو إنشاء الملف يدوياً:

```bash
sudo nano /etc/nginx/sites-available/ai-agent.bankid-sy.com
```

ثم الصق المحتوى التالي:

```nginx
# Upstream servers
upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream frontend {
    server 127.0.0.1:3000;
    keepalive 32;
}

# HTTP server (no SSL)
server {
    listen 80;
    listen [::]:80;
    server_name ai-agent.bankid-sy.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Frontend (Next.js)
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # WebSocket support for backend
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## تفعيل الموقع

```bash
# إنشاء رابط رمزي
sudo ln -s /etc/nginx/sites-available/ai-agent.bankid-sy.com /etc/nginx/sites-enabled/

# اختبار الإعداد
sudo nginx -t

# إعادة تحميل nginx
sudo systemctl reload nginx

# تفعيل nginx عند بدء التشغيل
sudo systemctl enable nginx
```

## التحقق

```bash
# التحقق من حالة nginx
sudo systemctl status nginx

# اختبار الموقع
curl http://ai-agent.bankid-sy.com/health
```

## الأوامر المفيدة

```bash
# إعادة تحميل nginx
sudo systemctl reload nginx

# إعادة تشغيل nginx
sudo systemctl restart nginx

# عرض السجلات
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

