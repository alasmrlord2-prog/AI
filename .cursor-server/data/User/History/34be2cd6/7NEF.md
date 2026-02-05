# إصلاح ملف nginx لـ AAA

## المشكلة:
في ملف `/etc/nginx/sites-available/aaa.bankid-sy.com` السطر 82 يوجد خطأ إملائي:
```
proxy_pass http://1270.0.1:3002;
```

يجب أن يكون:
```
proxy_pass http://127.0.0.1:3002;
```

## الحل:

قم بتشغيل الأمر التالي كـ root:

```bash
sudo sed -i 's|http://1270\.0\.1:3002|http://127.0.0.1:3002|g' /etc/nginx/sites-available/aaa.bankid-sy.com
```

أو قم بتعديل الملف يدوياً:
```bash
sudo nano /etc/nginx/sites-available/aaa.bankid-sy.com
```

ثم غير السطر 82 من:
```
proxy_pass http://1270.0.1:3002;
```
إلى:
```
proxy_pass http://127.0.0.1:3002;
```

بعد التعديل، أعد تحميل nginx:
```bash
sudo systemctl reload nginx
```

## التحقق:
```bash
grep -n "1270\|127\.0\.0\.1" /etc/nginx/sites-available/aaa.bankid-sy.com
```

يجب أن ترى جميع الأسطر تحتوي على `127.0.0.1` وليس `1270.0.1`.

