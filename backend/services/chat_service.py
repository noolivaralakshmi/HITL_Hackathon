"""HITL chat service - reviewer conversation with AI."""
import uuid
import json
from datetime import datetime
from backend.database.connection import get_db, dict_from_row
from backend.services.ai_service import hitl_chat
from backend.services.memory_service import get_memory, update_memory


def get_chat_history(memory_id: str) -> list:
    """Get all chat messages for a memory."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM chat_messages WHERE memory_id = ? ORDER BY created_at ASC",
        (memory_id,)
    ).fetchall()
    db.close()
    return [dict_from_row(r) for r in rows]


def save_message(memory_id: str, user_id: str, role: str, content: str) -> dict:
    """Save a chat message."""
    db = get_db()
    msg_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    db.execute(
        """INSERT INTO chat_messages (id, memory_id, user_id, role, content, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (msg_id, memory_id, user_id, role, content, now)
    )
    db.commit()
    db.close()
    return {"id": msg_id, "memory_id": memory_id, "user_id": user_id, "role": role, "content": content, "created_at": now}


def process_reviewer_message(memory_id: str, user_id: str, message: str) -> dict:
    """Process a reviewer message and get AI response.

    Returns AI response and any reasoning updates.
    """
    # Save reviewer message
    save_message(memory_id, user_id, "reviewer", message)

    # Get memory context
    memory = get_memory(memory_id)
    if not memory:
        return {"error": "Memory not found"}

    # Get source documents
    db = get_db()
    docs = db.execute(
        "SELECT filename, content FROM documents WHERE memory_id = ?",
        (memory_id,)
    ).fetchall()
    db.close()

    documents_text = "\n\n".join([
        f"=== {doc['filename']} ===\n{doc['content']}"
        for doc in docs
    ])

    # Call AI
    try:
        ai_response = hitl_chat(
            question=message,
            change_type=memory.get("change_type", "Unknown"),
            reasoning=memory.get("reasoning", {}),
            documents_text=documents_text
        )
    except Exception:
        # Fallback: generate response from reasoning data directly
        ai_response = generate_fallback_response(message, memory, docs)

    # Extract message and reasoning update
    ai_message = ai_response.get("message", "I couldn't process that request.")
    reasoning_update = ai_response.get("reasoning_update")

    # Save AI response
    ai_msg = save_message(memory_id, None, "ai", ai_message)

    # Apply reasoning update if provided
    if reasoning_update:
        current_reasoning = memory.get("reasoning", {})
        updated_reasoning = apply_reasoning_update(current_reasoning, reasoning_update)
        update_memory(memory_id, reasoning=updated_reasoning)

    return {
        "ai_message": ai_msg,
        "reasoning_update": reasoning_update
    }


def apply_reasoning_update(current: dict, update: dict) -> dict:
    """Apply a reasoning update from AI chat to current reasoning."""
    if not update:
        return current

    updated = current.copy() if isinstance(current, dict) else {}

    for field, instruction in update.items():
        if not isinstance(instruction, dict):
            continue

        action = instruction.get("action", "update")
        value = instruction.get("value")

        if action == "add":
            # Add to list field
            if field in updated and isinstance(updated[field], list):
                updated[field].append(value)
            elif field in updated and isinstance(updated[field], str):
                updated[field] = updated[field] + f"\n{value}"
            else:
                updated[field] = [value] if isinstance(value, str) else value

        elif action == "update":
            updated[field] = value

        elif action == "remove":
            if field in updated and isinstance(updated[field], list):
                updated[field] = [item for item in updated[field] if item != value]

    return updated


def generate_fallback_response(question: str, memory: dict, docs: list) -> dict:
    """Generate a contextual response from reasoning data when AI service is unavailable.

    Searches through the reasoning record and source documents to answer
    the reviewer's question using keyword matching.
    """
    question_lower = question.lower()
    reasoning = memory.get("reasoning", {})
    if isinstance(reasoning, str):
        try:
            reasoning = json.loads(reasoning)
        except (json.JSONDecodeError, TypeError):
            reasoning = {}

    # Map common question patterns to reasoning fields
    field_keywords = {
        "what_changed": ["what changed", "change", "migration", "moved", "switched"],
        "business_objective": ["business", "why", "objective", "goal", "purpose", "reason"],
        "technical_objective": ["technical", "how", "implement", "architecture"],
        "alternatives_considered": ["alternative", "other option", "rejected", "considered", "instead"],
        "risks_accepted": ["risk", "danger", "concern", "issue", "problem"],
        "assumptions": ["assumption", "assume", "expect", "believe"],
        "evidence": ["evidence", "document", "source", "proof", "support", "found in"],
        "decision_makers": ["who", "approved", "decided", "authority", "responsible", "owner"],
        "timeline": ["when", "timeline", "schedule", "date", "deadline"],
    }

    # Find the most relevant field
    best_field = None
    best_score = 0
    for field, keywords in field_keywords.items():
        score = sum(1 for kw in keywords if kw in question_lower)
        if score > best_score:
            best_score = score
            best_field = field

    # Build response from matching reasoning field
    if best_field and best_field in reasoning:
        value = reasoning[best_field]
        if isinstance(value, list):
            if best_field == "alternatives_considered":
                items = []
                for alt in value:
                    if isinstance(alt, dict):
                        items.append(f"• {alt.get('name', 'Unknown')}: Rejected because {alt.get('rejected_reason', 'no reason given')}")
                    else:
                        items.append(f"• {alt}")
                response_text = f"Based on the reasoning record, here are the {best_field.replace('_', ' ')}:\n\n" + "\n".join(items)
            elif best_field == "evidence":
                items = []
                for ev in value:
                    if isinstance(ev, dict):
                        items.append(f"• {ev.get('document', 'Unknown')}: {ev.get('supports', '')}")
                    else:
                        items.append(f"• {ev}")
                response_text = f"The evidence comes from these documents:\n\n" + "\n".join(items)
            else:
                response_text = f"According to the reasoning record ({best_field.replace('_', ' ')}):\n\n" + "\n".join(f"• {item}" for item in value)
        elif isinstance(value, str):
            response_text = f"According to the reasoning record:\n\n{value}"
        else:
            response_text = f"According to the reasoning record:\n\n{json.dumps(value, indent=2)}"

        # Add document citation if available
        cited_docs = [doc['filename'] for doc in docs] if docs else []
        if cited_docs:
            response_text += f"\n\nSource documents: {', '.join(cited_docs[:3])}"
    else:
        # Search documents for relevant content
        doc_matches = []
        for doc in docs:
            content = doc['content'].lower() if doc.get('content') else ""
            # Check if any significant question words appear in document
            q_words = [w for w in question_lower.split() if len(w) > 3]
            if any(word in content for word in q_words):
                doc_matches.append(doc['filename'])

        if doc_matches:
            response_text = (
                f"I found references to your question in: {', '.join(doc_matches)}.\n\n"
                f"Here's what the reasoning record contains:\n"
                f"• Change: {reasoning.get('what_changed', 'Not specified')}\n"
                f"• Business Objective: {reasoning.get('business_objective', 'Not specified')}\n"
                f"• Technical Objective: {reasoning.get('technical_objective', 'Not specified')}"
            )
        else:
            response_text = (
                "I couldn't find specific information about that in the source documents. "
                "The reasoning record covers:\n\n"
                + "\n".join(f"• {key.replace('_', ' ').title()}" for key in reasoning.keys())
                + "\n\nWould you like me to provide details on any of these sections?"
            )

    return {"message": response_text, "reasoning_update": None}
