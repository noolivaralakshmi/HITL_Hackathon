"""Embedding service using Amazon Bedrock Titan Embeddings for semantic search.

Provides vector-based memory retrieval so verified memories can be
discovered semantically rather than relying on exact keyword matches
or stuffing all memories into a single prompt.
"""
import json
import numpy as np
import boto3
from backend.config import AWS_REGION

# Bedrock Titan Embeddings model
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBEDDING_DIMENSION = 1024


def get_bedrock_client():
    """Create a Bedrock runtime client."""
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def generate_embedding(text: str) -> list:
    """Generate an embedding vector for the given text using Bedrock Titan.

    Args:
        text: The text to embed (max ~8000 tokens for Titan v2)

    Returns:
        A list of floats representing the embedding vector
    """
    client = get_bedrock_client()

    # Truncate to avoid token limits (roughly 4 chars per token)
    truncated = text[:30000]

    body = json.dumps({
        "inputText": truncated,
        "dimensions": EMBEDDING_DIMENSION,
        "normalize": True,
    })

    response = client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    result = json.loads(response["body"].read())
    return result["embedding"]


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def build_memory_text_for_embedding(memory: dict) -> str:
    """Build a text representation of a memory suitable for embedding.

    Combines the key fields that would be searched: change type,
    what changed, objectives, risks, alternatives, etc.
    """
    reasoning = memory.get("reasoning", {})
    if isinstance(reasoning, str):
        try:
            reasoning = json.loads(reasoning)
        except json.JSONDecodeError:
            reasoning = {}

    parts = []

    # Change type
    if memory.get("change_type"):
        parts.append(f"Change Type: {memory['change_type']}")

    # Core reasoning fields
    for field in ["what_changed", "business_objective", "technical_objective",
                  "timeline", "additional_context"]:
        if reasoning.get(field):
            parts.append(f"{field}: {reasoning[field]}")

    # Alternatives
    alternatives = reasoning.get("alternatives_considered", [])
    if alternatives:
        alt_text = "; ".join(
            f"{a.get('name', '')}: {a.get('rejected_reason', '')}"
            for a in alternatives if isinstance(a, dict)
        )
        parts.append(f"Alternatives considered: {alt_text}")

    # Risks
    risks = reasoning.get("risks_accepted", [])
    if risks:
        parts.append(f"Risks accepted: {'; '.join(str(r) for r in risks)}")

    # Decision makers
    makers = reasoning.get("decision_makers", [])
    if makers:
        parts.append(f"Decision makers: {', '.join(str(m) for m in makers)}")

    return "\n".join(parts)


def index_memory(memory_id: str, memory: dict) -> dict:
    """Generate embedding for a memory and store it in the database.

    Called when a memory is approved/verified.

    Returns:
        dict with memory_id and embedding status
    """
    from backend.database.connection import get_db

    text = build_memory_text_for_embedding(memory)

    try:
        embedding = generate_embedding(text)
    except Exception as e:
        return {"memory_id": memory_id, "indexed": False, "error": str(e)}

    db = get_db()
    # Upsert: delete any existing embedding for this memory, then insert
    db.execute("DELETE FROM memory_embeddings WHERE memory_id = ?", (memory_id,))
    db.execute(
        "INSERT INTO memory_embeddings (memory_id, embedding, text_content) VALUES (?, ?, ?)",
        (memory_id, json.dumps(embedding), text)
    )
    db.commit()
    db.close()

    return {"memory_id": memory_id, "indexed": True}


def remove_memory_index(memory_id: str):
    """Remove a memory's embedding from the index (on rollback/rejection)."""
    from backend.database.connection import get_db
    db = get_db()
    db.execute("DELETE FROM memory_embeddings WHERE memory_id = ?", (memory_id,))
    db.commit()
    db.close()


def semantic_search(query: str, top_k: int = 5) -> list:
    """Search for the most relevant verified memories using semantic similarity.

    Args:
        query: The user's natural language question
        top_k: Number of top results to return

    Returns:
        List of dicts with memory_id, similarity score, and text content
    """
    from backend.database.connection import get_db

    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
    except Exception as e:
        return []

    # Load all stored embeddings
    db = get_db()
    rows = db.execute(
        "SELECT memory_id, embedding, text_content FROM memory_embeddings"
    ).fetchall()
    db.close()

    if not rows:
        return []

    # Compute similarities
    results = []
    for row in rows:
        stored_embedding = json.loads(row["embedding"])
        similarity = cosine_similarity(query_embedding, stored_embedding)
        results.append({
            "memory_id": row["memory_id"],
            "similarity": similarity,
            "text_content": row["text_content"],
        })

    # Sort by similarity descending and return top_k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]
