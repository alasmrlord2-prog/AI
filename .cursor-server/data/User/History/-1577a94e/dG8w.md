# إزالة Cloudflare Proxy - حل Error 522

## المشكلة
لا يمكنك تغيير SSL/TLS mode من "Full (strict)" في Cloudflare.

## الحل: إزالة Cloudflare Proxy (DNS Only)

### الخطوات:

1. **اذهب إلى Cloudflare Dashboard**
   - https://dash.cloudflare.com
   - اختر domain: `bankid-sy.com`

2. **اذهب إلى DNS → Records**

3. **ابحث عن السجل:**
   - Name: `ai-agent`
   - Type: `A`
   - Content: `3.76.209.35`

4. **اضغط على السحابة البرتقالية** (Proxy enabled)
   - ستتحول إلى رمادية (DNS Only)
   - هذا يعني أن Cloudflare لن يعمل كـ proxy

5. **انتظر 1-2 دقيقة** حتى يتم التحديث

### بعد إزالة Proxy:

- ✅ الموقع سيكون متاحاً مباشرة على: `http://ai-agent.bankid-sy.com`
- ✅ لن تحصل على حماية Cloudflare (DDoS, WAF, etc.)
- ✅ لكن Error 522 سيختفي

## بديل: استخدام IP مباشرة

إذا لم تستطع تغيير DNS، يمكنك الوصول مباشرة:

- **HTTP**: http://3.76.209.35
- **HTTPS**: https://3.76.209.35 (إذا كان SSL يعمل)

## ملاحظة مهمة

بعد إزالة Cloudflare Proxy، يجب أن:
1. nginx يعمل على المنافذ 80 و 443
2. Firewall يسمح بالمنافذ 80 و 443
3. SSL certificates موجودة على الخادم

