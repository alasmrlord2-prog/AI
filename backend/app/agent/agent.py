import time
import requests

# Wait for Ollama to wake up
while True:
    try:
        print("Checking Ollama...")
        requests.get("http://ollama:11434/api/tags", timeout=3)
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

