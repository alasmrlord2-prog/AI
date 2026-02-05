"""Security API endpoints."""
from fastapi import APIRouter, Depends
from app.api.auth import get_current_user
from app.exceptions import AuthorizationError
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/security", tags=["security"])

# Import security tools
try:
    from app.tools.security_scan import (
        scan_repo, scan_infra, scan_logs_auth, scan_network_security,
        scan_system_security, scan_docker_security, scan_network_security_detailed,
        scan_vulnerabilities, scan_file_integrity, scan_malware,
        scan_intrusion_detection, scan_port_scan, scan_penetration_test
    )
    from app.tools.siem_monitor import run as siem_monitor
    from app.tools.advanced_security_tools import (
        threat_intelligence_scan, network_traffic_analysis,
        advanced_vulnerability_scan, web_vulnerability_scan,
        advanced_container_scan, kubernetes_security_scan,
        aws_security_scan, memory_forensics, disk_forensics,
        password_audit, compliance_check, burp_suite_scan,
        metasploit_scan, advanced_packet_analysis
    )
except ImportError:
    # Fallback functions
    def scan_repo(*args, **kwargs):
        return {"error": "Security scan not available"}
    def scan_infra(*args, **kwargs):
        return {"error": "Security scan not available"}
    # ... (similar for all other functions)


# Basic security scans
@router.post("/scan_repo")
async def api_scan_repo(
    path: str = "/app",
    max_files: int = 1000,
    current_user: dict = Depends(get_current_user)
):
    """Scan repository for secrets."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    try:
        check_action_permission("security.repo_scan", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            # Approval required - return JSONResponse
            return JSONResponse(
                status_code=202,
                content={"error": e.detail}
            )
        raise
    
    try:
        return scan_repo(path, max_files)
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_infra")
async def api_scan_infra(
    path: str = "/app",
    current_user: dict = Depends(get_current_user)
):
    """Scan infrastructure files."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    try:
        check_action_permission("security.infra_scan", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        return scan_infra(path)
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_logs")
async def api_scan_logs(
    path: str = "/app/logs",
    lines: int = 1000,
    current_user: dict = Depends(get_current_user)
):
    """Scan logs for authentication issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    try:
        check_action_permission("logs.read", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        return scan_logs_auth(path, lines)
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_network")
async def api_scan_network(current_user: dict = Depends(get_current_user)):
    """Scan network for security issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    try:
        check_action_permission("security.network_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        return scan_network_security()
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_system")
async def api_scan_system(current_user: dict = Depends(get_current_user)):
    """Scan system for security issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    try:
        check_action_permission("security.scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        return scan_system_security()
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_docker")
async def api_scan_docker(current_user: dict = Depends(get_current_user)):
    """Scan Docker configuration for security issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    try:
        check_action_permission("security.docker_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        return scan_docker_security()
    except Exception as e:
        return {"error": str(e)}


@router.get("/siem")
async def api_siem_monitor(current_user: dict = Depends(get_current_user)):
    """SIEM monitoring dashboard data."""
    check_action_permission("siem.monitor", current_user)
    try:
        return siem_monitor()
    except Exception as e:
        return {"error": str(e)}


# Advanced security tools
@router.post("/advanced/threat_intelligence")
async def api_threat_intelligence(
    ip: str,
    current_user: dict = Depends(get_current_user)
):
    """Threat intelligence scan."""
    check_action_permission("security.scan", current_user, resource=ip)
    try:
        return threat_intelligence_scan(ip)
    except Exception as e:
        return {"error": str(e)}


# Add more advanced security endpoints as needed...
# (Similar pattern for all other advanced security tools)

