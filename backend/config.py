"""Application configuration."""
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "app.db")

# AWS Bedrock Configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-2-lite-v1:0")

# Role hierarchy (higher index = more permissions)
ROLE_HIERARCHY = {
    "viewer": 0,
    "reviewer": 1,
    "approver": 2,
    "admin": 3,
}

# Approval rules by risk level
APPROVAL_RULES = {
    "LOW": {"required_role": "reviewer", "auto_approve": False, "blocked": False},
    "MEDIUM": {"required_role": "approver", "auto_approve": False, "blocked": False},
    "HIGH": {"required_role": "admin", "auto_approve": False, "blocked": False},
    "BLOCKED": {"required_role": None, "auto_approve": False, "blocked": True},
}
