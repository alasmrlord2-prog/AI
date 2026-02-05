# تشغيل Nginx - حل مشكلة Cloudflare Error 522

## ✅ الحالة الحالية

- ✅ **Backend**: يعمل (ai-agent-backend-prod)
- ✅ **Frontend**: يعمل (ai-agent-frontend-prod)  
- ✅ **Postgres**: يعمل
- ✅ **Ollama**: يعمل
- ❌ **Nginx**: غير مشغّل (هذا يسبب Cloudflare Error 522)

## 🚀 حل المشكلة

### الطريقة 1: استخدام السكربت

```bash
cd /home/ai/ai-agent
./start_nginx.sh
```

### الطريقة 2: يدوياً

```bash
cd /home/ai/ai-agent
docker-compose -f docker-compose.prod.yml up -d nginx
```

### التحقق من حالة nginx

```bash
docker ps | grep nginx
docker logs ai-agent-nginx
```

## 🔍 استكشاف الأخطاء

### إذا فشل تشغيل nginx:

1. **تحقق من شهادات SSL:**
```bash
ls -la /home/ai/ai-agent/nginx/ssl/
```

2. **إذا لم تكن موجودة، أنشئها:**
```bash
cd /home/ai/ai-agent/nginx
./generate-ssl.sh
cd ..
```

3. **تحقق من المنافذ:**
```bash
sudo netstat -tlnp | grep -E ':(80|443)'
```

4. **افتح المنافذ في Firewall:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

5. **تحقق من إعدادات nginx:**
```bash
docker exec ai-agent-nginx nginx -t
```

## 📝 بعد تشغيل nginx

بعد تشغيل nginx بنجاح، يجب أن يعمل الموقع على:
- **https://ai-agent.bankid-sy.com**

ولن تظهر مشكلة Cloudflare Error 522.

## 🔄 الترتيب الصحيح للتشغيل الكامل

```bash
cd /home/ai/ai-agent

# 1. Backend
./start_backend.sh

# 2. Frontend (بعد 10 ثواني)
sleep 10
./start_frontend.sh

# 3. Nginx (بعد 10 ثواني) - مهم جداً!
sleep 10
./start_nginx.sh
```

## ✅ التحقق النهائي

```bash
# جميع الخدمات يجب أن تكون Up
docker ps | grep -E "nginx|frontend|backend|postgres|ollama"

# اختبار الموقع
curl -k https://ai-agent.bankid-sy.com/health
```

