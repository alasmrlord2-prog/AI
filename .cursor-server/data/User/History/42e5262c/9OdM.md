# خيارات Cloudflare - حل مشكلة Error 522

## الخيار 1: تغيير SSL/TLS Mode في Cloudflare

### من "Full (strict)" إلى "Full":

1. اذهب إلى Cloudflare Dashboard
2. SSL/TLS → Overview
3. غيّر من "Full (strict)" إلى "Full"
4. احفظ التغييرات

**ملاحظة**: هذا يسمح لـ Cloudflare بالاتصال حتى لو كانت شهادة SSL على الخادم self-signed.

## الخيار 2: إزالة Cloudflare Proxy مؤقتاً (DNS Only)

1. اذهب إلى Cloudflare Dashboard
2. DNS → Records
3. ابحث عن `ai-agent.bankid-sy.com`
4. اضغط على السحابة البرتقالية لتغييرها إلى رمادية (DNS Only)
5. انتظر بضع دقائق

**ملاحظة**: هذا سيجعل الموقع متاحاً مباشرة بدون Cloudflare، لكن لن تحصل على حماية Cloudflare.

## الخيار 3: استخدام IP مباشرة

يمكنك الوصول للموقع مباشرة عبر IP:
- **http://3.76.209.35**
- **https://3.76.209.35** (إذا كان SSL يعمل)

## الخيار 4: إصلاح SSL Certificate على الخادم

إذا أردت البقاء على "Full (strict)"، يجب:
1. إنشاء شهادة SSL صالحة (Let's Encrypt)
2. تثبيتها على nginx

## التوصية

**للحل السريع**: غيّر SSL/TLS mode إلى "Full" في Cloudflare.

**للحل الدائم**: استخدم Let's Encrypt لإنشاء شهادة SSL صالحة.

