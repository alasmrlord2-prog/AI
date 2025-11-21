"""
Global Search API
واجهات API لمحرك البحث الشامل
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.api.auth import get_current_user
from app.services.global_search import get_global_search
from app.core.permission_helpers import check_action_permission

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/")
async def search(
    q: str = Query(..., description="Search query"),
    sources: Optional[str] = Query(None, description="Comma-separated sources: logs,files,workflows,docs,configs"),
    max_results: int = Query(100, description="Maximum number of results"),
    current_user: dict = Depends(get_current_user)
):
    """بحث شامل"""
    try:
        check_action_permission("search.global", current_user)
    except HTTPException:
        pass
    
    search_engine = get_global_search()
    
    # تحليل sources
    sources_list = None
    if sources:
        sources_list = [s.strip() for s in sources.split(",")]
    
    result = search_engine.search(
        query=q,
        sources=sources_list,
        max_results=max_results
    )
    
    return result


@router.post("/path/add")
async def add_search_path(
    source: str,
    path: str,
    current_user: dict = Depends(get_current_user)
):
    """إضافة مسار بحث جديد"""
    try:
        check_action_permission("search.configure", current_user)
    except HTTPException:
        pass
    
    search_engine = get_global_search()
    search_engine.add_search_path(source, path)
    
    return {"success": True, "message": f"Added search path: {source} -> {path}"}

