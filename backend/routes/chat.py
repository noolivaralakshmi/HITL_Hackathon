"""Chat routes for HITL interaction."""
from fastapi import APIRouter, HTTPException

from backend.models.chat import ChatRequest
from backend.services.chat_service import get_chat_history, process_reviewer_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/{memory_id}")
def send_message(memory_id: str, req: ChatRequest):
    """Send a reviewer message and get AI response."""
    result = process_reviewer_message(memory_id, req.user_id, req.message)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/{memory_id}")
def get_history(memory_id: str):
    """Get chat history for a memory."""
    history = get_chat_history(memory_id)
    return {"messages": history}
