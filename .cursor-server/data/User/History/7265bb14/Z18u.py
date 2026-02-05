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

# Create FastAPI app
app = FastAPI(
    title="AI-Agent Backend",
    version="0.1.0",
    description="AI Agent Backend API - Refactored",
)

# Setup CORS - Allow all origins for development
cors_origins = ["*"] if (isinstance(app_settings.CORS_ORIGINS, list) and "*" in app_settings.CORS_ORIGINS) else app_settings.CORS_ORIGINS

# When using "*" for origins, we cannot use allow_credentials=True
# So we'll use allow_origins=["*"] without credentials, or specific origins with credentials
if cors_origins == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Cannot use True with "*"
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
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

