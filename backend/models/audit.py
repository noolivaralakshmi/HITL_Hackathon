"""Audit/action log models."""
from pydantic import BaseModel
from typing import Optional, Any


class ActionLogEntry(BaseModel):
    id: str
    memory_id: str
    user_id: Optional[str] = None
    action: str
    risk_level: Optional[str] = None
    details: Any = {}
    ai_output: Optional[str] = None
    human_decision: Optional[str] = None
    timestamp: Optional[str] = None
