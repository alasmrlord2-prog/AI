"""Main FastAPI application - Refactored version."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.exceptions.handlers import setup_exception_handlers

# Import routers
from app.api import (
    auth, chat, settings as settings_router, logs, tools, monitor, 
    billing, approvals, permissions
)

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
from app.api.abac import router as abac_router
from app.api.ai_threat_detection import router as threat_detection_router
from app.api.intelligent_log_timeline import router as timeline_router
from app.api.config_drift import router as config_drift_router
from app.api.cost_analyzer import router as cost_analyzer_router
from app.api.user_behavior import router as user_behavior_router
from app.api.global_search import router as global_search_router
from app.api.snapshot_rollback import router as snapshot_rollback_router
from app.api.incident_command_center import router as incident_command_center_router
from app.api.unified_secrets import router as unified_secrets_router
from app.api.service_dependency import router as service_dependency_router
from app.api.kernel_metrics import router as kernel_metrics_router
from app.api.auto_hardening import router as auto_hardening_router
from app.api.shadow_deployment import router as shadow_deployment_router
from app.api.ai_performance_tuner import router as performance_tuner_router
from app.api.behavior_alerts import router as behavior_alerts_router
from app.api.blueprint_generator import router as blueprint_generator_router
from app.api.ai_code_review import router as code_review_router
from app.api.plugin_store import router as plugin_store_router
from app.api.ai_workflow_builder import router as workflow_builder_router
from app.api.distributed_agent_mesh import router as agent_mesh_router
from app.api.digital_twin import router as digital_twin_router
from app.api.knowledge import router as knowledge_router

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
app.include_router(abac_router)
app.include_router(threat_detection_router)
app.include_router(timeline_router)
app.include_router(config_drift_router)
app.include_router(cost_analyzer_router)
app.include_router(user_behavior_router)
app.include_router(global_search_router)
app.include_router(snapshot_rollback_router)
app.include_router(incident_command_center_router)
app.include_router(unified_secrets_router)
app.include_router(service_dependency_router)
app.include_router(kernel_metrics_router)
app.include_router(auto_hardening_router)
app.include_router(shadow_deployment_router)
app.include_router(performance_tuner_router)
app.include_router(behavior_alerts_router)
app.include_router(blueprint_generator_router)
app.include_router(code_review_router)
app.include_router(plugin_store_router)
app.include_router(workflow_builder_router)
app.include_router(agent_mesh_router)
app.include_router(digital_twin_router)
app.include_router(knowledge_router)


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
        "app.main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.DEBUG
    )

