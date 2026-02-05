#!/bin/bash

# ============================================
# Fix Dependencies - Install python3-dev
# ============================================

echo "🔧 Fixing Dependencies..."
echo "========================================"
echo ""

# Install python3-dev
echo "📦 Installing python3-dev and build tools..."
if command -v apt-get > /dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y python3-dev build-essential gcc
    echo "   ✅ python3-dev installed"
elif command -v yum > /dev/null 2>&1; then
    sudo yum install -y python3-devel gcc make
    echo "   ✅ python3-devel installed"
else
    echo "   ⚠️  Unknown package manager. Please install python3-dev manually."
    exit 1
fi

echo ""
echo "📦 Reinstalling dependencies..."
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -m pip install -r requirements.txt

echo ""
echo "✅ Done! You can now run: ./start_backend.sh"

