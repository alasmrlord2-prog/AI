"""Main FastAPI application - Refactored version."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.exceptions.handlers import setup_exception_handlers

# Import routers
from app.api import auth, chat, settings, logs, tools, monitor, billing, approvals, permissions

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

app_settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI-Agent Backend",
    version="0.1.0",
    description="AI Agent Backend API - Refactored",
)

# Setup CORS - Allow all origins for development
cors_origins = ["*"] if (isinstance(app_settings.CORS_ORIGINS, list) and "*" in app_settings.CORS_ORIGINS) else app_settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Import settings router
from app.api import settings as settings_router

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(settings_router.router)
app.include_router(logs.router)
app.include_router(tools.router)
app.include_router(monitor.router)
app.include_router(billing.router)
app.include_router(approvals.router)
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


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "ai-backend"}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "AI Agent Backend API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_new:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.DEBUG
    )

