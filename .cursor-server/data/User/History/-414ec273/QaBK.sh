#!/bin/bash
# Stop all frontends using PM2
set -e

echo "🛑 Stopping all frontends with PM2..."

pm2 stop all

echo "✅ All frontends stopped!"

