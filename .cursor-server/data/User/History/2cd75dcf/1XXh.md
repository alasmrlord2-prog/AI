# API Documentation

## Overview

The AI Agent Backend provides a RESTful API and WebSocket endpoints for interacting with the AI agent.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/register` - Register new user (admin only)
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/roles` - Get available roles

### Chat

- `POST /api/chat` - Send chat message
- `WebSocket /ws/chat` - WebSocket chat endpoint

### Settings

- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings

### Monitoring

- `GET /api/monitor` - Get system monitoring data
- `GET /metrics` - Prometheus metrics

### Tools

- `POST /api/tools/read_file` - Read file
- `POST /api/tools/run_shell` - Run shell command
- `POST /api/tools/service` - Check service status

### Billing

- `GET /api/billing/invoices` - Get invoices
- `GET /api/billing/subscriptions` - Get subscriptions
- `GET /api/billing/payment-methods` - Get payment methods

### Security

- `POST /api/security/scan_repo` - Scan repository for secrets
- `POST /api/security/scan_infra` - Scan infrastructure
- `GET /api/security/siem` - SIEM monitoring data

## WebSocket

Connect to `ws://localhost:8000/ws/chat` for real-time chat.

## Response Format

All responses are in JSON format:

```json
{
  "status": "success",
  "data": {...}
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes:

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

