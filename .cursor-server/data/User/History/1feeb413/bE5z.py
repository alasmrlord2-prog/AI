"""Main FastAPI application - Refactored version."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.config import get_settings
from app.exceptions.handlers import setup_exception_handlers

# Import routers
from app.api import auth, chat, settings, logs, tools, monitor, billing, approvals

# Import WebSocket and other endpoints
from app.api.websocket import router as websocket_router
from app.api.security import router as security_router
from app.api.filesystem import router as filesystem_router
from app.api.prometheus import router as prometheus_router

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI-Agent Backend",
    version="0.1.0",
    description="AI Agent Backend API - Refactored",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(logs.router)
app.include_router(tools.router)
app.include_router(monitor.router)
app.include_router(billing.router)
app.include_router(approvals.router)
app.include_router(websocket_router)
app.include_router(security_router)
app.include_router(filesystem_router)
app.include_router(prometheus_router)


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
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

