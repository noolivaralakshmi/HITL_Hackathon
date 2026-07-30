"""Risk and guardrail models."""
from pydantic import BaseModel
from typing import Optional, List


class GuardrailFlag(BaseModel):
    type: str  # pii, unsupported_claim, harmful_content, low_confidence, hallucination
    severity: str  # warning, critical, blocked
    message: str
    field: Optional[str] = None  # which reasoning field triggered this


class RiskAssessment(BaseModel):
    risk_level: str
    guardrail_flags: List[GuardrailFlag] = []
    reasoning: str


class ApprovalRule(BaseModel):
    id: str
    risk_level: str
    required_role: Optional[str] = None
    auto_approve: bool = False
    blocked: bool = False
    description: str
