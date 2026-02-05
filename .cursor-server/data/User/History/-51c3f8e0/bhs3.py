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
    session_id = req.session_id or "default"
    
    try:
        log_chat("user", session_id, req.message)
        
        # Validate message
        if not req.message or not req.message.strip():
            return ChatResponse(
                session_id=session_id,
                reply="الرجاء إدخال رسالة."
            )
        
        try:
            reply = think_and_act(req.message.strip())
            
            # Ensure reply is not empty
            if not reply or not reply.strip():
                reply = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."
            
        except ConnectionError as e:
            error_msg = str(e)
            log_chat("error", session_id, f"Connection error: {error_msg}")
            reply = f"⚠️ مشكلة في الاتصال بـ Ollama: {error_msg}\n\nتأكد من أن خدمة Ollama تعمل وأن الموديل متوفر."
        
        except Exception as e:
            import traceback
            error_msg = f"Agent error: {str(e)}\n{traceback.format_exc()}"
            log_chat("error", session_id, error_msg)
            
            # Provide user-friendly error message
            if "Ollama" in str(e) or "connection" in str(e).lower():
                reply = f"⚠️ مشكلة في الاتصال بـ Ollama. تأكد من أن الخدمة تعمل.\n\nالخطأ: {str(e)}"
            else:
                reply = f"⚠️ حدث خطأ أثناء معالجة طلبك: {str(e)}\n\nيرجى المحاولة مرة أخرى أو الاتصال بالدعم الفني."
        
        log_chat("assistant", session_id, reply)
        return ChatResponse(session_id=session_id, reply=reply)
        
    except Exception as e:
        import traceback
        error_msg = f"Chat endpoint error: {str(e)}\n{traceback.format_exc()}"
        log_chat("error", session_id, error_msg)
        return ChatResponse(
            session_id=session_id,
            reply=f"❌ خطأ في السيرفر: {str(e)}\n\nيرجى المحاولة مرة أخرى."
        )

