"""FastAPI Metrics Middleware - Real observability metrics."""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Prometheus metrics (if available)
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
    
    # HTTP metrics
    http_requests_total = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status_code', 'tenant_id']
    )
    
    http_request_duration_seconds = Histogram(
        'http_request_duration_seconds',
        'HTTP request duration in seconds',
        ['method', 'endpoint', 'status_code'],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    )
    
    http_request_size_bytes = Histogram(
        'http_request_size_bytes',
        'HTTP request size in bytes',
        ['method', 'endpoint'],
        buckets=[100, 500, 1000, 5000, 10000, 50000]
    )
    
    active_requests = Gauge(
        'active_requests',
        'Currently active requests',
        ['method', 'endpoint']
    )
    
except ImportError:
    PROMETHEUS_AVAILABLE = False
    http_requests_total = None
    http_request_duration_seconds = None
    http_request_size_bytes = None
    active_requests = None


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect real metrics from FastAPI."""
    
    async def dispatch(self, request: Request, call_next):
        if not PROMETHEUS_AVAILABLE:
            return await call_next(request)
        
        # Get endpoint (simplified path)
        endpoint = self._get_endpoint(request)
        method = request.method
        
        # Track active requests
        active_requests.labels(method=method, endpoint=endpoint).inc()
        
        # Measure request size
        content_length = request.headers.get("content-length", "0")
        try:
            request_size = int(content_length)
        except ValueError:
            request_size = 0
        
        start_time = time.time()
        status_code = 500
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Measure response time
            duration = time.time() - start_time
            
            # Get tenant_id from request state if available
            tenant_id = getattr(request.state, "tenant_id", "unknown")
            tenant_id_str = str(tenant_id) if tenant_id != "unknown" else "unknown"
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                tenant_id=tenant_id_str
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(duration)
            
            if request_size > 0:
                http_request_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(request_size)
            
            # Add metrics headers
            response.headers["X-Request-Duration"] = f"{duration:.4f}"
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            tenant_id_str = "unknown"
            
            # Record error metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500,
                tenant_id=tenant_id_str
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).observe(duration)
            
            raise
        finally:
            # Decrement active requests
            active_requests.labels(method=method, endpoint=endpoint).dec()
    
    def _get_endpoint(self, request: Request) -> str:
        """Extract endpoint name from request path."""
        path = request.url.path
        
        # Remove common prefixes
        if path.startswith("/api/"):
            parts = path.split("/")
            if len(parts) >= 3:
                return f"/api/{parts[2]}"
        
        # Limit length
        if len(path) > 50:
            return path[:50]
        
        return path or "/"

