import os
import json
import requests

# عنوان خدمة Ollama - يستخدم من environment variable أو localhost كافتراضي
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
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
    timeout: int = 300,
) -> dict:
    """
    استدعاء عام لـ Ollama مع ضبط:
    - num_predict: عدد التوكينات المتوقعة (نخليه صغير لسرعة الرد)
    - timeout: وقت الانتظار قبل الـ timeout
    """
    # التحقق من الاتصال قبل المحاولة
    is_connected, error_msg = _check_ollama_connection()
    if not is_connected:
        raise ConnectionError(f"Ollama connection failed: {error_msg}")
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json()
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
                    timeout=timeout,
                )
                r.raise_for_status()
                response_data = r.json()
                # تحويل رد /api/chat لشكل /api/generate
                return {"response": response_data.get("message", {}).get("content", "")}
            except Exception:
                raise ConnectionError(
                    f"Ollama API endpoint not found. Tried /api/generate and /api/chat. "
                    f"Make sure Ollama is running at {OLLAMA_URL} and model '{MODEL_NAME}' is available."
                )
        raise


def llm_text(user_prompt: str) -> str:
    """
    رد نصي عادي للمستخدم.
    نسمح بعدد توكينات معقول (256) حتى ما يعلق.
    """
    data = _call_ollama(
        user_prompt,
        temperature=0.4,
        num_predict=256,
        timeout=300,
    )
    return data.get("response", "").strip()


def llm_json(system_instructions: str, user_prompt: str) -> dict:
    """
    نطلب من الموديل يرجع JSON واحد فقط.
    نحدد num_predict أصغر (128) لأن JSON المفروض قصير.
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
        num_predict=128,
        timeout=300,
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
