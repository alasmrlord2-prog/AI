"""Brute Force Protection - Rate limiting and account lockout."""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.core.cache import get_cache, set_cache, delete_cache, cache_key

logger = logging.getLogger(__name__)

# Configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes
ATTEMPT_WINDOW = 900  # 15 minutes
RATE_LIMIT_PER_MINUTE = 5


class BruteForceProtection:
    """Protect against brute force attacks."""
    
    @staticmethod
    def check_lockout(identifier: str) -> Dict[str, Any]:
        """Check if identifier is locked out."""
        lockout_key = cache_key("lockout", identifier=identifier)
        lockout_data = get_cache(lockout_key)
        
        if lockout_data:
            lockout_until = datetime.fromisoformat(lockout_data["until"])
            if datetime.utcnow() < lockout_until:
                remaining = (lockout_until - datetime.utcnow()).total_seconds()
                return {
                    "locked": True,
                    "until": lockout_until.isoformat(),
                    "remaining_seconds": int(remaining)
                }
            else:
                # Lockout expired, clear it
                delete_cache(lockout_key)
        
        return {"locked": False}
    
    @staticmethod
    def record_failed_attempt(identifier: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Record a failed login attempt."""
        attempt_key = cache_key("login_attempts", identifier=identifier)
        attempts_data = get_cache(attempt_key) or {
            "count": 0,
            "first_attempt": datetime.utcnow().isoformat(),
            "last_attempt": datetime.utcnow().isoformat()
        }
        
        attempts_data["count"] += 1
        attempts_data["last_attempt"] = datetime.utcnow().isoformat()
        
        # Check if lockout threshold reached
        if attempts_data["count"] >= MAX_LOGIN_ATTEMPTS:
            lockout_until = datetime.utcnow() + timedelta(seconds=LOCKOUT_DURATION)
            lockout_key = cache_key("lockout", identifier=identifier)
            set_cache(
                lockout_key,
                {
                    "until": lockout_until.isoformat(),
                    "attempts": attempts_data["count"]
                },
                ttl=LOCKOUT_DURATION
            )
            
            logger.warning(
                f"Account locked: {identifier}",
                extra={
                    "identifier": identifier,
                    "ip_address": ip_address,
                    "attempts": attempts_data["count"]
                }
            )
            
            return {
                "locked": True,
                "until": lockout_until.isoformat(),
                "remaining_attempts": 0
            }
        
        # Store attempts
        set_cache(attempt_key, attempts_data, ttl=ATTEMPT_WINDOW)
        
        return {
            "locked": False,
            "remaining_attempts": MAX_LOGIN_ATTEMPTS - attempts_data["count"]
        }
    
    @staticmethod
    def clear_attempts(identifier: str):
        """Clear failed attempts after successful login."""
        attempt_key = cache_key("login_attempts", identifier=identifier)
        delete_cache(attempt_key)
    
    @staticmethod
    def check_rate_limit(ip_address: str) -> bool:
        """Check rate limit for IP address."""
        rate_key = cache_key("rate_limit", ip=ip_address)
        rate_data = get_cache(rate_key) or {"count": 0, "window_start": time.time()}
        
        current_time = time.time()
        window_start = rate_data["window_start"]
        
        # Reset window if expired
        if current_time - window_start > 60:
            rate_data = {"count": 0, "window_start": current_time}
        
        rate_data["count"] += 1
        
        if rate_data["count"] > RATE_LIMIT_PER_MINUTE:
            set_cache(rate_key, rate_data, ttl=60)
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return False
        
        set_cache(rate_key, rate_data, ttl=60)
        return True

