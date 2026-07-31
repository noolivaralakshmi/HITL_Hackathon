"""Memory record CRUD service."""
import json
import uuid
from datetime import datetime
from backend.database.connection import get_db, dict_from_row


def create_memory(contributor_id: str) -> dict:
    """Create a new draft memory record."""
    db = get_db()
    memory_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO memories (id, status, contributor_id, created_at)
           VALUES (?, 'DRAFT', ?, ?)""",
        (memory_id, contributor_id, datetime.utcnow().isoformat())
    )
    db.commit()
    db.close()
    return {"id": memory_id, "status": "DRAFT"}


def get_memory(memory_id: str) -> dict:
    """Get a memory record by ID."""
    db = get_db()
    row = db.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
    db.close()
    return dict_from_row(row)


def list_memories(status: str = None) -> list:
    """List all memories, optionally filtered by status."""
    db = get_db()
    if status:
        rows = db.execute("SELECT * FROM memories WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM memories ORDER BY created_at DESC").fetchall()
    db.close()
    return [dict_from_row(r) for r in rows]


def update_memory(memory_id: str, **kwargs) -> dict:
    """Update memory record fields."""
    db = get_db()

    # Serialize JSON fields
    json_fields = ['detection_reasons', 'reasoning', 'missing_info', 'guardrail_flags']
    for field in json_fields:
        if field in kwargs and not isinstance(kwargs[field], str):
            kwargs[field] = json.dumps(kwargs[field])

    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [memory_id]

    db.execute(f"UPDATE memories SET {set_clause} WHERE id = ?", values)
    db.commit()
    db.close()
    return get_memory(memory_id)


def approve_memory(memory_id: str, user_id: str) -> dict:
    """Approve a memory record."""
    now = datetime.utcnow().isoformat()
    db = get_db()
    db.execute(
        """UPDATE memories SET status = 'VERIFIED', approved_by = ?, approved_at = ?
           WHERE id = ?""",
        (user_id, now, memory_id)
    )

    # Update FTS index - read from same connection
    row = db.execute("SELECT change_type, reasoning FROM memories WHERE id = ?", (memory_id,)).fetchone()
    if row:
        reasoning_text = row["reasoning"] if isinstance(row["reasoning"], str) else json.dumps(row["reasoning"])
        db.execute(
            "INSERT INTO memory_fts (memory_id, change_type, reasoning) VALUES (?, ?, ?)",
            (memory_id, row["change_type"] or "", reasoning_text)
        )

    db.commit()
    db.close()
    return get_memory(memory_id)


def reject_memory(memory_id: str, user_id: str) -> dict:
    """Reject a memory record."""
    db = get_db()
    db.execute(
        "UPDATE memories SET status = 'REJECTED' WHERE id = ?",
        (memory_id,)
    )
    db.commit()
    db.close()
    return get_memory(memory_id)


def get_verified_memories() -> list:
    """Get all verified memories for Mode 2 queries."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM memories WHERE status = 'VERIFIED' ORDER BY approved_at DESC"
    ).fetchall()
    db.close()
    return [dict_from_row(r) for r in rows]


def search_memories(query: str) -> list:
    """Search verified memories using FTS."""
    db = get_db()
    rows = db.execute(
        """SELECT m.* FROM memories m
           JOIN memory_fts fts ON fts.memory_id = m.id
           WHERE memory_fts MATCH ? AND m.status = 'VERIFIED'""",
        (query,)
    ).fetchall()
    db.close()
    if not rows:
        # Fallback to LIKE search
        return get_verified_memories()
    return [dict_from_row(r) for r in rows]
