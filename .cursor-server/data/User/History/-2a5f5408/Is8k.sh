#!/bin/bash

# ============================================
# Renew Let's Encrypt SSL Certificate
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
DOMAIN="ai-agent.bankid-sy.com"

echo "🔄 Renewing SSL Certificate..."
echo "========================================"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Renew certificate
docker run -it --rm \
  -v "$(pwd)/nginx/www:/var/www/certbot" \
  -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
  certbot/certbot renew

# Reload nginx
echo ""
echo "🔄 Reloading nginx..."
docker exec ai-agent-nginx nginx -s reload

echo ""
echo "✅ SSL certificate renewed successfully!"
echo ""

