#!/bin/bash
# Start AAA Frontend on port 3002
set -e

cd "$(dirname "$0")"

echo "🚀 Starting AAA Frontend on port 3002..."

# Set port environment variable
export PORT=3002
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Start Next.js
npm run dev -- -p 3002

