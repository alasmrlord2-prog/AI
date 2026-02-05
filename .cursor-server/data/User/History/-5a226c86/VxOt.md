# Quick Start Guide - Nginx Setup

## ✅ الإعداد مكتمل!

تم إعداد nginx مع الدومين والـ IP التاليين:
- **الدومين**: ai-agent.bankid-sy.com
- **IP**: 3.76.209.35

## 🚀 خطوات التشغيل

### 1. تشغيل nginx مع Docker

```bash
cd /home/ai/ai-agent
docker-compose -f docker-compose.prod.yml up -d nginx
```

### 2. التحقق من حالة nginx

```bash
docker ps | grep nginx
docker logs ai-agent-nginx
```

### 3. اختبار الإعداد

```bash
# اختبار الإعداد
docker exec ai-agent-nginx nginx -t

# فتح الموقع
curl -k https://ai-agent.bankid-sy.com/health
```

## 📝 ملاحظات مهمة

1. **SSL Certificates**: تم إنشاء شهادات SSL مؤقتة (self-signed). للاستخدام في الإنتاج، استخدم Let's Encrypt (راجع README.md)

2. **DNS**: تأكد من أن الدومين يشير إلى IP الخادم:
   ```
   ai-agent.bankid-sy.com  A  3.76.209.35
   ```

3. **Firewall**: تأكد من فتح المنافذ 80 و 443:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

4. **Backend & Frontend**: تأكد من تشغيل الخدمات الأخرى:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🔧 الأوامر المفيدة

```bash
# إعادة تحميل إعدادات nginx
docker exec ai-agent-nginx nginx -s reload

# إعادة تشغيل nginx
docker-compose -f docker-compose.prod.yml restart nginx

# عرض السجلات
docker logs -f ai-agent-nginx
tail -f nginx/logs/error.log
```

## 🌐 الوصول للموقع

- **HTTP**: http://ai-agent.bankid-sy.com (سيتم التوجيه تلقائياً إلى HTTPS)
- **HTTPS**: https://ai-agent.bankid-sy.com
- **API**: https://ai-agent.bankid-sy.com/api
- **Health Check**: https://ai-agent.bankid-sy.com/health

