"""User and role models."""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    APPROVER = "approver"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class User(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    created_at: Optional[str] = None


class UserSwitch(BaseModel):
    user_id: str
