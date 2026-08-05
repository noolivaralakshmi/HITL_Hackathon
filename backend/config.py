"""Application configuration."""
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "app.db")

# AWS Bedrock Configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-2-lite-v1:0")
BEDROCK_GUARDRAIL_ID = os.environ.get("BEDROCK_GUARDRAIL_ID", "ka5t8n9etx95")
BEDROCK_GUARDRAIL_VERSION = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "5")

# S3 Configuration for document storage
S3_BUCKET = os.environ.get("S3_BUCKET", "hitl-change-impact-memory-docs")
S3_PREFIX = os.environ.get("S3_PREFIX", "organizational-memory/")

# Role definitions
# contributor: can upload docs, create memory, edit, discard, send for approval
# contributor+reviewer: all of above + can approve/reject memories assigned to them
ROLES = {
    "contributor": {
        "can_contribute": True,
        "can_review": False,
    },
    "contributor+reviewer": {
        "can_contribute": True,
        "can_review": True,
    },
}
