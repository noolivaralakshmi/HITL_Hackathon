"""Query routes for Mode 2 - verified knowledge with semantic search."""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.query_service import query_knowledge
from backend.services.memory_service import get_verified_memories

router = APIRouter(prefix="/api/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str


@router.post("")
def query_verified_knowledge(req: QueryRequest):
    """Query verified organizational memory using semantic search.

    Uses vector embeddings to find the most relevant verified memories,
    then synthesizes an answer from those memories only.
    Falls back to full-scan if semantic search is unavailable.
    """
    return query_knowledge(req.question)


@router.post("/reindex")
def reindex_all_memories():
    """Re-index all verified memories for semantic search.

    Use this endpoint to bootstrap the vector index when:
    - Deploying semantic search for the first time
    - Embeddings model changes
    - Index becomes corrupted
    """
    from backend.services.embedding_service import index_memory

    verified = get_verified_memories()
    results = {"indexed": 0, "failed": 0, "errors": []}

    for mem in verified:
        result = index_memory(mem["id"], mem)
        if result.get("indexed"):
            results["indexed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "memory_id": mem["id"],
                "error": result.get("error", "Unknown")
            })

    return {
        "total_verified": len(verified),
        **results,
    }
