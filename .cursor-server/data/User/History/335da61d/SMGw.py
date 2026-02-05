"""
Advanced Caching System - نظام تخزين مؤقت متقدم
"""
import hashlib
import json
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
from threading import Lock
from app.utils.logger import log_debug

# Global cache storage
_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = Lock()
_cache_ttl = timedelta(hours=1)  # Default TTL: 1 hour
_max_cache_size = 1000  # Maximum number of cached items

def _generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """
    Generate a cache key from function name and arguments.
    
    Args:
        func_name: Function name
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Cache key string
    """
    # Create a hash of the arguments
    key_data = {
        "func": func_name,
        "args": args,
        "kwargs": kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.sha256(key_str.encode()).hexdigest()
    return f"{func_name}:{key_hash}"

def _is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """
    Check if a cache entry is still valid.
    
    Args:
        cache_entry: Cache entry dictionary
    
    Returns:
        True if cache is valid, False otherwise
    """
    if "timestamp" not in cache_entry:
        return False
    
    timestamp = datetime.fromisoformat(cache_entry["timestamp"])
    age = datetime.utcnow() - timestamp
    
    return age < cache_ttl

def _cleanup_cache():
    """Remove expired and old cache entries."""
    global _cache
    
    with _cache_lock:
        # Remove expired entries
        expired_keys = [
            key for key, entry in _cache.items()
            if not _is_cache_valid(entry)
        ]
        for key in expired_keys:
            del _cache[key]
        
        # If still too large, remove oldest entries
        if len(_cache) > _max_cache_size:
            # Sort by timestamp and keep newest
            sorted_entries = sorted(
                _cache.items(),
                key=lambda x: x[1].get("timestamp", ""),
                reverse=True
            )
            _cache = dict(sorted_entries[:_max_cache_size])
            log_debug(f"Cache cleaned: {len(_cache)} entries remaining")

def cached(ttl: Optional[timedelta] = None, max_size: int = 1000):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live for cache entries (default: 1 hour)
        max_size: Maximum cache size (default: 1000)
    
    Usage:
        @cached(ttl=timedelta(minutes=30))
        def expensive_function(arg1, arg2):
            ...
    """
    global _cache_ttl, _max_cache_size
    
    if ttl:
        _cache_ttl = ttl
    if max_size:
        _max_cache_size = max_size
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func.__name__, *args, **kwargs)
            
            # Check cache
            with _cache_lock:
                if cache_key in _cache:
                    entry = _cache[cache_key]
                    if _is_cache_valid(entry):
                        log_debug(f"Cache hit: {func.__name__}")
                        return entry["result"]
                    else:
                        # Remove expired entry
                        del _cache[cache_key]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            with _cache_lock:
                _cache[cache_key] = {
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                log_debug(f"Cache miss: {func.__name__} - cached")
            
            # Cleanup if needed
            if len(_cache) > _max_cache_size:
                _cleanup_cache()
            
            return result
        
        return wrapper
    return decorator

def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries.
    
    Args:
        pattern: Optional pattern to match cache keys (e.g., "scan_repo:*")
    """
    global _cache
    
    with _cache_lock:
        if pattern:
            # Clear matching entries
            prefix = pattern.split(":")[0] if ":" in pattern else pattern
            keys_to_remove = [
                key for key in _cache.keys()
                if key.startswith(prefix)
            ]
            for key in keys_to_remove:
                del _cache[key]
            log_debug(f"Cleared {len(keys_to_remove)} cache entries matching '{pattern}'")
        else:
            # Clear all
            count = len(_cache)
            _cache.clear()
            log_debug(f"Cleared all {count} cache entries")

def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    with _cache_lock:
        valid_entries = sum(1 for entry in _cache.values() if _is_cache_valid(entry))
        expired_entries = len(_cache) - valid_entries
        
        return {
            "total_entries": len(_cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "max_size": _max_cache_size,
            "ttl_hours": _cache_ttl.total_seconds() / 3600
        }

