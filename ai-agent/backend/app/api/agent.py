"""Legacy agent endpoint for compatibility."""
from fastapi import APIRouter
from app.models.chat import ChatRequest

router = APIRouter(tags=["agent"])

# Import agent function
try:
    from app.agent.think_and_act import think_and_act
except ImportError as e:
    def think_and_act(message: str) -> str:
        return f"Agent not available: {str(e)}"


@router.post("/api/agent/run")
def run_agent(q: ChatRequest):
    """Legacy agent endpoint."""
    result = think_and_act(q.message)
    return {"result": result}

