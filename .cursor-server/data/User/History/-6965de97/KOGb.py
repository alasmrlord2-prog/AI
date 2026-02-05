"""Logs API endpoints."""
from fastapi import APIRouter
import os
import json
from app.core.config import get_settings

router = APIRouter(prefix="/api/logs", tags=["logs"])
settings = get_settings()


@router.get("")
async def get_logs(limit: int = 100):
    """Get last N lines from chat.log - optimized for large files."""
    chat_log_file = os.path.join(settings.LOG_DIR, "chat.log")
    if not os.path.exists(chat_log_file):
        return []
    
    try:
        file_size = os.path.getsize(chat_log_file)
        if file_size == 0:
            return []
        
        # Estimate: average line is ~200 bytes, so read last (limit * 300) bytes to be safe
        # But cap at 1MB to avoid reading too much
        max_read_size = min(limit * 300, 1024 * 1024)  # 1MB max
        read_size = min(max_read_size, file_size)
        
        # Read only the last portion of the file
        with open(chat_log_file, "rb") as f:
            # Seek to position that should contain last N lines
            f.seek(max(0, file_size - read_size))
            # Read the chunk
            chunk = f.read(read_size)
        
        # Decode and split into lines
        try:
            text = chunk.decode('utf-8', errors='ignore')
        except Exception:
            # If decode fails, try with different encoding
            try:
                text = chunk.decode('latin-1', errors='ignore')
            except Exception:
                text = ""
        
        # Split into lines and take last N
        all_lines = text.split('\n')
        # Filter empty lines and take last N
        lines = [line.strip() for line in all_lines if line.strip()][-limit:]
        
        # Parse JSON from each line
        items = []
        for line in lines:
            if not line:
                continue
            try:
                parsed = json.loads(line)
                items.append(parsed)
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue
        
        return items
    
    except Exception as e:
        # Fallback to simple read if optimized method fails
        try:
            with open(chat_log_file, "r", encoding="utf-8", errors='ignore') as f:
                all_lines = f.readlines()
    
            lines = all_lines[-limit:]
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
        except Exception as fallback_error:
            # If everything fails, return empty list
            print(f"Error reading logs: {e}, fallback also failed: {fallback_error}")
            return []

