"""Main FastAPI application - Production-ready version with security and performance enhancements."""
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.exceptions.handlers import setup_exception_handlers
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    APIVersionMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import routers
from app.api import (
    auth, chat, settings as settings_router, logs, tools, monitor, 
    billing, approvals, permissions
)
from app.api.services_config import router as services_config_router
from app.api.roles_config import router as roles_config_router

# Import WebSocket and other endpoints
from app.api.websocket import router as websocket_router
from app.api.security import router as security_router
from app.api.filesystem import router as filesystem_router
from app.api.prometheus import router as prometheus_router
from app.api.agent import router as agent_router
from app.api.cicd import router as cicd_router
from app.api.debugger import router as debugger_router
from app.api.monitoring import router as monitoring_router
from app.api.audit import router as audit_router
from app.api.backup import router as backup_router
from app.api.incidents import router as incidents_router
from app.api.workflows import router as workflows_router
from app.api.visualization import router as visualization_router
from app.api.dashboard import router as dashboard_router
from app.api.abac import router as abac_router
from app.api.ai_threat_detection import router as threat_detection_router
from app.api.intelligent_log_timeline import router as timeline_router
from app.api.config_drift import router as config_drift_router
from app.api.cost_analyzer import router as cost_analyzer_router
from app.api.user_behavior import router as user_behavior_router
from app.api.global_search import router as global_search_router
from app.api.snapshot_rollback import router as snapshot_rollback_router
from app.api.incident_command_center import router as incident_command_center_router
# Optional imports - make them lazy to avoid startup errors
try:
    from app.api.unified_secrets import router as unified_secrets_router
except ImportError:
    unified_secrets_router = None
try:
    from app.api.service_dependency import router as service_dependency_router
except ImportError:
    service_dependency_router = None
try:
    from app.api.kernel_metrics import router as kernel_metrics_router
except ImportError:
    kernel_metrics_router = None
try:
    from app.api.auto_hardening import router as auto_hardening_router
except ImportError:
    auto_hardening_router = None
try:
    from app.api.shadow_deployment import router as shadow_deployment_router
except ImportError:
    shadow_deployment_router = None
try:
    from app.api.ai_performance_tuner import router as performance_tuner_router
except ImportError:
    performance_tuner_router = None
try:
    from app.api.behavior_alerts import router as behavior_alerts_router
except ImportError:
    behavior_alerts_router = None
try:
    from app.api.blueprint_generator import router as blueprint_generator_router
except ImportError:
    blueprint_generator_router = None
try:
    from app.api.ai_code_review import router as code_review_router
except ImportError:
    code_review_router = None
try:
    from app.api.plugin_store import router as plugin_store_router
except ImportError:
    plugin_store_router = None
try:
    from app.api.ai_workflow_builder import router as workflow_builder_router
except ImportError:
    workflow_builder_router = None
try:
    from app.api.distributed_agent_mesh import router as agent_mesh_router
except ImportError:
    agent_mesh_router = None
try:
    from app.api.digital_twin import router as digital_twin_router
except ImportError:
    digital_twin_router = None
try:
    from app.api.knowledge import router as knowledge_router
except ImportError:
    knowledge_router = None

# Import new CRM + AAA routers - make them optional
try:
    from app.api.identity_api import router as identity_router
except ImportError:
    identity_router = None
try:
    from app.api.access_api import router as access_router
except ImportError:
    access_router = None
try:
    from app.api.policy_api import router as policy_router
except ImportError:
    policy_router = None
try:
    from app.api.subscription_api import router as subscription_router
except ImportError:
    subscription_router = None
try:
    from app.api.audit_api import router as audit_api_router
except ImportError:
    audit_api_router = None
try:
    from app.api.crm_api import router as crm_router
    print(f"[MAIN] ✅ CRM router imported successfully: {crm_router}")
    print(f"[MAIN] ✅ CRM router prefix: {crm_router.prefix}")
    print(f"[MAIN] ✅ CRM router has {len(crm_router.routes)} routes")
except ImportError as e:
    print(f"[MAIN] ❌ ImportError importing CRM router: {e}")
    import traceback
    traceback.print_exc()
    crm_router = None
