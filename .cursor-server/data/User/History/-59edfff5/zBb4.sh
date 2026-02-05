#!/bin/bash
# Script to debug build issues

set -e

echo "🔍 Debugging Frontend Build..."
echo "========================================"

cd /home/ai/ai-agent/frontend || exit 1

echo "1. Checking Node version..."
node --version
npm --version

echo ""
echo "2. Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install --legacy-peer-deps
else
    echo "   node_modules exists"
fi

echo ""
echo "3. Checking TypeScript..."
npx tsc --noEmit --skipLibCheck || echo "   TypeScript errors found (non-blocking)"

echo ""
echo "4. Checking ESLint..."
npm run lint || echo "   ESLint errors found (non-blocking)"

echo ""
echo "5. Attempting build..."
npm run build

echo ""
echo "✅ Build completed successfully!"

