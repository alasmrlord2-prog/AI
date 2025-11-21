"""WebSocket endpoints."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.utils.helpers import log_chat

router = APIRouter(tags=["websocket"])

# Import agent
try:
    from agent.think_and_act import think_and_act
except ImportError as e:
    def think_and_act(message: str) -> str:
        return f"Agent not available: {str(e)}"


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_json(self, websocket: WebSocket, data: dict):
        """Send JSON data through WebSocket."""
        await websocket.send_json(data)


manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            session_id = data.get("session_id") or "default"
            message = data.get("message") or ""
            
            log_chat("user", session_id, message)
            
            await manager.send_json(websocket, {
                "type": "start",
                "session_id": session_id,
            })
            
            reply = think_and_act(message)
            log_chat("assistant", session_id, reply)
            
            await manager.send_json(websocket, {
                "type": "chunk",
                "session_id": session_id,
                "text": reply,
            })
            
            await manager.send_json(websocket, {
                "type": "end",
                "session_id": session_id,
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        log_chat("error", None, f"WebSocket error: {e}")
        try:
            await manager.send_json(websocket, {
                "type": "error",
                "error": str(e),
            })
        except Exception:
            pass


@router.websocket("/ws/agent")
async def websocket_agent(ws: WebSocket):
    """Legacy WebSocket endpoint for compatibility."""
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            reply = think_and_act(data)
            await ws.send_text(reply)
    except WebSocketDisconnect:
        pass

