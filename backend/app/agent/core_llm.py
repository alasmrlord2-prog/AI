import os
import json
import requests
from app.core.config import get_settings

# استخدام الإعدادات من config بدلاً من os.getenv مباشرة
# هذا يضمن أن المتغيرات من docker-compose.yml تُستخدم بشكل صحيح
settings = get_settings()
OLLAMA_URL = settings.OLLAMA_URL
MODEL_NAME = os.getenv("AGENT_MODEL", "llama3.2:1b")


def _check_ollama_connection():
    """التحقق من اتصال Ollama وتوفر الموديل"""
    try:
        # التحقق من أن Ollama يعمل
        health_check = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if health_check.status_code != 200:
            return False, f"Ollama service returned status {health_check.status_code}"
        
        # التحقق من وجود الموديل
        models = health_check.json().get("models", [])
        model_names = [m.get("name", "") for m in models]
        if MODEL_NAME not in model_names:
            return False, f"Model '{MODEL_NAME}' not found. Available models: {', '.join(model_names[:5])}"
        
        return True, None
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to Ollama at {OLLAMA_URL}. Make sure Ollama service is running."
    except requests.exceptions.Timeout:
        return False, f"Connection to Ollama timed out at {OLLAMA_URL}"
    except Exception as e:
        return False, f"Error checking Ollama: {str(e)}"


def _call_ollama(
    prompt: str,
    temperature: float = 0.2,
    num_predict: int = 256,
    timeout: int = 300,  # Increased to 300 seconds (5 minutes) to allow complex and long questions
) -> dict:
    """
    استدعاء عام لـ Ollama مع ضبط:
    - num_predict: عدد التوكينات المتوقعة
    - timeout: وقت الانتظار قبل الـ timeout (زيادة لضمان إجابة جميع الأسئلة)
    """
    # Skip connection check to save time - just try the request
    # التحقق من الاتصال يأخذ وقت، نستخدمه فقط عند الحاجة
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }

    # Try with retry logic for better reliability
    max_retries = 2
    for attempt in range(max_retries):
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=timeout,
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                # Retry with longer timeout on second attempt
                timeout = timeout * 1.5
                print(f"[LLM] Timeout on attempt {attempt + 1}, retrying with timeout={timeout}")
                continue
            raise ConnectionError(f"Ollama request timed out after {timeout} seconds after {max_retries} attempts. The model may be too slow.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # محاولة استخدام /api/chat كبديل
            try:
                chat_payload = {
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": num_predict,
                    },
                }
                r = requests.post(
                    f"{OLLAMA_URL}/api/chat",
                    json=chat_payload,
                    timeout=timeout,  # Reduced timeout
                )
                r.raise_for_status()
                response_data = r.json()
                # تحويل رد /api/chat لشكل /api/generate
                return {"response": response_data.get("message", {}).get("content", "")}
            except requests.exceptions.Timeout:
                raise ConnectionError(f"Ollama chat request timed out after {timeout} seconds.")
            except Exception:
                raise ConnectionError(
                    f"Ollama API endpoint not found. Tried /api/generate and /api/chat. "
                    f"Make sure Ollama is running at {OLLAMA_URL} and model '{MODEL_NAME}' is available."
                )
        raise


def llm_text(user_prompt: str) -> str:
    """
    رد نصي عادي للمستخدم.
    نسمح بعدد توكينات كبير جداً لضمان إجابة كاملة على جميع الأسئلة حتى لو كانت طويلة.
    """
    data = _call_ollama(
        user_prompt,
        temperature=0.4,
        num_predict=4096,  # Increased significantly to allow very long, complete responses
        timeout=300,  # Increased to 300 seconds (5 minutes) to ensure all questions are answered completely
    )
    return data.get("response", "").strip()


def llm_json(system_instructions: str, user_prompt: str) -> dict:
    """
    نطلب من الموديل يرجع JSON واحد فقط.
    نحدد num_predict أصغر (64) لأن JSON المفروض قصير جداً.
    """
    prompt = f"""{system_instructions.strip()}

User message:
{user_prompt}
"""

    json_enforce = """
You MUST reply with ONLY ONE valid JSON object.
JSON ONLY. No explanation, no markdown, no backticks.
"""

    full_prompt = prompt + "\n\n" + json_enforce

    data = _call_ollama(
        full_prompt,
        temperature=0.1,
        num_predict=1024,  # Increased to allow complete JSON responses
        timeout=180,  # Increased to 180 seconds for JSON to ensure complete responses
    )
    raw = data.get("response", "").strip()

    # محاولة parsing للـ JSON
    try:
        return json.loads(raw)
    except Exception:
        cleaned = raw.strip()
        # أحياناً الموديل بيرجع ```json ...``` نحاول ننضفها
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except Exception:
            # لو فشل كل شي، رجّع الرد الخام داخل dict
            return {"raw": raw}
