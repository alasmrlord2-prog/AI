"""Chat API endpoints."""
from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.utils.helpers import log_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Import agent function
try:
    from app.agent.think_and_act import think_and_act
except ImportError as e:
    def think_and_act(message: str) -> str:
        return f"Agent not available: {str(e)}"


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat endpoint."""
    try:
        session_id = req.session_id or "default"
        log_chat("user", session_id, req.message)
        
        try:
            reply = think_and_act(req.message)
        except Exception as e:
            import traceback
            error_msg = f"Agent error: {str(e)}\n{traceback.format_exc()}"
            log_chat("error", session_id, error_msg)
            reply = f"خطأ في الـ Agent: {str(e)}"
        
        log_chat("assistant", session_id, reply)
        return ChatResponse(session_id=session_id, reply=reply)
    except Exception as e:
        import traceback
        error_msg = f"Chat endpoint error: {str(e)}\n{traceback.format_exc()}"
        log_chat("error", None, error_msg)
        return ChatResponse(
            session_id=req.session_id or "default",
            reply=f"خطأ في السيرفر: {str(e)}"
        )

