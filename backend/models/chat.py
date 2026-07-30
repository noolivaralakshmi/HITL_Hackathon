"""Chat message models."""
from pydantic import BaseModel
from typing import Optional, Any


class ChatMessage(BaseModel):
    id: str
    memory_id: str
    user_id: Optional[str] = None
    role: str
    content: str
    created_at: Optional[str] = None


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    ai_message: ChatMessage
    reasoning_update: Optional[Any] = None
