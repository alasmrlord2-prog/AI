# Deployment Guide

## Docker Compose (Recommended)

### Development

```bash
docker-compose up -d
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Manual Deployment

### Backend

1. Install dependencies
2. Set environment variables
3. Run migrations: `alembic upgrade head`
4. Start with uvicorn or gunicorn

### Frontend

1. Build: `npm run build`
2. Start: `npm start`

## Environment Variables

See `.env.example` files for required environment variables.

## Database Migrations

Always run migrations before deploying:

```bash
cd backend
alembic upgrade head
```

## Health Checks

- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`

## Monitoring

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- Loki: `http://localhost:3100`

## Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure CORS properly
- [ ] Enable HTTPS in production
- [ ] Set up firewall rules
- [ ] Configure backup strategy

