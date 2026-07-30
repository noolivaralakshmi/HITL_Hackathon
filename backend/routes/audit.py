"""Audit log routes."""
from fastapi import APIRouter

from backend.database.connection import get_db, dict_from_row

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/{memory_id}")
def get_audit_log(memory_id: str):
    """Get the full audit/action log for a memory."""
    db = get_db()
    rows = db.execute(
        """SELECT al.*, u.name as user_name, u.role as user_role
           FROM action_log al
           LEFT JOIN users u ON al.user_id = u.id
           WHERE al.memory_id = ?
           ORDER BY al.timestamp ASC""",
        (memory_id,)
    ).fetchall()
    db.close()
    return {"log": [dict_from_row(r) for r in rows]}
