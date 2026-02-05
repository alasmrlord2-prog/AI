#!/bin/bash
# Start AI-Agent Frontend on port 3000
set -e

cd "$(dirname "$0")"

echo "🚀 Starting AI-Agent Frontend on port 3000..."

# Set port environment variable
export PORT=3000
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Start Next.js
npm run dev -- -p 3000

