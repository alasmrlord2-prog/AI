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
    import logging
    logger = logging.getLogger(__name__)
    
    session_id = req.session_id or "default"
    
    try:
        logger.info(f"[Chat] Received message from session {session_id}: {req.message[:100]}")
        log_chat("user", session_id, req.message)
        
        # Validate message
        if not req.message or not req.message.strip():
            logger.warning(f"[Chat] Empty message received from session {session_id}")
            return ChatResponse(
                session_id=session_id,
                reply="الرجاء إدخال رسالة."
            )
        
        try:
            import asyncio
            
            logger.info(f"[Chat] Calling think_and_act for session {session_id}")
            
            # Run think_and_act in executor with timeout (max 50 seconds for chat)
            loop = asyncio.get_event_loop()
            reply = await asyncio.wait_for(
                loop.run_in_executor(None, think_and_act, req.message.strip()),
                timeout=50.0  # 50 second timeout for chat responses (reduced from 60)
            )
            
            logger.info(f"[Chat] Agent replied with {len(reply)} characters for session {session_id}")
            
            # Ensure reply is not empty - this should never happen now, but keep as safety
            if not reply or not reply.strip():
                logger.error(f"[Chat] Empty reply from agent for session {session_id}")
                reply = "عذراً، لم أتمكن من إنتاج رد. يرجى المحاولة مرة أخرى."
            
        except asyncio.TimeoutError:
            error_msg = "Request timeout - العملية استغرقت وقتاً طويلاً"
            logger.error(f"[Chat] Timeout for session {session_id}")
            log_chat("error", session_id, error_msg)
            reply = "⚠️ استغرقت العملية وقتاً طويلاً. يرجى المحاولة مرة أخرى أو تبسيط السؤال."
        
        except ConnectionError as e:
            error_msg = str(e)
            logger.error(f"[Chat] Connection error for session {session_id}: {error_msg}")
            log_chat("error", session_id, f"Connection error: {error_msg}")
            reply = f"⚠️ مشكلة في الاتصال بـ Ollama: {error_msg}\n\nتأكد من أن خدمة Ollama تعمل وأن الموديل متوفر."
        
        except Exception as e:
            import traceback
            error_msg = f"Agent error: {str(e)}\n{traceback.format_exc()}"
            logger.error(f"[Chat] Agent error for session {session_id}: {error_msg}")
            log_chat("error", session_id, error_msg)
            
            # Provide user-friendly error message
            if "Ollama" in str(e) or "connection" in str(e).lower():
                reply = f"⚠️ مشكلة في الاتصال بـ Ollama. تأكد من أن الخدمة تعمل.\n\nالخطأ: {str(e)}"
            else:
                reply = f"⚠️ حدث خطأ أثناء معالجة طلبك: {str(e)}\n\nيرجى المحاولة مرة أخرى أو الاتصال بالدعم الفني."
        
        # Final safety check - ensure we always have a reply
        if not reply or not reply.strip():
            logger.error(f"[Chat] Final safety check: empty reply for session {session_id}")
            reply = "عذراً، حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
        
        logger.info(f"[Chat] Sending reply to session {session_id}: {len(reply)} characters")
        log_chat("assistant", session_id, reply)
        return ChatResponse(session_id=session_id, reply=reply)
        
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        error_msg = f"Chat endpoint error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"[Chat] Endpoint error for session {session_id}: {error_msg}")
        log_chat("error", session_id, error_msg)
        return ChatResponse(
            session_id=session_id,
            reply=f"❌ خطأ في السيرفر: {str(e)}\n\nيرجى المحاولة مرة أخرى."
        )

