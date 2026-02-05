import os
import json
import traceback

from .core_llm import llm_text, llm_json
from app.tools.read_file import run as read_file_run
from app.tools.check_service import run as check_service_run
from app.tools.run_shell import run as run_shell_run

MEMORY_FILE = "memory/memory.json"

TOOLS = {
    "read_file": read_file_run,
    "check_service": check_service_run,
    "run_shell": run_shell_run,
}

# ===========================
# MEMORY FUNCTIONS
# ===========================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory(history):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def _build_history_text(history):
    lines = []
    for msg in history[-3:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        lines.append(f"{role.upper()}: {content}")
    return "\n".join(lines)

# ===========================
# HARD OVERRIDES
# ===========================

def _hard_rule_force_tool(user_message: str):
    triggers = [
        "شو الملفات",
        "شو في هون",
        "شو الموجود هون",
        "شو الموجود",
        "ls",
        "الملفات",
        "المجلد",
        "الدليل",
        "هون",
    ]

    text = user_message.strip().replace("؟", "")

    for t in triggers:
        if t in text:
            return {
                "mode": "tool",
                "tool_name": "run_shell",
                "tool_args": {"cmd": "ls -la"},
                "answer": "",
                "thought": "forced by rule",
            }

    return None


# ===========================
# DECISION LAYER
# ===========================

def _decide_action(user_message: str, history) -> dict:

    forced = _hard_rule_force_tool(user_message)
    if forced:
        return forced

    system = """
Return ONLY ONE JSON object:
{
  "mode": "answer" | "tool",
  "answer": "",
  "tool_name": "",
  "tool_args": {},
  "thought": ""
}

Rules:
- For ANY question about listing files, folders, 'ls', 'شو الملفات', use:
  tool_name = "run_shell", tool_args = {"cmd": "ls -la"}
- Use read_file when reading a file.
- Use check_service for service status.

JSON ONLY.
""".strip()

    history_text = _build_history_text(history)

    user_prompt = (
        f"Conversation history:\n{history_text}\n\n"
        f"User message:\n{user_message}\n"
    )

    try:
        result = llm_json(system, user_prompt)
    except Exception as e:
        err = f"decision failed: {e}"
        print(err)
        traceback.print_exc()
        # Try to get a text response as fallback
        try:
            fallback_answer = llm_text(user_message).strip()
            if not fallback_answer:
                fallback_answer = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."
        except Exception as e2:
            fallback_answer = f"⚠️ حدث خطأ أثناء معالجة طلبك: {str(e2)}. يرجى المحاولة مرة أخرى."
        
        return {
            "mode": "answer",
            "answer": fallback_answer,
            "tool_name": None,
            "tool_args": {},
            "thought": err,
            "raw": {},
        }

    mode = result.get("mode", "answer")
    if mode not in ["answer", "tool"]:
        mode = "answer"

    return {
        "mode": mode,
        "answer": result.get("answer", ""),
        "tool_name": result.get("tool_name"),
        "tool_args": result.get("tool_args") or {},
        "thought": result.get("thought", ""),
        "raw": result,
    }

# ===========================
# MAIN LOGIC
# ===========================

def think_and_act(user_message: str) -> str:
    """Main agent function - always returns a response, even on errors."""
    try:
        history = load_memory()
    except Exception as e:
        print(f"[Agent] Error loading memory: {e}")
        history = []
    
    try:
        decision = _decide_action(user_message, history)
    except Exception as e:
        print(f"[Agent] Error in decision: {e}")
        # Fallback to direct LLM call
        try:
            final = llm_text(user_message).strip()
            if not final:
                final = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."
        except Exception as e2:
            final = f"⚠️ حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى. (Error: {str(e2)})"
        
        # Save to memory
        try:
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": final})
            save_memory(history)
        except Exception:
            pass
        
        return final

    # TOOL MODE
    if decision["mode"] == "tool" and decision.get("tool_name") in TOOLS:
        tool_name = decision["tool_name"]
        tool_args = decision["tool_args"]

        try:
            tool_fn = TOOLS[tool_name]

            if tool_name == "run_shell" and not tool_args:
                tool_args = {"cmd": "ls -la"}

            if isinstance(tool_args, dict):
                output = tool_fn(**tool_args)
            else:
                output = tool_fn(tool_args)

            output_str = str(output)

        except Exception as e:
            output_str = f"Tool error: {e}"
            print(f"[Agent] Tool error ({tool_name}): {e}")

        # ⛔️ مهم جداً: منع LLM من الهذيان بعد run_shell
        if tool_name == "run_shell":
            final = output_str  
        else:
            try:
                follow_prompt = (
                    "Give short answer only, no inventions.\n"
                    f"User message: {user_message}\n"
                    f"Tool output:\n{output_str}\n"
                )
                final = llm_text(follow_prompt).strip()
                if not final:
                    final = output_str
            except Exception as e:
                print(f"[Agent] Error in follow-up LLM call: {e}")
                final = output_str

    else:
        # If answer is empty, try to generate one
        if not decision["answer"] or not decision["answer"].strip():
            try:
                final = llm_text(user_message).strip()
                # If still empty, provide fallback
                if not final:
                    final = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."
            except Exception as e:
                print(f"[Agent] Error in llm_text fallback: {e}")
                # If llm_text fails, provide error message
                final = f"⚠️ حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى. (Error: {str(e)})"
        else:
            final = decision["answer"].strip()
    
    # Ensure final is never empty
    if not final or not final.strip():
        final = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."

    # Save memory
    try:
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": final})
        save_memory(history)
    except Exception as e:
        print(f"[Agent] Error saving memory: {e}")

    return final
