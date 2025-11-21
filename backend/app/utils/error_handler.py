"""
Unified Error Handling - معالجة أخطاء موحدة
"""
from typing import Dict, Any, Optional, Callable
from functools import wraps
from fastapi import HTTPException
from app.utils.logger import log_error, log_warning

class SecurityScanError(Exception):
    """Base exception for security scan errors"""
    pass

class PathResolutionError(SecurityScanError):
    """Error in path resolution"""
    pass

class PermissionDeniedError(SecurityScanError):
    """Permission denied error"""
    pass

class ScanExecutionError(SecurityScanError):
    """Error during scan execution"""
    pass

def handle_scan_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in security scan functions.
    
    Usage:
        @handle_scan_errors
        def scan_repo(path: str) -> Dict[str, Any]:
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionDeniedError as e:
            log_error(e, context=f"{func.__name__}")
            return {"error": f"Permission denied: {str(e)}", "error_type": "permission_denied"}
        except PathResolutionError as e:
            log_error(e, context=f"{func.__name__}")
            return {"error": f"Path resolution failed: {str(e)}", "error_type": "path_error"}
        except ScanExecutionError as e:
            log_error(e, context=f"{func.__name__}")
            return {"error": f"Scan execution failed: {str(e)}", "error_type": "execution_error"}
        except Exception as e:
            log_error(e, context=f"{func.__name__}")
            return {"error": f"Unexpected error: {str(e)}", "error_type": "unexpected_error"}
    
    return wrapper

def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in API endpoints.
    
    Usage:
        @router.post("/endpoint")
        @handle_api_errors
        async def endpoint(...):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except PermissionDeniedError as e:
            log_error(e, context=f"{func.__name__}")
            raise HTTPException(status_code=403, detail=str(e))
        except PathResolutionError as e:
            log_error(e, context=f"{func.__name__}")
            raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}")
        except ScanExecutionError as e:
            log_error(e, context=f"{func.__name__}")
            raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
        except Exception as e:
            log_error(e, context=f"{func.__name__}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    return wrapper

def create_error_response(error: Exception, error_type: str = "unknown") -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error: Exception instance
        error_type: Type of error
    
    Returns:
        Standardized error dictionary
    """
    return {
        "error": str(error),
        "error_type": error_type,
        "timestamp": datetime.utcnow().isoformat()
    }