except Exception as e:
    print(f"[MAIN] ❌ Exception importing CRM router: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    crm_router = None
try:
    from app.api.capabilities import router as capabilities_router
except ImportError:
    capabilities_router = None

app_settings = get_settings()

# Create FastAPI app with production-ready settings
app = FastAPI(
    title="SHIFTWAVE AI Platform - Backend API",
    version="1.0.0",
    description="Production-ready AI Agent Backend API with comprehensive security and monitoring",
    docs_url="/docs" if app_settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if app_settings.DEBUG else None,  # Disable redoc in production
    openapi_url="/openapi.json" if app_settings.DEBUG else None,  # Disable OpenAPI in production
)

# Add production middleware (order matters - last added is first executed)
# 1. Security Headers (innermost - applied last)
app.add_middleware(SecurityHeadersMiddleware)

# 2. API Versioning
app.add_middleware(APIVersionMiddleware, api_version="v1")

# 3. Request Logging
if app_settings.DEBUG or app_settings.LOG_LEVEL == "DEBUG":
    app.add_middleware(RequestLoggingMiddleware)

# 4. Rate Limiting (before CORS to catch early)
# Configure rate limits based on environment
if app_settings.DEBUG:
    # More lenient limits in development
    rate_limit_per_minute = 120
    rate_limit_per_hour = 2000
    burst_limit = 20
else:
    # Stricter limits in production
    rate_limit_per_minute = 60
    rate_limit_per_hour = 1000
    burst_limit = 10

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=rate_limit_per_minute,
    requests_per_hour=rate_limit_per_hour,
    burst_limit=burst_limit
)

# 5. CORS - Allow all origins for development, specific origins for production
cors_origins = ["*"] if (isinstance(app_settings.CORS_ORIGINS, list) and "*" in app_settings.CORS_ORIGINS) else app_settings.CORS_ORIGINS

# When using "*" for origins, we cannot use allow_credentials=True
# So we'll use allow_origins=["*"] without credentials, or specific origins with credentials
if cors_origins == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Cannot use True with "*"
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Limit-Minute", "X-RateLimit-Remaining-Minute", 
                       "X-RateLimit-Limit-Hour", "X-RateLimit-Remaining-Hour",
                       "X-API-Version", "X-Process-Time"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Limit-Minute", "X-RateLimit-Remaining-Minute",
                       "X-RateLimit-Limit-Hour", "X-RateLimit-Remaining-Hour",
                       "X-API-Version", "X-Process-Time"],
    )

# Setup exception handlers
setup_exception_handlers(app)

