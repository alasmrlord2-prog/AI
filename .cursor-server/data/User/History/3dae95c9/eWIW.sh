#!/bin/bash

# Script to setup NGINX for CRM subdomain
# Run with: bash setup-nginx-crm.sh

echo "🔧 Setting up NGINX for CRM subdomain..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Copy config file
echo "📝 Copying NGINX configuration..."
cp /home/ai/ai-agent/nginx-crm-cloudflare.conf /etc/nginx/sites-available/crm.bankid-sy.com

# Create symlink
echo "🔗 Creating symlink..."
ln -sf /etc/nginx/sites-available/crm.bankid-sy.com /etc/nginx/sites-enabled/crm.bankid-sy.com

# Test configuration
echo "🧪 Testing NGINX configuration..."
if nginx -t; then
    echo "✅ NGINX configuration is valid"
    
    # Reload NGINX
    echo "🔄 Reloading NGINX..."
    systemctl reload nginx
    
    echo ""
    echo "✅ Setup complete!"
    echo "🌐 CRM should now be accessible at: https://crm.bankid-sy.com"
    echo ""
    echo "📋 To check status:"
    echo "   sudo systemctl status nginx"
    echo "   sudo tail -f /var/log/nginx/crm-access.log"
else
    echo "❌ NGINX configuration test failed!"
    exit 1
fi

