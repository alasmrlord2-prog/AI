"""Redis cache utility for performance optimization."""
import json
import logging
from typing import Optional, Any, Union, Callable
from functools import wraps
from datetime import timedelta
import redis
from redis.exceptions import ConnectionError, TimeoutError, RedisError
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Redis client instance
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """Get or create Redis client instance."""
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    # Check if Redis is enabled
    redis_enabled = getattr(settings, 'REDIS_ENABLED', False)
    if not redis_enabled:
        logger.debug("Redis caching is disabled")
        return None
    
    # Get Redis URL from settings
    redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test connection
        _redis_client.ping()
        logger.info(f"Redis connection established: {redis_url}")
        return _redis_client
    except (ConnectionError, TimeoutError, RedisError) as e:
        logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
        _redis_client = None
        return None
    except Exception as e:
        logger.error(f"Unexpected Redis error: {e}")
        _redis_client = None
        return None


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from prefix and arguments."""
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif arg is not None:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}:{value}")
        elif value is not None:
            key_parts.append(f"{key}:{hash(str(value))}")
    
    return ":".join(key_parts)


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    client = get_redis_client()
    if client is None:
        return None
    
    try:
        value = client.get(key)
        if value is None:
            return None
        
        # Try to deserialize JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return as string if not JSON
            return value
    except (ConnectionError, TimeoutError, RedisError) as e:
        logger.warning(f"Redis get error for key {key}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected Redis get error: {e}")
        return None


def set_cache(
    key: str,
    value: Any,
    ttl: Optional[Union[int, timedelta]] = None,
    nx: bool = False
) -> bool:
    """Set value in cache with optional TTL."""
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        # Serialize value
        if isinstance(value, (str, int, float, bool)):
            serialized_value = json.dumps(value)
        else:
            serialized_value = json.dumps(value, default=str)
        
        # Convert TTL to seconds if timedelta
        if isinstance(ttl, timedelta):
            ttl_seconds = int(ttl.total_seconds())
        elif isinstance(ttl, int):
            ttl_seconds = ttl
        else:
            ttl_seconds = None
        
        # Set with options
        if nx:
            result = client.set(key, serialized_value, ex=ttl_seconds, nx=True)
        else:
            result = client.set(key, serialized_value, ex=ttl_seconds)
        
        return bool(result)
    except (ConnectionError, TimeoutError, RedisError) as e:
        logger.warning(f"Redis set error for key {key}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected Redis set error: {e}")
        return False


def delete_cache(key: str) -> bool:
    """Delete key from cache."""
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        result = client.delete(key)
        return bool(result)
    except (ConnectionError, TimeoutError, RedisError) as e:
        logger.warning(f"Redis delete error for key {key}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected Redis delete error: {e}")
        return False


def clear_cache_pattern(pattern: str) -> int:
    """Clear all keys matching pattern."""
    client = get_redis_client()
    if client is None:
        return 0
    
    try:
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except (ConnectionError, TimeoutError, RedisError) as e:
        logger.warning(f"Redis clear pattern error for {pattern}: {e}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected Redis clear pattern error: {e}")
        return 0


def cached(
    ttl: Optional[Union[int, timedelta]] = 300,
    key_prefix: Optional[str] = None,
    key_func: Optional[Callable] = None
):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}:{func.__name__}"
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = get_cache(cache_key_str)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key_str}")
                return cached_value
            
            # Execute function
            logger.debug(f"Cache miss: {cache_key_str}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            set_cache(cache_key_str, result, ttl=ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}:{func.__name__}"
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = get_cache(cache_key_str)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key_str}")
                return cached_value
            
            # Execute function
            logger.debug(f"Cache miss: {cache_key_str}")
            result = func(*args, **kwargs)
            
            # Store in cache
            set_cache(cache_key_str, result, ttl=ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern."""
    return clear_cache_pattern(pattern)

