#!/bin/bash

# ============================================
# Install Backend Dependencies
# ============================================

set -e

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

echo "📦 Installing Backend Dependencies..."
echo "========================================"
echo ""

# Find Python command
if command -v python3.11 > /dev/null 2>&1; then
    PYTHON_CMD="python3.11"
elif command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "🔍 Using Python: $($PYTHON_CMD --version)"
echo ""

# Check for Python development headers
echo "🔍 Checking for Python development headers..."
if ! $PYTHON_CMD -c "import sysconfig; sysconfig.get_path('include')" 2>/dev/null; then
    echo "   ⚠️  Python development headers not found"
    echo "   Installing python3-dev..."
    if command -v apt-get > /dev/null 2>&1; then
        sudo apt-get update -qq && sudo apt-get install -y python3-dev build-essential 2>/dev/null || {
            echo "   ⚠️  Could not install python3-dev automatically"
            echo "   Please run: sudo apt-get install python3-dev build-essential"
        }
    elif command -v yum > /dev/null 2>&1; then
        sudo yum install -y python3-devel gcc 2>/dev/null || {
            echo "   ⚠️  Could not install python3-dev automatically"
            echo "   Please run: sudo yum install python3-devel gcc"
        }
    else
        echo "   ⚠️  Please install python3-dev manually for your system"
    fi
else
    echo "   ✅ Python development headers found"
fi
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip --quiet
echo "   ✅ pip upgraded"
echo ""

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing from requirements.txt..."
    $PYTHON_CMD -m pip install -r requirements.txt
    echo ""
    echo "✅ All dependencies installed successfully!"
else
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Installation complete!"
echo ""
echo "💡 You can now run: ./start_backend.sh"

