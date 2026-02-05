# إصلاح مشكلة Nginx و Cloudflare Error 522

## المشكلة

nginx يعمل لكن Cloudflare لا يستطيع الاتصال به (Error 522).

## الحلول

### 1. إعادة تحميل إعدادات nginx

```bash
cd /home/ai/ai-agent

# إعادة تحميل nginx بدون إيقاف
docker exec ai-agent-nginx nginx -s reload

# أو إعادة تشغيل nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### 2. التحقق من أن جميع الخدمات في نفس الشبكة

```bash
# تحقق من الشبكة
docker network inspect ai-agent_ai-agent-network | grep -A 5 "Containers"

# يجب أن ترى: nginx, frontend, backend, postgres, ollama
```

### 3. اختبار الاتصال من nginx إلى الخدمات

```bash
# اختبار الاتصال إلى frontend
docker exec ai-agent-nginx wget -O- http://frontend:3000 2>&1 | head -10

# اختبار الاتصال إلى backend
docker exec ai-agent-nginx wget -O- http://backend:8000/health 2>&1 | head -10
```

### 4. التحقق من السجلات

```bash
# سجلات nginx
docker logs ai-agent-nginx --tail 50

# سجلات frontend
docker logs ai-agent-frontend-prod --tail 20

# سجلات backend
docker logs ai-agent-backend-prod --tail 20
```

### 5. التحقق من المنافذ

```bash
# تحقق من أن المنافذ مفتوحة
sudo netstat -tlnp | grep -E ':(80|443)'

# يجب أن ترى nginx يستمع على 80 و 443
```

### 6. إعادة بناء وإعادة تشغيل nginx

```bash
cd /home/ai/ai-agent

# إيقاف nginx
docker-compose -f docker-compose.prod.yml stop nginx

# إعادة تشغيل nginx
docker-compose -f docker-compose.prod.yml up -d nginx

# انتظر قليلاً
sleep 5

# تحقق من الحالة
docker ps | grep nginx
```

### 7. اختبار محلي

```bash
# اختبار HTTP (يجب أن يعيد redirect إلى HTTPS)
curl -I http://localhost

# اختبار HTTPS
curl -k -I https://localhost

# اختبار health endpoint
curl -k https://localhost/health
```

## إذا استمرت المشكلة

### تحقق من Cloudflare Settings

1. **Proxy Status**: تأكد من أن Cloudflare في وضع "Proxied" (برتقالي)
2. **SSL/TLS Mode**: يجب أن يكون "Full" أو "Full (strict)"
3. **Always Use HTTPS**: مفعّل

### تحقق من Firewall

```bash
# فتح المنافذ
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# التحقق
sudo ufw status
```

### تحقق من DNS

```bash
# تأكد من أن DNS يشير إلى IP الصحيح
dig ai-agent.bankid-sy.com

# يجب أن ترى: 3.76.209.35
```

## الأوامر السريعة

```bash
# إعادة تشغيل nginx
docker-compose -f docker-compose.prod.yml restart nginx

# عرض السجلات
docker logs -f ai-agent-nginx

# اختبار الاتصال
docker exec ai-agent-nginx wget -O- http://frontend:3000
docker exec ai-agent-nginx wget -O- http://backend:8000/health
```

