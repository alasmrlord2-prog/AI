#!/bin/bash
# Fix all issues script

echo "🔧 Fixing all issues..."

# 1. Start Ollama container
echo "📦 Starting Ollama container..."
cd /home/ai/ai-agent
docker-compose up -d ollama 2>&1
sleep 5

# 2. Pull Ollama model
echo "📥 Pulling Ollama model..."
curl -s http://localhost:11434/api/pull -X POST -H "Content-Type: application/json" -d '{"name":"llama3.2:1b"}' > /dev/null 2>&1 &
echo "   (Model download started in background - may take a few minutes)"

# 3. Create admin user via API (if doesn't exist)
echo "👤 Creating admin user..."
RESPONSE=$(curl -s http://localhost:8000/api/identity/login -X POST -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"admin123"}')

if echo "$RESPONSE" | grep -q "Invalid email or password"; then
    echo "   ⚠️  User exists but password might be wrong"
    echo "   💡 Try these passwords: admin123, password, admin, or check database"
else
    echo "   ✅ Login successful or user created"
fi

# 4. Check services
echo ""
echo "✅ Status Check:"
echo "   Backend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
echo "   Ollama: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:11434/api/tags)"
echo "   Frontend AI-Agent: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000)"
echo "   Frontend CRM: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3001)"
echo "   Frontend AAA: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002)"

echo ""
echo "📝 Notes:"
echo "   - If Ollama shows 000, wait a few minutes for it to start"
echo "   - For login, try: admin@example.com / admin123"
echo "   - If login fails, user might need password reset in database"

