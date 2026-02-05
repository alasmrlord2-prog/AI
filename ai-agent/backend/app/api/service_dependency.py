"""
Service Dependency Graph API
واجهات API لخريطة التبعيات
"""
from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.services.service_dependency_graph import get_dependency_graph
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/services/dependency", tags=["service-dependency"])


@router.post("/discover")
async def discover_services(current_user: dict = Depends(get_current_user)):
    """اكتشاف الخدمات تلقائياً"""
    try:
        check_action_permission("services.view", current_user)
    except HTTPException:
        pass
    
    graph = get_dependency_graph()
    result = graph.discover_services()
    
    return result


@router.get("/graph")
async def get_graph(current_user: dict = Depends(get_current_user)):
    """الحصول على الـgraph الكامل"""
    try:
        check_action_permission("services.view", current_user)
    except HTTPException:
        pass
    
    graph = get_dependency_graph()
    result = graph.get_graph()
    
    return result


@router.get("/{service_id}")
async def get_service_dependencies(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """الحصول على تبعيات خدمة"""
    try:
        check_action_permission("services.view", current_user)
    except HTTPException:
        pass
    
    graph = get_dependency_graph()
    result = graph.get_service_dependencies(service_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/{service_id}/impact")
async def get_impact_analysis(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """تحليل التأثير عند توقف خدمة"""
    try:
        check_action_permission("services.view", current_user)
    except HTTPException:
        pass
    
    graph = get_dependency_graph()
    result = graph.get_impact_analysis(service_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/connection")
async def add_connection(
    from_service: str,
    to_service: str,
    connection_type: str = "http",
    current_user: dict = Depends(get_current_user)
):
    """إضافة اتصال يدوياً"""
    try:
        check_action_permission("services.manage", current_user)
    except HTTPException:
        pass
    
    graph = get_dependency_graph()
    graph.add_connection(from_service, to_service, connection_type)
    
    return {"success": True, "message": "Connection added"}

