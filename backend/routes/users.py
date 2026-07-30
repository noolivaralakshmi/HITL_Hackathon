"""User management routes."""
from fastapi import APIRouter

from backend.services.approval_service import get_all_users, get_user, get_approval_rules

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
def list_users():
    """List all users."""
    return {"users": get_all_users()}


@router.get("/{user_id}")
def get_user_by_id(user_id: str):
    """Get a single user."""
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404
    return user


@router.get("/rules/approval")
def get_rules():
    """Get approval rules."""
    return {"rules": get_approval_rules()}
