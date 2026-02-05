# 📧 إعداد Email Alerts - Setup Email Alerts

## 🔧 الخطوات:

### 1. إعداد Gmail App Password:

1. افتح Gmail → Settings → Security
2. فعّل "2-Step Verification"
3. أنشئ "App Password":
   - Google Account → Security → 2-Step Verification → App passwords
   - اختر "Mail" و "Other (Custom name)" → "AI Backend"
   - انسخ الـ password (16 حرف)

### 2. تحديث Configuration:

#### أ) `alertmanager/alertmanager.yml`:
```yaml
smtp_from: 'your-email@gmail.com'
smtp_auth_username: 'your-email@gmail.com'
smtp_auth_password: 'your-16-char-app-password'
```

#### ب) `prometheus-grafana-compose.yml` (Grafana):
```yaml
- GF_SMTP_USER=your-email@gmail.com
- GF_SMTP_PASSWORD=your-16-char-app-password
- GF_SMTP_FROM_ADDRESS=your-email@gmail.com
```

### 3. إعادة تشغيل:
```bash
cd /home/ai/ai-agent
docker compose -f prometheus-grafana-compose.yml restart
```

### 4. اختبار:
- افتح Prometheus: http://63.178.23.205:9090/alerts
- افتح Alertmanager: http://63.178.23.205:9093
- جرّب trigger alert (مثلاً: CPU عالي)

## 📧 Alerts المتاحة:

1. **HighCPUUsage** → Email
2. **HighMemoryUsage** → Email
3. **HighDiskUsage** → Email
4. **HighChatErrors** → Email (Critical)
5. **HighNetworkTraffic** → Email
6. **TooManyConnections** → Email
7. **BackendDown** → Email (Critical)

## ✅ بعد الإعداد:

- كل alert سيُرسل email تلقائياً
- Critical alerts → Subject: 🚨 CRITICAL
- Warning alerts → Subject: ⚠️ WARNING

