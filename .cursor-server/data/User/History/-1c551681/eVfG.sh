#!/bin/bash
# Script to start Ollama for AI Agent

echo "=== تشغيل Ollama ==="
echo ""

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama مثبت"
    echo "تشغيل Ollama..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo "✅ Ollama بدأ التشغيل"
    echo ""
    echo "للتحقق:"
    echo "  curl http://localhost:11434/api/tags"
else
    echo "❌ Ollama غير مثبت"
    echo ""
    echo "التثبيت:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "أو استخدام Docker:"
    echo "  docker run -d -p 11434:11434 --name ollama ollama/ollama"
fi

echo ""
echo "بعد التشغيل، تحميل model:"
echo "  ollama pull llama2"
echo "  # أو"
echo "  ollama pull mistral"

