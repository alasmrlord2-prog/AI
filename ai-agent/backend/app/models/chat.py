"""Chat-related models."""
from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: Optional[str] = None
    reply: str