# Enhanced global exception handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Enhanced HTTP exception handler with logging."""
    logger.warning(
        f"HTTP {exc.status_code} error: {exc.detail} "
        f"Path: {request.url.path} "
        f"Method: {request.method}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Enhanced validation exception handler."""
    logger.warning(
        f"Validation error: {exc.errors()} "
        f"Path: {request.url.path} "
        f"Method: {request.method}"
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "status_code": 422,
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    logger.error(
        f"Unexpected error: {str(exc)} "
        f"Path: {request.url.path} "
        f"Method: {request.method}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if not app_settings.DEBUG else str(exc),
            "status_code": 500,
            "path": request.url.path
        }
    )

# Initialize cache connection on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    from app.core.cache import get_redis_client
    logger.info("Starting up SHIFTWAVE AI Platform Backend...")
    
    # Initialize Redis cache
    redis_client = get_redis_client()
    if redis_client:
        logger.info("✅ Redis cache initialized")
    else:
        logger.warning("⚠️  Redis cache not available - caching disabled")
    
    # Test database connection
    try:
        from app.core.database import get_db
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    from app.core.cache import get_redis_client
    logger.info("Shutting down...")
    
    # Close Redis connection
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.close()
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis: {e}")

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(settings_router.router)  # Using settings_router (no duplicate import)
app.include_router(logs.router)
app.include_router(tools.router)
app.include_router(monitor.router)
app.include_router(billing.router)
app.include_router(approvals.router)
app.include_router(permissions.router)
app.include_router(services_config_router)
app.include_router(roles_config_router)
app.include_router(websocket_router)
app.include_router(security_router)
app.include_router(filesystem_router)
app.include_router(prometheus_router)
app.include_router(agent_router)
app.include_router(cicd_router)
app.include_router(debugger_router)
app.include_router(monitoring_router)
app.include_router(audit_router)
app.include_router(backup_router)
app.include_router(incidents_router)
app.include_router(workflows_router)
app.include_router(visualization_router)
app.include_router(dashboard_router)
app.include_router(abac_router)
app.include_router(threat_detection_router)
app.include_router(timeline_router)
app.include_router(config_drift_router)
app.include_router(cost_analyzer_router)
app.include_router(user_behavior_router)
app.include_router(global_search_router)
app.include_router(snapshot_rollback_router)
app.include_router(incident_command_center_router)
# Include optional routers only if available
if unified_secrets_router:
    app.include_router(unified_secrets_router)
if service_dependency_router:
    app.include_router(service_dependency_router)
if kernel_metrics_router:
    app.include_router(kernel_metrics_router)
if auto_hardening_router:
    app.include_router(auto_hardening_router)
if shadow_deployment_router:
    app.include_router(shadow_deployment_router)
if performance_tuner_router:
    app.include_router(performance_tuner_router)
if behavior_alerts_router:
    app.include_router(behavior_alerts_router)
if blueprint_generator_router:
    app.include_router(blueprint_generator_router)
if code_review_router:
    app.include_router(code_review_router)
if plugin_store_router:
    app.include_router(plugin_store_router)
if workflow_builder_router:
    app.include_router(workflow_builder_router)
if agent_mesh_router:
    app.include_router(agent_mesh_router)
if digital_twin_router:
    app.include_router(digital_twin_router)
if knowledge_router:
    app.include_router(knowledge_router)

# Include new CRM + AAA routers - only if available
if identity_router:
    app.include_router(identity_router)
if access_router:
    app.include_router(access_router)
if policy_router:
    app.include_router(policy_router)
if subscription_router:
    app.include_router(subscription_router)
if audit_api_router:
    app.include_router(audit_api_router)
if crm_router:
    app.include_router(crm_router)
    print(f"[MAIN] ✅ CRM router included in app with prefix: {crm_router.prefix}")
    print(f"[MAIN] ✅ Total routes in app after CRM: {len([r for r in app.routes if hasattr(r, 'path')])}")
else:
    print(f"[MAIN] ❌ CRITICAL: CRM router is None, not including!")
    print(f"[MAIN] ❌ This means CRM endpoints will NOT be available!")
if capabilities_router:
    app.include_router(capabilities_router)


@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with detailed status."""
    import psutil
    import os
    
    try:
        # Check database connectivity (if available)
        db_status = "unknown"
        try:
            from app.core.database import get_db
            db = next(get_db())
            db.execute("SELECT 1")
            db_status = "connected"
        except Exception:
            db_status = "disconnected"
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "service": "ai-backend",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "ai-backend",
                "error": str(e) if app_settings.DEBUG else "Service unavailable"
            }
        )


@app.get("/api/")
@app.get("/api/v1/")
async def api_info():
    """Root API endpoint - provides API information and available endpoints."""
    try:
        # Get all registered routes
        api_routes = []
        route_prefixes = set()
        endpoint_map = {}
        
        for route in app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api/'):
                # Extract route information
                methods = []
                if hasattr(route, 'methods'):
                    methods = [m for m in route.methods if m != 'HEAD' and m != 'OPTIONS']
                elif hasattr(route, 'endpoint'):
                    # Try to get methods from endpoint
                    methods = ['GET']  # Default
                
                # Extract module prefix
                path_parts = route.path.split('/')
                if len(path_parts) >= 3 and path_parts[1] == 'api':
                    module_name = path_parts[2]
                    # Skip internal/system endpoints from main listing
                    if module_name not in ['auth', 'services', 'capabilities', 'health']:
                        route_prefixes.add(module_name)
                    
                    # Build endpoint map for quick reference (limit to avoid huge response)
                    if len(endpoint_map) < 50:  # Limit endpoint map size
                        if module_name not in endpoint_map:
                            endpoint_map[module_name] = []
                        # Only add first few routes per module to keep response manageable
                        if len(endpoint_map[module_name]) < 5:
                            endpoint_map[module_name].append({
                                "path": route.path,
                                "methods": methods if methods else ["GET"]
                            })
                
                api_routes.append({
                    "path": route.path,
                    "methods": methods if methods else ["GET"]
                })
        
        # Count unique API modules
        unique_modules = len(route_prefixes)
        
        # Build comprehensive endpoint information
        return {
            "api": "SHIFTWAVE AI Platform - Backend API",
            "version": "1.0.0",
            "api_version": "v1",
            "status": "operational",
            "base_url": "/api",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "openapi": "/openapi.json",
                "services": {
                    "list": "/api/services/list",
                    "categories": "/api/services/categories",
                    "details": "/api/services/{service_id}"
                },
                "auth": {
                    "login": "/api/auth/login",
                    "register": "/api/auth/register",
                    "me": "/api/auth/me",
                    "roles": "/api/auth/roles"
                },
                "dashboard": "/api/dashboard/stats",
                "capabilities": "/api/capabilities"
            },
            "statistics": {
                "modules_count": unique_modules,
                "total_routes": len(api_routes),
                "available_modules": sorted(list(route_prefixes))
            },
            "modules": endpoint_map
        }
    except Exception as e:
        import traceback
        return {
            "api": "SHIFTWAVE AI Platform - Backend API",
            "version": "1.0.0",
            "api_version": "v1",
            "status": "operational",
            "error": f"Error gathering API info: {str(e)}",
            "traceback": traceback.format_exc() if app_settings.DEBUG else None
        }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    docs_url = "/docs" if app_settings.DEBUG else None
    return {
        "message": "SHIFTWAVE AI Platform - Backend API",
        "version": "1.0.0",
        "status": "operational",
        "docs": docs_url,
        "health": "/health",
        "api": "/api/",
        "api_version": "v1"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Production-ready uvicorn configuration
    uvicorn.run(
        "app.main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.DEBUG,
        access_log=app_settings.DEBUG,  # Disable access log in production
        log_level=app_settings.LOG_LEVEL.lower(),
        timeout_keep_alive=600,
        timeout_graceful_shutdown=30,
        limit_concurrency=1000,  # Max concurrent connections
        limit_max_requests=10000,  # Max requests before restart (for memory leaks)
        backlog=2048,  # Connection backlog
    )

