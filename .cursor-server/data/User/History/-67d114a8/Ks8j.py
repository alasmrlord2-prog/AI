"""Knowledge Base API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeItem(BaseModel):
    """Knowledge item model."""
    id: Optional[str] = None
    title: str
    content: str
    category: str = "general"
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SearchRequest(BaseModel):
    """Search request."""
    query: str
    limit: int = 10


# Simple in-memory storage (in production, use a database)
knowledge_storage: List[dict] = []


@router.get("")
async def list_knowledge(
    category: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List knowledge items."""
    items = knowledge_storage.copy()
    
    if category:
        items = [item for item in items if item.get("category") == category]
    
    # Sort by created_at descending
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "items": items[:limit]
    }


@router.post("")
async def create_knowledge(
    item: KnowledgeItem,
    current_user: dict = Depends(get_current_user)
):
    """Create a knowledge item."""
    from datetime import datetime
    import uuid
    
    knowledge_item = {
        "id": str(uuid.uuid4()),
        "title": item.title,
        "content": item.content,
        "category": item.category,
        "tags": item.tags,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    knowledge_storage.append(knowledge_item)
    
    return knowledge_item


@router.get("/{item_id}")
async def get_knowledge(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a knowledge item by ID."""
    item = next((i for i in knowledge_storage if i.get("id") == item_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    return item


@router.put("/{item_id}")
async def update_knowledge(
    item_id: str,
    item: KnowledgeItem,
    current_user: dict = Depends(get_current_user)
):
    """Update a knowledge item."""
    from datetime import datetime
    
    existing = next((i for i in knowledge_storage if i.get("id") == item_id), None)
    
    if not existing:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    existing.update({
        "title": item.title,
        "content": item.content,
        "category": item.category,
        "tags": item.tags,
        "updated_at": datetime.now().isoformat(),
    })
    
    return existing


@router.delete("/{item_id}")
async def delete_knowledge(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a knowledge item."""
    global knowledge_storage
    item = next((i for i in knowledge_storage if i.get("id") == item_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    knowledge_storage = [i for i in knowledge_storage if i.get("id") != item_id]
    
    return {"success": True, "message": "Knowledge item deleted"}


@router.post("/search")
async def search_knowledge(
    req: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Search knowledge base using semantic search."""
    query_lower = req.query.lower()
    results = []
    
    for item in knowledge_storage:
        score = 0.0
        
        # Simple keyword matching (in production, use embeddings/vector search)
        title_match = query_lower in item.get("title", "").lower()
        content_match = query_lower in item.get("content", "").lower()
        category_match = query_lower in item.get("category", "").lower()
        tags_match = any(query_lower in tag.lower() for tag in item.get("tags", []))
        
        if title_match:
            score += 0.5
        if content_match:
            score += 0.3
        if category_match:
            score += 0.1
        if tags_match:
            score += 0.1
        
        if score > 0:
            results.append({
                "item": item,
                "score": score,
                "relevance": "high" if score > 0.5 else "medium" if score > 0.2 else "low"
            })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "results": results[:req.limit]
    }

