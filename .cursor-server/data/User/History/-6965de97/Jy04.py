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
        # Optimized: Read from end of file instead of loading entire file
        # This is much faster for large log files
        items = []
        buffer_size = 8192  # 8KB chunks
        file_size = os.path.getsize(chat_log_file)
        
        if file_size == 0:
            return []
        
        # Read file in reverse chunks to get last N lines
        with open(chat_log_file, "rb") as f:
            # Start from end of file
            f.seek(0, os.SEEK_END)
            position = f.tell()
            buffer = b''
            lines = []
            
            # Read backwards in chunks
            while position > 0 and len(lines) < limit * 2:  # Read extra to ensure we get enough valid lines
                # Calculate how much to read
                read_size = min(buffer_size, position)
                position -= read_size
                f.seek(position)
                
                # Read chunk
                chunk = f.read(read_size)
                buffer = chunk + buffer
                
                # Split into lines
                while b'\n' in buffer:
                    line, buffer = buffer.rsplit(b'\n', 1)
                    if line.strip():
                        try:
                            decoded = line.decode('utf-8', errors='ignore').strip()
                            if decoded:
                                lines.append(decoded)
                        except Exception:
                            continue
            
            # Add remaining buffer as last line
            if buffer.strip():
                try:
                    decoded = buffer.decode('utf-8', errors='ignore').strip()
                    if decoded:
                        lines.append(decoded)
                except Exception:
                    pass
        
        # Reverse lines to get chronological order (oldest to newest)
        lines.reverse()
        
        # Take last N lines and parse JSON
        lines = lines[-limit:]
        for line in lines:
            if not line.strip():
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

