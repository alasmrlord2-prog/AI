#!/bin/bash
# Setup NGINX for all three services
set -e

echo "🚀 Setting up NGINX for all services..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script requires sudo. Please run with sudo."
    exit 1
fi

# Copy NGINX configurations
if [ -f "nginx-ai-agent-complete.conf" ]; then
    cp nginx-ai-agent-complete.conf /etc/nginx/sites-available/ai-agent.bankid-sy.com
    echo "✅ Copied ai-agent.bankid-sy.com config"
else
    echo "❌ nginx-ai-agent-complete.conf not found!"
    exit 1
fi

if [ -f "nginx-aaa-complete.conf" ]; then
    cp nginx-aaa-complete.conf /etc/nginx/sites-available/aaa.bankid-sy.com
    echo "✅ Copied aaa.bankid-sy.com config"
else
    echo "❌ nginx-aaa-complete.conf not found!"
    exit 1
fi

if [ -f "nginx-crm-complete.conf" ]; then
    cp nginx-crm-complete.conf /etc/nginx/sites-available/crm.bankid-sy.com
    echo "✅ Copied crm.bankid-sy.com config"
else
    echo "❌ nginx-crm-complete.conf not found!"
    exit 1
fi

# Enable sites
ln -sf /etc/nginx/sites-available/ai-agent.bankid-sy.com /etc/nginx/sites-enabled/ 2>/dev/null || true
ln -sf /etc/nginx/sites-available/aaa.bankid-sy.com /etc/nginx/sites-enabled/ 2>/dev/null || true
ln -sf /etc/nginx/sites-available/crm.bankid-sy.com /etc/nginx/sites-enabled/ 2>/dev/null || true

echo "✅ Enabled all NGINX sites"
echo ""

# Test NGINX configuration
echo "Testing NGINX configuration..."
if nginx -t; then
    echo "✅ NGINX configuration is valid"
else
    echo "❌ NGINX configuration test failed!"
    exit 1
fi
echo ""

# Reload NGINX
echo "Reloading NGINX..."
if systemctl reload nginx; then
    echo "✅ NGINX reloaded successfully"
else
    echo "❌ Failed to reload NGINX!"
    exit 1
fi

echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "  1. Start Backend: cd backend && ./start.sh"
echo "  2. Start Frontends: cd frontend && ./pm2-start.sh"

