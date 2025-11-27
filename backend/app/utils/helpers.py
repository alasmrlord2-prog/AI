"""Helper utility functions."""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.settings import SettingsModel
from app.core.config import get_settings

settings = get_settings()


def log_chat(role: str, session_id: Optional[str], content: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Log chat messages to file."""
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    chat_log_file = os.path.join(settings.LOG_DIR, "chat.log")
    
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "session_id": session_id,
        "content": content,
        "meta": meta or {},
    }
    try:
        os.makedirs(os.path.dirname(chat_log_file), exist_ok=True)
        with open(chat_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except (PermissionError, OSError) as e:
        # Log to stderr if file logging fails
        import sys
        print(f"Warning: Could not write to chat log: {e}", file=sys.stderr)


def load_settings() -> SettingsModel:
    """Load settings from file."""
    settings_file = settings.SETTINGS_FILE
    if not os.path.exists(settings_file):
        return SettingsModel()
    
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SettingsModel(**data)
    except Exception:
        return SettingsModel()


def save_settings(s: SettingsModel) -> None:
    """Save settings to file."""
    settings_file = settings.SETTINGS_FILE
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(s.dict(), f, ensure_ascii=False, indent=2)

