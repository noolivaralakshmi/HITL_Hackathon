"""Query service for Mode 2 - verified organizational knowledge.

Uses semantic search (vector embeddings) to find relevant memories,
then passes only the top matches to the AI for answer generation.
This scales to thousands of memories without stuffing them all into a prompt.
"""
import json
from backend.services.memory_service import get_verified_memories, get_memory
from backend.services.ai_service import query_verified_memory


def query_knowledge(question: str) -> dict:
    """Query verified organizational memory using semantic search.

    Flow:
    1. Semantic search to find top-k relevant memories
    2. Fall back to FTS/keyword if semantic search unavailable
    3. Pass relevant memories to AI for answer synthesis
    """
    # Try semantic search first
    relevant_memories = semantic_retrieve(question, top_k=5)

    if relevant_memories:
        # Format only the relevant memories for AI context
        memories_text = format_memories_for_query(relevant_memories)

        try:
            result = query_verified_memory(question, memories_text)
            # Attach search metadata
            result["search_method"] = "semantic"
            result["memories_searched"] = len(relevant_memories)
            result["similarity_scores"] = [
                {"memory_id": m["id"], "score": m.get("_similarity", 0)}
                for m in relevant_memories
            ]
            return result
        except Exception:
            return fallback_query(question, relevant_memories)

    # Fallback: get all verified memories (original behavior)
    verified = get_verified_memories()

    if not verified:
        return {
            "found": False,
            "message": "No verified organizational memory exists.",
            "search_method": "none",
            "possible_reasons": [
                "No reasoning records have been approved yet",
                "Supporting documents have never been uploaded",
                "The change was never documented"
            ]
        }

    # Format all memories for AI context (legacy behavior)
    memories_text = format_memories_for_query(verified)

    try:
        result = query_verified_memory(question, memories_text)
        result["search_method"] = "full_scan"
        result["memories_searched"] = len(verified)
        return result
    except Exception:
        return fallback_query(question, verified)


def semantic_retrieve(question: str, top_k: int = 5) -> list:
    """Retrieve relevant verified memories using semantic similarity.

    Returns full memory dicts for the top-k similar results,
    with a _similarity score attached.
    """
    try:
        from backend.services.embedding_service import semantic_search
        results = semantic_search(question, top_k=top_k)
    except Exception:
        return []

    if not results:
        return []

    # Filter by minimum similarity threshold
    MIN_SIMILARITY = 0.3
    filtered = [r for r in results if r["similarity"] >= MIN_SIMILARITY]

    if not filtered:
        return []

    # Load full memory records for matched IDs
    memories = []
    for result in filtered:
        memory = get_memory(result["memory_id"])
        if memory and memory.get("status") == "VERIFIED":
            memory["_similarity"] = round(result["similarity"], 4)
            memories.append(memory)

    return memories


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

        similarity_note = ""
        if mem.get("_similarity"):
            similarity_note = f"\nRelevance Score: {mem['_similarity']}"

        section = f"""
--- VERIFIED MEMORY (ID: {mem['id']}) ---
Change Type: {mem.get('change_type', 'Unknown')}
Confidence: {mem.get('confidence', 0)}%
Approved By: {mem.get('approved_by', 'Unknown')}
Approved At: {mem.get('approved_at', 'Unknown')}{similarity_note}
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
                "search_method": "keyword_fallback",
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
        "search_method": "keyword_fallback",
        "message": "No verified organizational memory matches this question.",
        "possible_reasons": [
            "The change was never documented",
            "The reasoning record has not yet been approved",
            "Supporting documents have never been uploaded"
        ]
    }
