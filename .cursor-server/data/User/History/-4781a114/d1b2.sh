#!/bin/bash
# Start CRM Frontend on port 3001
set -e

cd "$(dirname "$0")"

echo "🚀 Starting CRM Frontend on port 3001..."

# Set port environment variable
export PORT=3001
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Start Next.js
npm run dev -- -p 3001

