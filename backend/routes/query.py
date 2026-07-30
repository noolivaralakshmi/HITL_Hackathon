"""Query routes for Mode 2 - verified knowledge."""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.query_service import query_knowledge

router = APIRouter(prefix="/api/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str


@router.post("")
def query_verified_knowledge(req: QueryRequest):
    """Query verified organizational memory.

    ONLY returns answers from VERIFIED memories.
    Never searches drafts, rejected, or rolled-back records.
    """
    return query_knowledge(req.question)
