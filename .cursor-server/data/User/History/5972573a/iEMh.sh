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

