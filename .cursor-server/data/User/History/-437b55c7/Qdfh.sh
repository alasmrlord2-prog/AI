#!/bin/bash

# Script to generate self-signed SSL certificate for ai-agent.bankid-sy.com
# For production, replace with Let's Encrypt certificates

DOMAIN="ai-agent.bankid-sy.com"
SSL_DIR="./ssl"

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Generate private key
openssl genrsa -out "$SSL_DIR/key.pem" 2048

# Generate certificate signing request
openssl req -new -key "$SSL_DIR/key.pem" -out "$SSL_DIR/csr.pem" \
    -subj "/C=SY/ST=Damascus/L=Damascus/O=AI Agent/CN=$DOMAIN"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in "$SSL_DIR/csr.pem" -signkey "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -extensions v3_req \
    -extfile <(echo "[v3_req]"; echo "subjectAltName=DNS:$DOMAIN,DNS:*.$DOMAIN,IP:3.76.209.35")

# Set proper permissions
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificates location: $SSL_DIR"
echo ""
echo "⚠️  Note: These are self-signed certificates. For production, use Let's Encrypt:"
echo "   docker run -it --rm -v \$(pwd)/nginx/www:/var/www/certbot -v \$(pwd)/nginx/ssl:/etc/letsencrypt certbot/certbot certonly --webroot -w /var/www/certbot -d $DOMAIN"

