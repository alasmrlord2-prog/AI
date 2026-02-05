# AI Agent Frontend - دليل شامل

## 📋 نظرة عامة

Frontend للنظام مبني على **Next.js 16** مع React 19 و TypeScript.

## 🏗️ البنية

```
frontend/
├── app/                    # Next.js App Router
│   ├── settings/          # صفحة الإعدادات
│   ├── security/           # Security Center
│   ├── cicd/              # CI/CD
│   ├── debugger/          # AI Debugger
│   └── ...
├── components/             # React Components
├── lib/                   # Utilities
├── start.sh              # سكربت بدء التشغيل
├── stop.sh               # سكربت إيقاف التشغيل
└── restart.sh            # سكربت إعادة التشغيل
```

## 🚀 البدء السريع

### 1. تثبيت المتطلبات

```bash
cd /home/ai/ai-agent/frontend
npm install
```

### 2. تشغيل Frontend

```bash
# طريقة 1: استخدام السكربت
./start.sh

# طريقة 2: يدوياً
npm run dev
```

### 3. إيقاف Frontend

```bash
./stop.sh
```

### 4. إعادة تشغيل Frontend

```bash
./restart.sh
```

## 🌐 الوصول

بعد التشغيل:
- **Local**: http://localhost:3000
- **Network**: http://0.0.0.0:3000

## ⚙️ الإعدادات

### Environment Variables

أنشئ ملف `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### تعديل API URL

في `app/api/config.ts` أو `.env.local`:

```typescript
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
```

## 📱 الصفحات الرئيسية

### Settings Page (`/settings`)
- Agent Permissions
- Tool Permissions
- Memory Settings
- Email Notifications

### Security Center (`/security`)
- Repository Scan
- Infrastructure Scan
- Network Scan
- SIEM Monitoring

### CI/CD (`/cicd`)
- Repository Management
- Pipeline Execution
- Deployment

### AI Debugger (`/debugger`)
- Error Analysis
- Auto-fix
- Log Monitoring

## 🛠️ التطوير

### Build للإنتاج

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

### Testing

```bash
npm test
```

## 📝 Logs

```bash
# عرض logs
tail -f /tmp/frontend.log

# أو
tail -f frontend.log
```

## 🔍 Troubleshooting

### Port 3000 مستخدم

```bash
# إيقاف العملية
lsof -ti:3000 | xargs kill -9

# أو
./stop.sh
```

### node_modules مفقود

```bash
npm install
```

### Build فشل

```bash
# تنظيف وبناء من جديد
rm -rf .next node_modules
npm install
npm run build
```

## 🔗 روابط مهمة

- [Backend README](../backend/README.md)
- [Project README](../README.md)
