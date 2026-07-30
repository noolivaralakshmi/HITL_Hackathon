"""Memory record models."""
from pydantic import BaseModel
from typing import Optional, List, Any
from enum import Enum


class MemoryStatus(str, Enum):
    DRAFT = "DRAFT"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"
    BLOCKED = "BLOCKED"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


class MemoryRecord(BaseModel):
    id: str
    change_type: Optional[str] = None
    confidence: float = 0
    detection_reasons: List[str] = []
    reasoning: Any = {}
    missing_info: List[str] = []
    risk_level: RiskLevel = RiskLevel.MEDIUM
    guardrail_flags: List[Any] = []
    status: MemoryStatus = MemoryStatus.DRAFT
    reviewer_id: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: Optional[str] = None
    approved_at: Optional[str] = None
    rolled_back_at: Optional[str] = None
    rollback_reason: Optional[str] = None


class GenerateMemoryRequest(BaseModel):
    document_ids: List[str]
    user_id: str


class ApproveRequest(BaseModel):
    user_id: str


class RejectRequest(BaseModel):
    user_id: str
    reason: str


class EditReasoningRequest(BaseModel):
    user_id: str
    reasoning: Any


class RollbackRequest(BaseModel):
    user_id: str
    reason: str
