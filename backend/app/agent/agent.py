import time
import requests
from app.core.config import get_settings

# Wait for Ollama to wake up
settings = get_settings()
ollama_url = settings.OLLAMA_URL if settings.OLLAMA_URL else "http://ollama:11434"  # Fallback for Docker
while True:
    try:
        print("Checking Ollama...")
        requests.get(f"{ollama_url}/api/tags", timeout=3)
        print("Ollama is ready!")
        break
    except Exception as e:
        print("Waiting for Ollama...", e)
        time.sleep(2)

from agent.think_and_act import think_and_act

if __name__ == "__main__":
    print("agent-core started")

    while True:
        try:
            out = think_and_act("hello from agent-core")
            print("LLM:", out)
        except Exception as e:
            print("ERROR:", e)

        time.sleep(5)

