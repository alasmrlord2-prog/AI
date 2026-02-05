#!/bin/bash
# Start all frontends using PM2
set -e

cd "$(dirname "$0")"

echo "🚀 Starting all frontends with PM2..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 is not installed. Installing..."
    npm install -g pm2
fi

# Start all services
pm2 start ../ecosystem.config.js

echo ""
echo "✅ All frontends started with PM2!"
echo ""
echo "📝 Useful commands:"
echo "   pm2 status          - View status"
echo "   pm2 logs            - View logs"
echo "   pm2 stop all        - Stop all"
echo "   pm2 restart all     - Restart all"
echo "   pm2 delete all      - Delete all"
echo "   pm2 save            - Save current process list"
echo "   pm2 startup         - Setup startup script"

