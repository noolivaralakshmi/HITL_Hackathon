"""Rollback service - undo approved actions with snapshot restoration."""
import json
import uuid
from datetime import datetime
from backend.database.connection import get_db, dict_from_row
from backend.services.memory_service import get_memory, update_memory


def create_snapshot(memory_id: str, action: str) -> str:
    """Create a snapshot of current memory state before changes."""
    memory = get_memory(memory_id)
    if not memory:
        return None

    db = get_db()
    snapshot_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO memory_snapshots (id, memory_id, snapshot, action, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (snapshot_id, memory_id, json.dumps(memory), action, datetime.utcnow().isoformat())
    )
    db.commit()
    db.close()
    return snapshot_id


def get_snapshots(memory_id: str) -> list:
    """Get all snapshots for a memory."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM memory_snapshots WHERE memory_id = ? ORDER BY created_at DESC",
        (memory_id,)
    ).fetchall()
    db.close()
    results = []
    for row in rows:
        d = dict(row)
        if 'snapshot' in d and isinstance(d['snapshot'], str):
            try:
                d['snapshot'] = json.loads(d['snapshot'])
            except json.JSONDecodeError:
                pass
        results.append(d)
    return results


def rollback_memory(memory_id: str, user_id: str, reason: str) -> dict:
    """Rollback a memory to its pre-approval state.

    - Changes status to ROLLED_BACK
    - Records rollback reason and timestamp
    - Removes from verified memory pool (Mode 2 won't return it)
    """
    # Create snapshot of current state before rollback
    create_snapshot(memory_id, "PRE_ROLLBACK")

    now = datetime.utcnow().isoformat()

    # Update memory status
    db = get_db()
    db.execute(
        """UPDATE memories
           SET status = 'ROLLED_BACK', rolled_back_at = ?, rollback_reason = ?
           WHERE id = ?""",
        (now, reason, memory_id)
    )

    # Remove from FTS index
    try:
        db.execute("DELETE FROM memory_fts WHERE memory_id = ?", (memory_id,))
    except Exception:
        pass  # FTS entry may not exist

    db.commit()
    db.close()

    return get_memory(memory_id)


def restore_from_snapshot(memory_id: str, snapshot_id: str) -> dict:
    """Restore a memory from a specific snapshot."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM memory_snapshots WHERE id = ? AND memory_id = ?",
        (snapshot_id, memory_id)
    ).fetchone()
    db.close()

    if not row:
        return None

    snapshot_data = json.loads(row["snapshot"]) if isinstance(row["snapshot"], str) else row["snapshot"]

    # Restore key fields from snapshot
    update_fields = {
        "reasoning": snapshot_data.get("reasoning"),
        "missing_info": snapshot_data.get("missing_info"),
        "confidence": snapshot_data.get("confidence"),
        "risk_level": snapshot_data.get("risk_level"),
        "status": "DRAFT",  # Reset to draft for re-review
    }

    return update_memory(memory_id, **update_fields)
