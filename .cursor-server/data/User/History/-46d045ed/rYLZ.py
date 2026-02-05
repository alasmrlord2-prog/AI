import os
import json
from typing import Dict, List, Any

# Security: Root directory restriction
ALLOWED_ROOT = os.getenv("AGENT_ROOT", "/app")
MAX_DEPTH = 10

def _normalize_path(path: str) -> str:
    """Normalize and validate path"""
    if not path:
        return ALLOWED_ROOT
    
    # Remove leading slashes and normalize
    path = path.lstrip("/")
    if not path:
        return ALLOWED_ROOT
    
    # Build full path
    full_path = os.path.join(ALLOWED_ROOT, path)
    
    # Resolve to absolute and check it's within allowed root
    full_path = os.path.abspath(full_path)
    root_abs = os.path.abspath(ALLOWED_ROOT)
    
    if not full_path.startswith(root_abs):
        raise PermissionError(f"Path outside allowed root: {root_abs}")
    
    return full_path

def list_dir(path: str = "") -> Dict[str, Any]:
    """
    List directory contents
    Returns: { "path": "...", "items": [...] }
    """
    try:
        full_path = _normalize_path(path)
        
        if not os.path.exists(full_path):
            return {"error": f"Path does not exist: {path}"}
        
        if not os.path.isdir(full_path):
            return {"error": f"Not a directory: {path}"}
        
        items = []
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            rel_path = os.path.relpath(item_path, ALLOWED_ROOT)
            
            stat = os.stat(item_path)
            items.append({
                "name": item,
                "path": rel_path,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": stat.st_size if os.path.isfile(item_path) else 0,
                "modified": stat.st_mtime,
            })
        
        return {
            "path": path or "/",
            "items": items,
            "count": len(items),
        }
    except PermissionError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error listing directory: {e}"}

def read_file(path: str, limit: int = 10000) -> Dict[str, Any]:
    """
    Read file content (with size limit)
    """
    try:
        full_path = _normalize_path(path)
        
        if not os.path.exists(full_path):
            return {"error": f"File does not exist: {path}"}
        
        if not os.path.isfile(full_path):
            return {"error": f"Not a file: {path}"}
        
        stat = os.stat(full_path)
        if stat.st_size > limit:
            return {
                "error": f"File too large ({stat.st_size} bytes). Max: {limit}",
                "size": stat.st_size,
            }
        
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        return {
            "path": path,
            "content": content,
            "size": stat.st_size,
            "lines": len(content.splitlines()),
        }
    except PermissionError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error reading file: {e}"}

def tail_file(path: str, lines: int = 50) -> Dict[str, Any]:
    """
    Read last N lines of a file
    """
    try:
        full_path = _normalize_path(path)
        
        if not os.path.exists(full_path):
            return {"error": f"File does not exist: {path}"}
        
        if not os.path.isfile(full_path):
            return {"error": f"Not a file: {path}"}
        
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
        
        tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "path": path,
            "content": "".join(tail_lines),
            "lines": len(tail_lines),
            "total_lines": len(all_lines),
        }
    except PermissionError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error tailing file: {e}"}

def run(path: str = "", action: str = "list", **kwargs) -> Dict[str, Any]:
    """
    Main entry point for file explorer tool
    """
    if action == "list":
        return list_dir(path)
    elif action == "read":
        limit = kwargs.get("limit", 10000)
        return read_file(path, limit=limit)
    elif action == "tail":
        lines = kwargs.get("lines", 50)
        return tail_file(path, lines=lines)
    else:
        return {"error": f"Unknown action: {action}"}

