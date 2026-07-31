"""User management and authentication routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database.connection import get_db, dict_from_row

router = APIRouter(prefix="/api/users", tags=["users"])


class LoginRequest(BaseModel):
    email: str


@router.post("/login")
def login(req: LoginRequest):
    """Login by email (SSO-style demo). Returns user if found."""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (req.email,)).fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found. Please use a registered email.")
    return dict_from_row(row)


@router.get("")
def list_users():
    """List all users."""
    db = get_db()
    rows = db.execute("SELECT * FROM users ORDER BY role, name").fetchall()
    db.close()
    return {"users": [dict_from_row(r) for r in rows]}


@router.get("/reviewers")
def list_reviewers():
    """List users who can review (contributor+reviewer role)."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM users WHERE role = 'contributor+reviewer' ORDER BY name"
    ).fetchall()
    db.close()
    return {"reviewers": [dict_from_row(r) for r in rows]}


@router.get("/{user_id}")
def get_user_by_id(user_id: str):
    """Get a single user."""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict_from_row(row)


@router.get("/{user_id}/dashboard")
def get_dashboard(user_id: str):
    """Get dashboard data for a user based on their role."""
    db = get_db()

    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = dict_from_row(user)
    dashboard = {"user": user_dict, "tabs": {}}

    # Tab 1: My Contributions (all roles see this)
    contributions = db.execute(
        """SELECT m.*, u.name as reviewer_name FROM memories m
           LEFT JOIN users u ON m.assigned_reviewer = u.id
           WHERE m.contributor_id = ?
           ORDER BY m.created_at DESC""",
        (user_id,)
    ).fetchall()
    dashboard["tabs"]["contributed"] = [dict_from_row(r) for r in contributions]

    # If user is a reviewer, show review tabs
    if user_dict["role"] == "contributor+reviewer":
        # Tab 2: Pending My Review
        pending = db.execute(
            """SELECT m.*, u.name as contributor_name FROM memories m
               LEFT JOIN users u ON m.contributor_id = u.id
               WHERE m.assigned_reviewer = ? AND m.status = 'PENDING_REVIEW'
               ORDER BY m.submitted_at DESC""",
            (user_id,)
        ).fetchall()
        dashboard["tabs"]["pending_review"] = [dict_from_row(r) for r in pending]

        # Tab 3: Approved by me
        approved = db.execute(
            """SELECT m.*, u.name as contributor_name FROM memories m
               LEFT JOIN users u ON m.contributor_id = u.id
               WHERE m.approved_by = ? AND m.status = 'VERIFIED'
               ORDER BY m.approved_at DESC""",
            (user_id,)
        ).fetchall()
        dashboard["tabs"]["approved"] = [dict_from_row(r) for r in approved]

        # Tab 4: Rejected by me
        rejected = db.execute(
            """SELECT m.*, u.name as contributor_name FROM memories m
               LEFT JOIN users u ON m.contributor_id = u.id
               WHERE m.approved_by = ? AND m.status = 'REJECTED'
               ORDER BY m.created_at DESC""",
            (user_id,)
        ).fetchall()
        dashboard["tabs"]["rejected"] = [dict_from_row(r) for r in rejected]

    db.close()
    return dashboard
