"""Security API endpoints."""
from fastapi import APIRouter, Depends, Query
from app.api.auth import get_current_user
from app.exceptions import AuthorizationError
from app.core.permission_helpers import check_action_permission
from app.pending_actions import get_action_by_id

router = APIRouter(prefix="/api/security", tags=["security"])

# Import Security Service Layer
from app.services.security_service import security_service
from app.utils.error_handler import handle_api_errors


# Basic security scans
@router.post("/scan_repo")
async def api_scan_repo(
    path: str = "/app",
    max_files: int = 1000,
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None, description="Optional: Get result from approved action")
):
    """Scan repository for secrets."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    # If action_id is provided, try to get the result from an approved action
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            # Parse execution_result if it's a string
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(
                status_code=202,
                content={
                    "error": {
                        "status": "pending",
                        "action_id": action_id,
                        "message": "Action is still pending approval"
                    }
                }
            )
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
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
        result = security_service.scan_repository(path, max_files)
        _send_to_siem_soc("repo", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_infra")
async def api_scan_infra(
    path: str = "/app",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None, description="Optional: Get result from approved action")
):
    """Scan infrastructure files."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    # If action_id is provided, try to get the result from an approved action
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={
                "error": {
                    "status": "pending",
                    "action_id": action_id,
                    "message": "Action is still pending approval"
                }
            })
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.infra_scan", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_infrastructure(path)
        _send_to_siem_soc("infra", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_logs")
async def api_scan_logs(
    path: str = "/app/logs",
    lines: int = 1000,
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None, description="Optional: Get result from approved action")
):
    """Scan logs for authentication issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    # If action_id is provided, try to get the result from an approved action
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={
                "error": {
                    "status": "pending",
                    "action_id": action_id,
                    "message": "Action is still pending approval"
                }
            })
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("logs.read", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_logs(path, lines)
        _send_to_siem_soc("logs", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_network")
async def api_scan_network(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None, description="Optional: Get result from approved action")
):
    """Scan network for security issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    # If action_id is provided, try to get the result from an approved action
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={
                "error": {
                    "status": "pending",
                    "action_id": action_id,
                    "message": "Action is still pending approval"
                }
            })
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.network_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_network(detailed=False)
        _send_to_siem_soc("network", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_system")
async def api_scan_system(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None, description="Optional: Get result from approved action")
):
    """Scan system for security issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    # If action_id is provided, try to get the result from an approved action
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={
                "error": {
                    "status": "pending",
                    "action_id": action_id,
                    "message": "Action is still pending approval"
                }
            })
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.system_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_system()
        _send_to_siem_soc("system", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_docker")
async def api_scan_docker(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None, description="Optional: Get result from approved action")
):
    """Scan Docker configuration for security issues."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    # If action_id is provided, try to get the result from an approved action
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={
                "error": {
                    "status": "pending",
                    "action_id": action_id,
                    "message": "Action is still pending approval"
                }
            })
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.docker_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_docker()
        _send_to_siem_soc("docker", result, current_user)
        return result
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
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None, description="Optional: Get result from approved action")
):
    """Threat intelligence scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    # If action_id is provided, try to get the result from an approved action
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.threat_intelligence_scan", current_user, resource=ip)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.threat_intelligence(ip)
        _send_to_siem_soc("threat_intelligence", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


# Helper function to send scan results to SIEM/SOC
def _send_to_siem_soc(scan_type: str, result: dict, user: dict):
    """Send scan results to SIEM/SOC for monitoring."""
    try:
        from app.tools.siem_monitor import add_scan_event
        from datetime import datetime
        
        # Extract security events from scan results
        events = []
        severity = "low"
        
        # Determine severity based on scan results
        if result.get("error"):
            severity = "high"
        elif result.get("secrets_found") or result.get("vulnerabilities") or result.get("issues"):
            issues_count = 0
            if result.get("secrets_found"):
                issues_count += sum(f.get("count", 0) for f in result.get("secrets_found", []))
            if result.get("vulnerabilities"):
                issues_count += len(result.get("vulnerabilities", []))
            if result.get("issues"):
                issues_count += len(result.get("issues", []))
            
            if issues_count > 10:
                severity = "critical"
            elif issues_count > 5:
                severity = "high"
            elif issues_count > 0:
                severity = "medium"
        
        # Create SIEM event
        event = {
            "timestamp": datetime.now().isoformat(),
            "source": "security_scan",
            "type": scan_type,
            "severity": severity,
            "message": f"Security scan completed: {scan_type}",
            "scan_result": result,
            "user": user.get("username", "unknown")
        }
        
        add_scan_event(event)
    except Exception as e:
        # Silently fail - don't break scan execution
        pass


# Additional basic security scans
@router.post("/scan_network_detailed")
async def api_scan_network_detailed(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Detailed network security scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.network_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_network(detailed=True)
        _send_to_siem_soc("network_detailed", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_vulnerabilities")
async def api_scan_vulnerabilities(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Scan for system vulnerabilities."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.vulnerability_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_vulnerabilities()
        _send_to_siem_soc("vulnerabilities", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_file_integrity")
async def api_scan_file_integrity(
    path: str = "/",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Scan file integrity."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.file_integrity_scan", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_file_integrity(path)
        _send_to_siem_soc("file_integrity", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_malware")
async def api_scan_malware(
    path: str = "/",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Scan for malware."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.malware_scan", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_malware(path)
        _send_to_siem_soc("malware", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_intrusion_detection")
async def api_scan_intrusion_detection(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Intrusion detection scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.intrusion_detection_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = security_service.scan_intrusion_detection()
        _send_to_siem_soc("intrusion_detection", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_port_scan")
async def api_scan_port_scan(
    target: str = "localhost",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Port scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.port_scan", current_user, resource=target)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = scan_port_scan(target)
        _send_to_siem_soc("port_scan", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/scan_penetration_test")
async def api_scan_penetration_test(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Penetration test scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.penetration_test", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = scan_penetration_test()
        _send_to_siem_soc("penetration_test", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


# Advanced security endpoints
@router.post("/advanced/network_forensics")
async def api_network_forensics(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Network forensics analysis."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.network_forensics", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = network_traffic_analysis()
        _send_to_siem_soc("network_forensics", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/vulnerability")
async def api_advanced_vulnerability(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Advanced vulnerability scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.advanced_vulnerability_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = advanced_vulnerability_scan()
        _send_to_siem_soc("advanced_vulnerability", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/web_scan")
async def api_web_scan(
    url: str = "http://localhost",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Web application vulnerability scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.web_scan", current_user, resource=url)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = web_vulnerability_scan(url)
        _send_to_siem_soc("web_scan", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/container")
async def api_advanced_container(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Advanced container security scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.advanced_container_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = advanced_container_scan()
        _send_to_siem_soc("advanced_container", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/kubernetes")
async def api_kubernetes(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Kubernetes security scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.kubernetes_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = kubernetes_security_scan()
        _send_to_siem_soc("kubernetes", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/aws")
async def api_aws(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """AWS security scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.aws_scan", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = aws_security_scan()
        _send_to_siem_soc("aws", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/memory_forensics")
async def api_memory_forensics(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Memory forensics scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.memory_forensics", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = memory_forensics()
        _send_to_siem_soc("memory_forensics", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/disk_forensics")
async def api_disk_forensics(
    path: str = "/",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Disk forensics scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.disk_forensics", current_user, resource=path)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = disk_forensics(path)
        _send_to_siem_soc("disk_forensics", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/password_audit")
async def api_password_audit(
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Password audit scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.password_audit", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = password_audit()
        _send_to_siem_soc("password_audit", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/compliance")
async def api_compliance(
    standard: str = "CIS",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Compliance check scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.compliance_check", current_user)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = compliance_check(standard)
        _send_to_siem_soc("compliance", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/burp_suite")
async def api_burp_suite(
    url: str = "http://localhost",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Burp Suite web scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.burp_suite_scan", current_user, resource=url)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = burp_suite_scan(url)
        _send_to_siem_soc("burp_suite", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/metasploit")
async def api_metasploit(
    target: str = "localhost",
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Metasploit exploit scan."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.metasploit_scan", current_user, resource=target)
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = metasploit_scan(target)
        _send_to_siem_soc("metasploit", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/advanced/packet_analysis")
async def api_packet_analysis(
    file_path: str = None,
    current_user: dict = Depends(get_current_user),
    action_id: str = Query(None)
):
    """Advanced packet analysis."""
    from fastapi.responses import JSONResponse
    from fastapi import HTTPException
    
    if action_id:
        action = get_action_by_id(action_id)
        if action and action.get("status") == "approved" and action.get("execution_result") is not None:
            import json
            result = action.get("execution_result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    pass
            return result
        elif action and action.get("status") == "pending":
            return JSONResponse(status_code=202, content={"error": {"status": "pending", "action_id": action_id, "message": "Action is still pending approval"}})
        elif action and action.get("status") == "rejected":
            return {"error": f"Action {action_id} was rejected"}
        elif not action:
            return {"error": f"Action {action_id} not found"}
    
    try:
        check_action_permission("security.packet_analysis", current_user, resource=file_path or "")
    except HTTPException as e:
        if e.status_code == 202:
            return JSONResponse(status_code=202, content={"error": e.detail})
        raise
    
    try:
        result = advanced_packet_analysis(file_path)
        _send_to_siem_soc("packet_analysis", result, current_user)
        return result
    except Exception as e:
        return {"error": str(e)}

