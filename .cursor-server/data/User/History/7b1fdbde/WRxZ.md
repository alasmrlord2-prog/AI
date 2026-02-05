# 🚀 Scripts Guide

## Backend Scripts

### `./backend-start.sh`
تشغيل جميع خدمات الـ Backend (PostgreSQL, Ollama, Backend API)

### `./backend-stop.sh`
إيقاف جميع خدمات الـ Backend

### `./backend-restart.sh`
إعادة تشغيل جميع خدمات الـ Backend

## Frontend Scripts

### `./frontend-start.sh`
تشغيل جميع خدمات الـ Frontend (AI-Agent, CRM, AAA)

### `./frontend-stop.sh`
إيقاف جميع خدمات الـ Frontend

### `./frontend-restart.sh`
إعادة تشغيل جميع خدمات الـ Frontend

## All Services Scripts

### `./start-all.sh`
تشغيل كل شيء (Backend + Frontend)

### `./stop-all.sh`
إيقاف كل شيء (Backend + Frontend)

### `./restart-all.sh`
إعادة تشغيل كل شيء (Backend + Frontend)

## Docker Containers

جميع الخدمات تعمل في Docker containers:

- **ai-backend** - Backend API (port 8000)
- **ai-agent-postgres** - PostgreSQL Database (port 5432)
- **ai-agent-ollama** - Ollama Service (port 11434)
- **ai-agent-frontend** - AI-Agent Frontend (port 3000)
- **ai-agent-frontend-crm** - CRM Frontend (port 3001)
- **ai-agent-frontend-aaa** - AAA Frontend (port 3002)

## View Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend-ai-agent
docker-compose logs -f frontend-crm
docker-compose logs -f frontend-aaa

# All logs
docker-compose logs -f
```

