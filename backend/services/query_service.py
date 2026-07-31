"""Query service for Mode 2 - verified organizational knowledge."""
import json
from backend.services.memory_service import get_verified_memories, search_memories
from backend.services.ai_service import query_verified_memory


def query_knowledge(question: str) -> dict:
    """Query verified organizational memory.

    ONLY searches approved/verified memories.
    Never returns drafts, rejected, or rolled-back memories.
    """
    # Get all verified memories
    verified = get_verified_memories()

    if not verified:
        return {
            "found": False,
            "message": "No verified organizational memory exists.",
            "possible_reasons": [
                "No reasoning records have been approved yet",
                "Supporting documents have never been uploaded",
                "The change was never documented"
            ]
        }

    # Format memories for AI context
    memories_text = format_memories_for_query(verified)

    # Ask AI to answer from verified memory only
    try:
        result = query_verified_memory(question, memories_text)
        return result
    except Exception as e:
        # Fallback: direct search in verified memories without AI
        return fallback_query(question, verified)


def format_memories_for_query(memories: list) -> str:
    """Format verified memories as context for AI."""
    sections = []
    for mem in memories:
        reasoning = mem.get("reasoning", {})
        if isinstance(reasoning, str):
            try:
                reasoning = json.loads(reasoning)
            except json.JSONDecodeError:
                reasoning = {}

        section = f"""
--- VERIFIED MEMORY (ID: {mem['id']}) ---
Change Type: {mem.get('change_type', 'Unknown')}
Confidence: {mem.get('confidence', 0)}%
Approved By: {mem.get('approved_by', 'Unknown')}
Approved At: {mem.get('approved_at', 'Unknown')}
Reasoning: {json.dumps(reasoning, indent=2)}
---"""
        sections.append(section)

    return "\n\n".join(sections)


def fallback_query(question: str, memories: list) -> dict:
    """Fallback query when AI service is unavailable.

    Does keyword matching against verified memory reasoning.
    """
    question_lower = question.lower()

    for mem in memories:
        reasoning = mem.get("reasoning", {})
        if isinstance(reasoning, str):
            try:
                reasoning = json.loads(reasoning)
            except json.JSONDecodeError:
                reasoning = {}

        # Simple keyword match against reasoning text
        reasoning_text = json.dumps(reasoning).lower()
        if any(word in reasoning_text for word in question_lower.split() if len(word) > 3):
            # Build answer from structured reasoning
            alternatives = reasoning.get("alternatives_considered", [])
            evidence_docs = reasoning.get("evidence", [])

            return {
                "found": True,
                "answer": {
                    "summary": f"According to verified organizational memory about {mem.get('change_type', 'this change')}:",
                    "decision": reasoning.get("what_changed", "See reasoning record"),
                    "reason": reasoning.get("business_objective", reasoning.get("technical_objective", "")),
                    "rejected_alternatives": [
                        {"name": alt.get("name", ""), "reason": alt.get("rejected_reason", "")}
                        for alt in alternatives
                    ],
                    "evidence": [e.get("document", e) if isinstance(e, dict) else str(e) for e in evidence_docs],
                    "approved_by": mem.get("approver_name", mem.get("approved_by", "Unknown")),
                    "confidence": mem.get("confidence", 0),
                    "memory_id": mem.get("id")
                }
            }

    return {
        "found": False,
        "message": "No verified organizational memory matches this question.",
        "possible_reasons": [
            "The change was never documented",
            "The reasoning record has not yet been approved",
            "Supporting documents have never been uploaded"
        ]
    }
