#!/bin/bash

# ============================================
# Install Let's Encrypt SSL Certificate
# ============================================
# This script installs Let's Encrypt SSL certificate
# Domain: ai-agent.bankid-sy.com
# ============================================

set -e

PROJECT_DIR="/home/ai/ai-agent"
DOMAIN="ai-agent.bankid-sy.com"
EMAIL="khalilalesmael@gmail.com"

echo "🔐 Installing Let's Encrypt SSL Certificate..."
echo "========================================"
echo "Domain: $DOMAIN"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Check if nginx is running
if ! docker ps | grep -q "ai-agent-nginx"; then
    echo "⚠️  Nginx is not running!"
    echo "   Starting nginx first..."
    docker-compose -f docker-compose.prod.yml up -d nginx
    sleep 5
fi

# Create certbot directory if it doesn't exist
mkdir -p nginx/www

# Install certbot and get certificate
echo "📦 Installing certbot and getting certificate..."
docker run -it --rm \
  -v "$(pwd)/nginx/www:/var/www/certbot" \
  -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d "$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email

# Update nginx config to use Let's Encrypt certificates
echo ""
echo "📝 Updating nginx configuration..."
sed -i 's|ssl_certificate /etc/nginx/ssl/cert.pem;|ssl_certificate /etc/nginx/ssl/live/ai-agent.bankid-sy.com/fullchain.pem;|g' nginx/conf.d/default.conf
sed -i 's|ssl_certificate_key /etc/nginx/ssl/key.pem;|ssl_certificate_key /etc/nginx/ssl/live/ai-agent.bankid-sy.com/privkey.pem;|g' nginx/conf.d/default.conf

# Reload nginx
echo "🔄 Reloading nginx..."
docker exec ai-agent-nginx nginx -s reload

echo ""
echo "✅ SSL certificate installed successfully!"
echo "========================================"
echo ""
echo "🌐 Your site is now available at:"
echo "   https://$DOMAIN"
echo ""
echo "💡 Certificate will auto-renew. To renew manually:"
echo "   ./renew-ssl.sh"
echo ""

