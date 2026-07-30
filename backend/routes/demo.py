"""Demo data loading route."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter

from backend.database.connection import get_db
from backend.services.memory_service import update_memory
from backend.services.rollback_service import create_snapshot

router = APIRouter(prefix="/api/demo", tags=["demo"])

DEMO_DIR = Path(__file__).parent.parent.parent / "demo"


@router.get("/load")
def load_demo_data():
    """Load demo scenario: Password → Passkeys migration."""
    db = get_db()

    # Create memory record
    memory_id = "demo-memory-001"
    now = datetime.utcnow().isoformat()

    # Check if already loaded
    existing = db.execute("SELECT id FROM memories WHERE id = ?", (memory_id,)).fetchone()
    if existing:
        db.close()
        return {"status": "already_loaded", "memory_id": memory_id}

    # Insert memory
    db.execute(
        """INSERT INTO memories (id, change_type, confidence, detection_reasons,
           reasoning, missing_info, risk_level, guardrail_flags, status,
           reviewer_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            memory_id,
            "Authentication",
            96.0,
            json.dumps([
                "Passkeys implementation discussed",
                "MFA migration referenced",
                "Authentication APIs mentioned",
                "Security Review conducted"
            ]),
            json.dumps({
                "what_changed": "Password Authentication → Passkeys (WebAuthn)",
                "business_objective": "Reduce phishing attacks by 95% and eliminate password-related support tickets",
                "technical_objective": "Implement passwordless authentication using WebAuthn/FIDO2 standards",
                "alternatives_considered": [
                    {"name": "Keep Password Authentication", "rejected_reason": "High phishing risk - 67% of breaches involve credentials"},
                    {"name": "Hardware MFA Tokens", "rejected_reason": "Operational complexity - $45/token, logistics for 10K+ employees"},
                    {"name": "SMS-based 2FA", "rejected_reason": "SIM swap vulnerability - not recommended by NIST 800-63B"}
                ],
                "risks_accepted": [
                    "Older devices (pre-2019) require fallback authentication method",
                    "Initial user training period may cause support ticket spike",
                    "Platform authenticator lock-in risk if users lose device"
                ],
                "assumptions": [
                    "95% of users have devices supporting WebAuthn",
                    "IT support can handle 5% fallback cases manually",
                    "Browser compatibility covers 98% of corporate fleet"
                ],
                "evidence": [
                    {"document": "SecurityReview.pdf", "supports": "Phishing statistics and recommendation for passkeys"},
                    {"document": "ArchitectureDecision.pdf", "supports": "Technical implementation and WebAuthn standard"},
                    {"document": "MeetingNotes.pdf", "supports": "Team consensus and timeline agreement"},
                    {"document": "RiskAssessment.pdf", "supports": "Identified risks and mitigation strategies"},
                    {"document": "ApprovalEmail.pdf", "supports": "Executive sign-off and budget approval"}
                ],
                "decision_makers": ["CISO Sarah Chen", "VP Engineering Marcus Johnson", "Security Team Lead"],
                "timeline": "Q1 2026: Pilot (1000 users) → Q2 2026: Full rollout → Q3 2026: Password deprecation",
                "additional_context": "Part of broader Zero Trust initiative. Budget approved: $2.3M over 18 months."
            }),
            json.dumps([
                "⚠ No rollback strategy found",
                "⚠ No risk owner assigned",
                "⚠ No compliance review documented"
            ]),
            "MEDIUM",
            json.dumps([]),
            "DRAFT",
            "user-reviewer-001",
            now
        )
    )

    # Load demo documents
    demo_docs = {
        "meeting_notes.txt": "MeetingNotes.pdf",
        "security_review.txt": "SecurityReview.pdf",
        "architecture_decision.txt": "ArchitectureDecision.pdf",
        "risk_assessment.txt": "RiskAssessment.pdf",
        "approval_email.txt": "ApprovalEmail.pdf",
    }

    for filename, display_name in demo_docs.items():
        file_path = DEMO_DIR / filename
        if file_path.exists():
            content = file_path.read_text()
        else:
            content = f"[Demo content for {display_name}]"

        doc_id = f"demo-doc-{filename.split('.')[0]}"
        db.execute(
            """INSERT OR IGNORE INTO documents (id, memory_id, filename, file_type, content, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (doc_id, memory_id, display_name, "txt", content, now)
        )

    # Add demo audit log entries
    audit_entries = [
        ("USER_REQUEST", "user-reviewer-001", "MEDIUM",
         {"document_count": 5, "documents": list(demo_docs.values())}, None, "Uploaded 5 documents for analysis"),
        ("AI_DRAFT", None, "MEDIUM",
         {"change_type": "Authentication", "confidence": 96, "guardrail_flags_count": 0, "missing_info_count": 3},
         "AI generated reasoning record", None),
        ("GUARDRAIL_FLAG", None, "MEDIUM",
         {"flags": [{"type": "low_confidence", "severity": "info", "message": "All checks passed"}]},
         None, None),
    ]

    for i, (action, user_id, risk, details, ai_out, human_dec) in enumerate(audit_entries):
        db.execute(
            """INSERT INTO action_log (id, memory_id, user_id, action, risk_level, details, ai_output, human_decision, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (f"demo-audit-{i:03d}", memory_id, user_id, action, risk,
             json.dumps(details), ai_out, human_dec, now)
        )

    db.commit()
    db.close()

    # Create initial snapshot
    create_snapshot(memory_id, "DEMO_LOADED")

    return {"status": "loaded", "memory_id": memory_id}
