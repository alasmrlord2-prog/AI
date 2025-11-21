"""Logs API endpoints."""
from fastapi import APIRouter
import os
import json
from app.core.config import get_settings

router = APIRouter(prefix="/api/logs", tags=["logs"])
settings = get_settings()


@router.get("")
async def get_logs(limit: int = 100):
    """Get last N lines from chat.log."""
    chat_log_file = os.path.join(settings.LOG_DIR, "chat.log")
    if not os.path.exists(chat_log_file):
        return []
    
    with open(chat_log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    lines = lines[-limit:]
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    
    return items

