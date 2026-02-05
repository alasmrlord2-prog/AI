import os
import json
from datetime import datetime
from .core_llm import llm_text
from app.tools.read_file import run as read_file_run
from app.tools.check_service import run as check_service_run
from app.tools.run_shell import run as run_shell_run
from app.tools.doc_search import run as doc_search_run
from app.tools.read_logs import run as read_logs_run
from app.tools.monitor import run as monitor_run

SHORT_MEMORY = "memory/memory.json"
LONG_MEMORY = "memory/long_memory.json"
LOGFILE = "logs/agent.log"

TOOLS = {
    "read_file": read_file_run,
    "check_service": check_service_run,
    "run_shell": run_shell_run,
    "doc_search": doc_search_run,
    "read_logs": read_logs_run,
    "monitor": monitor_run
}



def load_json(path):
    if not os.path.exists(path):
        return []
    return json.load(open(path, "r", encoding="utf-8"))


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def log(msg):
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {msg}\n")


def think_and_act(user_input):
    memory = load_json(SHORT_MEMORY)
    long_mem = load_json(LONG_MEMORY)

    system_prompt = f"""
أنت وكيل DevOps محلي. الأدوات المتاحة:
{list(TOOLS.keys())}

الذاكرة الطويلة:
{long_mem}

الذاكرة القصيرة:
{memory[-5:]}

مهمة المستخدم:
{user_input}

استخدم:
ACTION: tool
ARGS: value
عند الحاجة.
"""

    thought = llm_text(system_prompt)
    log(f"USER: {user_input}")
    log(f"AGENT_RAW: {thought}")

    memory.append({"user": user_input, "agent": thought})
    save_json(SHORT_MEMORY, memory)

    if "ACTION:" in thought:
        try:
            tool = thought.split("ACTION:")[1].split("\n")[0].strip()
            args = thought.split("ARGS:")[1].strip()

            if tool in TOOLS:
                result = TOOLS[tool](args)
                return f"🛠 tool: {tool}\n{result}"
            return "أداة غير معروفة"
        except:
            return "خطأ في تحليل رد النموذج"

    return thought


if __name__ == "__main__":
    while True:
        q = input("🧠: ")
        print(think_and_act(q))
