# Nginx Configuration for AI Agent

This directory contains the nginx configuration for the AI Agent application.

## Domain Configuration
- **Domain**: ai-agent.bankid-sy.com
- **IP**: 3.76.209.35

## Directory Structure
```
nginx/
├── nginx.conf          # Main nginx configuration
├── conf.d/
│   └── default.conf    # Server block configuration
├── ssl/                # SSL certificates (cert.pem, key.pem)
├── logs/               # Nginx access and error logs
├── www/                # Web root for Let's Encrypt challenges
└── generate-ssl.sh     # Script to generate self-signed certificates
```

## Setup Instructions

### 1. Generate SSL Certificates

For initial setup with self-signed certificates:
```bash
cd /home/ai/ai-agent/nginx
./generate-ssl.sh
```

For production with Let's Encrypt:
```bash
# Make sure nginx is running first
docker-compose -f docker-compose.prod.yml up -d nginx

# Generate Let's Encrypt certificate
docker run -it --rm \
  -v $(pwd)/nginx/www:/var/www/certbot \
  -v $(pwd)/nginx/ssl:/etc/letsencrypt \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d ai-agent.bankid-sy.com

# Update nginx config to use Let's Encrypt paths
# Change in conf.d/default.conf:
# ssl_certificate /etc/nginx/ssl/cert.pem;
# ssl_certificate_key /etc/nginx/ssl/key.pem;
# To:
# ssl_certificate /etc/nginx/ssl/live/ai-agent.bankid-sy.com/fullchain.pem;
# ssl_certificate_key /etc/nginx/ssl/live/ai-agent.bankid-sy.com/privkey.pem;
```

### 2. Start Nginx with Docker Compose

```bash
cd /home/ai/ai-agent
docker-compose -f docker-compose.prod.yml up -d nginx
```

### 3. Verify Configuration

```bash
# Check nginx configuration
docker exec ai-agent-nginx nginx -t

# View nginx logs
docker logs ai-agent-nginx

# Check if nginx is running
docker ps | grep nginx
```

## Configuration Details

### Routing
- **Frontend (/)**: Proxies to `frontend:3000` (Next.js application)
- **Backend API (/api)**: Proxies to `backend:8000` (FastAPI backend)
- **WebSocket (/ws)**: Proxies to `backend:8000` for WebSocket connections
- **Health Check (/health)**: Returns healthy status

### SSL/TLS
- Supports TLS 1.2 and 1.3
- Modern cipher suites
- Security headers enabled
- HTTP to HTTPS redirect

### Performance
- Gzip compression enabled
- Keep-alive connections
- Connection pooling
- Client max body size: 100MB

## Troubleshooting

### Check nginx logs
```bash
docker logs ai-agent-nginx
tail -f nginx/logs/error.log
tail -f nginx/logs/access.log
```

### Test nginx configuration
```bash
docker exec ai-agent-nginx nginx -t
```

### Reload nginx configuration
```bash
docker exec ai-agent-nginx nginx -s reload
```

### Restart nginx container
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

## DNS Configuration

Make sure your DNS is configured to point the domain to the server IP:
```
ai-agent.bankid-sy.com  A  3.76.209.35
```

## Firewall

Ensure ports 80 and 443 are open:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

