"""Role-based approval engine."""
import json
from backend.database.connection import get_db, dict_from_row
from backend.services.risk_service import can_user_approve


def get_user(user_id: str) -> dict:
    """Get user by ID."""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return dict_from_row(row)


def get_all_users() -> list:
    """Get all users."""
    db = get_db()
    rows = db.execute("SELECT * FROM users ORDER BY role, name").fetchall()
    db.close()
    return [dict_from_row(r) for r in rows]


def check_approval_permission(user_id: str, risk_level: str) -> dict:
    """Check if user can approve for given risk level."""
    user = get_user(user_id)
    if not user:
        return {"allowed": False, "reason": "User not found."}

    return can_user_approve(user["role"], risk_level)


def get_approval_rules() -> list:
    """Get all approval rules."""
    db = get_db()
    rows = db.execute("SELECT * FROM approval_rules ORDER BY risk_level").fetchall()
    db.close()
    return [dict_from_row(r) for r in rows]
