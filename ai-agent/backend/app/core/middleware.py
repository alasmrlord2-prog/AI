"""Production-ready middleware for security, rate limiting, and monitoring."""
import time
import logging
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from collections import defaultdict
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# Rate limiting storage (in-memory, use Redis in production)
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        current_time = time.time()
        
        # Clean old entries (older than 1 hour)
        if client_ip in _rate_limit_store:
            _rate_limit_store[client_ip] = [
                timestamp for timestamp in _rate_limit_store[client_ip]
                if current_time - timestamp < 3600
            ]
        
        # Check burst limit (requests in last 10 seconds)
        recent_requests = [
            timestamp for timestamp in _rate_limit_store.get(client_ip, [])
            if current_time - timestamp < 10
        ]
        
        if len(recent_requests) >= self.burst_limit:
            logger.warning(f"Rate limit exceeded (burst) for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please slow down.",
                    "retry_after": 10
                },
                headers={"Retry-After": "10"}
            )
        
        # Check per-minute limit
        minute_requests = [
            timestamp for timestamp in _rate_limit_store.get(client_ip, [])
            if current_time - timestamp < 60
        ]
        
        if len(minute_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded (per minute) for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Check per-hour limit
        hour_requests = [
            timestamp for timestamp in _rate_limit_store.get(client_ip, [])
            if current_time - timestamp < 3600
        ]
        
        if len(hour_requests) >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded (per hour) for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Hourly rate limit exceeded. Please try again later.",
                    "retry_after": 3600
                },
                headers={"Retry-After": "3600"}
            )
        
        # Record this request
        _rate_limit_store[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining_minute = max(0, self.requests_per_minute - len(minute_requests) - 1)
        remaining_hour = max(0, self.requests_per_hour - len(hour_requests) - 1)
        
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(remaining_hour)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring and debugging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s"
            )
            
            # Add performance header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error processing request: {request.method} {request.url.path} "
                f"Error: {str(e)} "
                f"Time: {process_time:.3f}s",
                exc_info=True
            )
            raise


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Add API versioning support."""
    
    def __init__(self, app: ASGIApp, api_version: str = "v1"):
        super().__init__(app)
        self.api_version = api_version
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-API-Version"] = self.api_version
        return response

