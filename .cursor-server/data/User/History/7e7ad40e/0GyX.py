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

    # Simple keyword-based decision for common queries to avoid LLM call
    user_lower = user_message.lower().strip()
    
    # Check for service-related queries
    if any(keyword in user_lower for keyword in ["nginx", "service", "check", "status", "systemctl"]):
        if "nginx" in user_lower:
            return {
                "mode": "tool",
                "tool_name": "check_service",
                "tool_args": "nginx",  # check_service.run() takes a string argument, not keyword
                "answer": "",
                "thought": "nginx service check detected",
            }
    
    # Check for file reading queries
    if any(keyword in user_lower for keyword in ["read", "file", "show", "content", "cat"]):
        # Extract filename if possible
        words = user_lower.split()
        for i, word in enumerate(words):
            if word in ["read", "file", "show", "cat"] and i + 1 < len(words):
                filename = words[i + 1]
                if "/" in filename or "." in filename:
                    return {
                        "mode": "tool",
                        "tool_name": "read_file",
                        "tool_args": {"path": filename},
                        "answer": "",
                        "thought": "file read detected",
                    }

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
- Keep answers SHORT and DIRECT.

JSON ONLY.
""".strip()

    history_text = _build_history_text(history)

    user_prompt = (
        f"User message:\n{user_message}\n"
        f"Reply with SHORT answer or tool usage."
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
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[Agent] think_and_act called with message: {user_message[:100]}")
    
    try:
        history = load_memory()
        logger.debug(f"[Agent] Loaded {len(history)} messages from memory")
    except Exception as e:
        logger.warning(f"[Agent] Error loading memory: {e}")
        print(f"[Agent] Error loading memory: {e}")
        history = []
    
    try:
        logger.info(f"[Agent] Calling _decide_action")
        decision = _decide_action(user_message, history)
        logger.info(f"[Agent] Decision: mode={decision.get('mode')}, tool={decision.get('tool_name')}")
    except Exception as e:
        logger.error(f"[Agent] Error in decision: {e}")
        print(f"[Agent] Error in decision: {e}")
        traceback.print_exc()
        # Fallback to direct LLM call
        try:
            logger.info(f"[Agent] Fallback: calling llm_text directly")
            final = llm_text(user_message).strip()
            if not final:
                logger.warning(f"[Agent] Fallback llm_text returned empty")
                final = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."
        except Exception as e2:
            logger.error(f"[Agent] Fallback llm_text failed: {e2}")
            final = f"⚠️ حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى. (Error: {str(e2)})"
        
        # Save to memory
        try:
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": final})
            save_memory(history)
        except Exception as e3:
            logger.warning(f"[Agent] Error saving memory: {e3}")
        
        logger.info(f"[Agent] Returning fallback response: {len(final)} characters")
        return final

    # TOOL MODE
    if decision["mode"] == "tool" and decision.get("tool_name") in TOOLS:
        tool_name = decision["tool_name"]
        tool_args = decision["tool_args"]
        logger.info(f"[Agent] Using tool: {tool_name} with args: {tool_args}")

        try:
            tool_fn = TOOLS[tool_name]

            if tool_name == "run_shell":
                if not tool_args:
                    tool_args = {"cmd": "ls -la"}
                # run_shell expects dict with "cmd" key
                if isinstance(tool_args, dict):
                    output = tool_fn(**tool_args)
                else:
                    output = tool_fn({"cmd": str(tool_args)})
            elif tool_name == "check_service":
                # check_service.run() takes a string argument directly
                if isinstance(tool_args, dict):
                    # Extract service name from dict if passed as dict
                    service_name = tool_args.get("service") or tool_args.get("svc") or list(tool_args.values())[0] if tool_args else "nginx"
                    output = tool_fn(service_name)
                else:
                    output = tool_fn(str(tool_args))
            elif tool_name == "read_file":
                # read_file.run() takes a string path
                if isinstance(tool_args, dict):
                    path = tool_args.get("path") or list(tool_args.values())[0] if tool_args else ""
                    output = tool_fn(path)
                else:
                    output = tool_fn(str(tool_args))
            else:
                # For other tools, try dict first, then string
                if isinstance(tool_args, dict):
                    output = tool_fn(**tool_args)
                else:
                    output = tool_fn(tool_args)

            output_str = str(output)
            logger.info(f"[Agent] Tool {tool_name} returned: {len(output_str)} characters")

        except Exception as e:
            logger.error(f"[Agent] Tool error ({tool_name}): {e}")
            output_str = f"Tool error: {e}"
            print(f"[Agent] Tool error ({tool_name}): {e}")

        # ⛔️ مهم جداً: منع LLM من الهذيان بعد run_shell
        if tool_name == "run_shell":
            final = output_str  
            logger.info(f"[Agent] Using tool output directly for run_shell")
        else:
            # For most tools, use output directly without LLM follow-up to save time
            # Only use LLM for complex tool outputs that need interpretation
            if tool_name == "check_service":
                # Format service check output nicely
                if "active" in output_str.lower() or "running" in output_str.lower():
                    final = f"✅ الخدمة تعمل بشكل صحيح.\n\n{output_str}"
                elif "inactive" in output_str.lower() or "stopped" in output_str.lower():
                    final = f"❌ الخدمة متوقفة.\n\n{output_str}"
                else:
                    final = f"ℹ️ حالة الخدمة:\n\n{output_str}"
            else:
                # For other tools, use output directly
                final = output_str

    else:
        # If answer is empty, try to generate one
        if not decision["answer"] or not decision["answer"].strip():
            logger.info(f"[Agent] Decision answer is empty, calling llm_text")
            try:
                final = llm_text(user_message).strip()
                # If still empty, provide fallback
                if not final:
                    logger.warning(f"[Agent] llm_text returned empty")
                    final = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."
            except Exception as e:
                logger.error(f"[Agent] Error in llm_text fallback: {e}")
                print(f"[Agent] Error in llm_text fallback: {e}")
                # If llm_text fails, provide error message
                final = f"⚠️ حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى. (Error: {str(e)})"
        else:
            logger.info(f"[Agent] Using decision answer: {len(decision['answer'])} characters")
            final = decision["answer"].strip()
    
    # Ensure final is never empty
    if not final or not final.strip():
        logger.error(f"[Agent] Final response is empty, using fallback")
        final = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."

    # Save memory
    try:
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": final})
        save_memory(history)
        logger.debug(f"[Agent] Saved to memory, total messages: {len(history)}")
    except Exception as e:
        logger.warning(f"[Agent] Error saving memory: {e}")
        print(f"[Agent] Error saving memory: {e}")

    logger.info(f"[Agent] Returning final response: {len(final)} characters")
    return final
