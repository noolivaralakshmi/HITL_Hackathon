"""Memory management routes."""
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel as PydanticBaseModel

from backend.services.ai_service import GuardrailBlockedException

from backend.database.connection import get_db, dict_from_row
from backend.models.memory import (
    GenerateMemoryRequest, ApproveRequest,
    RejectRequest, EditReasoningRequest, RollbackRequest
)
from backend.services.memory_service import (
    create_memory, get_memory, list_memories,
    update_memory, approve_memory, reject_memory
)
from backend.services.ai_service import analyze_documents, detect_missing_info
from backend.services.guardrail_service import run_guardrails
from backend.services.risk_service import assess_risk
from backend.services.approval_service import check_approval_permission
from backend.services.rollback_service import (
    create_snapshot, rollback_memory, get_snapshots
)

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.post("/generate")
def generate_memory(req: GenerateMemoryRequest):
    """Generate a memory record from uploaded documents."""
    db = get_db()

    # Get document contents
    placeholders = ",".join("?" * len(req.document_ids))
    docs = db.execute(
        f"SELECT * FROM documents WHERE id IN ({placeholders})",
        req.document_ids
    ).fetchall()

    if not docs:
        raise HTTPException(status_code=404, detail="No documents found")

    # Combine document text
    documents_text = "\n\n".join([
        f"=== {doc['filename']} ===\n{doc['content']}"
        for doc in docs
    ])

    # Mask PII in documents before sending to Bedrock
    # This prevents the AWS Guardrail from blocking on input PII
    from backend.services.guardrail_service import detect_pii
    pii_flags_docs, documents_text_safe = detect_pii(documents_text)

    # Create memory record
    memory = create_memory(req.user_id)
    memory_id = memory["id"]

    # Link documents to memory
    for doc_id in req.document_ids:
        db.execute(
            "UPDATE documents SET memory_id = ? WHERE id = ?",
            (memory_id, doc_id)
        )
    db.commit()

    # Log user request
    log_action(db, memory_id, req.user_id, "USER_REQUEST", details={
        "document_count": len(docs),
        "documents": [doc["filename"] for doc in docs]
    })

    # AI Analysis
    try:
        analysis = analyze_documents(documents_text_safe)
    except GuardrailBlockedException as e:
        # AWS Bedrock Guardrail blocked the content
        analysis = {
            "change_type": "BLOCKED",
            "confidence": 0,
            "detection_reasons": ["AWS Bedrock Guardrail blocked this content"],
            "reasoning": {
                "what_changed": "Content blocked by AWS Bedrock Guardrail",
                "guardrail_message": str(e),
            }
        }
        # Force BLOCKED status
        update_memory(memory_id, status="BLOCKED", risk_level="BLOCKED",
                      change_type="BLOCKED", confidence=0,
                      detection_reasons=["AWS Bedrock Guardrail blocked this content"],
                      reasoning=analysis["reasoning"],
                      guardrail_flags=[{
                          "type": "aws_guardrail_block",
                          "severity": "blocked",
                          "message": f"AWS Bedrock Guardrail: {str(e)}",
                          "field": "content"
                      }])
        log_action(db, memory_id, None, "BLOCKED", risk_level="BLOCKED",
                   details={"reason": str(e), "source": "AWS Bedrock Guardrail"})
        db.close()
        return get_memory(memory_id)
    except Exception as e:
        # Other errors
        print(f"[ERROR] Bedrock analysis failed: {e}")
        analysis = {
            "change_type": "Unknown",
            "confidence": 0,
            "detection_reasons": [f"AI analysis failed: {str(e)}"],
            "reasoning": {
                "what_changed": "Analysis could not be completed. Please try again.",
                "error": str(e)
            }
        }

    # Extract AI results
    change_type = analysis.get("change_type", "Unknown")
    confidence = analysis.get("confidence", 0)
    detection_reasons = analysis.get("detection_reasons", [])
    reasoning = analysis.get("reasoning", {})

    # Duplicate detection - check if similar memory already exists
    existing = db.execute(
        "SELECT id, change_type, status, confidence, approved_by FROM memories WHERE change_type = ? AND id != ?",
        (change_type, memory_id)
    ).fetchall()
    duplicate_warning = None
    if existing:
        existing_list = [dict(row) for row in existing]
        duplicate_warning = {
            "exists": True,
            "count": len(existing_list),
            "memories": existing_list,
            "message": f"A memory for '{change_type}' already exists ({len(existing_list)} record{'s' if len(existing_list) > 1 else ''}). You may want to update the existing memory instead of creating a new one."
        }

    # Missing info detection
    try:
        missing_result = detect_missing_info(reasoning, change_type)
        missing_info = [item["message"] for item in missing_result.get("missing_items", [])]
    except Exception:
        missing_info = ["⚠ Could not perform completeness analysis"]

    # Guardrail checks
    try:
        guardrail_result = run_guardrails(reasoning, documents_text_safe, confidence)
        # If PII was detected, use the redacted/cleaned reasoning instead
        if guardrail_result.get("has_pii") and guardrail_result.get("cleaned_reasoning"):
            reasoning = guardrail_result["cleaned_reasoning"]
    except Exception:
        guardrail_result = {"flags": [], "overall_safe": True, "should_block": False}

    # Risk assessment
    risk_level = assess_risk(confidence, len(missing_info), guardrail_result)

    # Combine document PII flags with guardrail flags
    all_guardrail_flags = pii_flags_docs + guardrail_result.get("flags", [])

    # Update memory with all results
    status = "BLOCKED" if risk_level == "BLOCKED" else "DRAFT"
    update_memory(
        memory_id,
        change_type=change_type,
        confidence=confidence,
        detection_reasons=detection_reasons,
        reasoning=reasoning,
        missing_info=missing_info,
        risk_level=risk_level,
        guardrail_flags=all_guardrail_flags,
        status=status,
    )

    # Log AI draft
    log_action(db, memory_id, None, "AI_DRAFT", risk_level=risk_level, details={
        "change_type": change_type,
        "confidence": confidence,
        "guardrail_flags_count": len(guardrail_result.get("flags", [])),
        "missing_info_count": len(missing_info),
    }, ai_output=json.dumps(analysis))

    # Log guardrail flags if any
    if guardrail_result.get("flags"):
        log_action(db, memory_id, None, "GUARDRAIL_FLAG", details={
            "flags": guardrail_result["flags"]
        })

    if status == "BLOCKED":
        log_action(db, memory_id, None, "BLOCKED", details={
            "reason": "Content blocked by guardrail checks"
        })

    # Create initial snapshot
    create_snapshot(memory_id, "INITIAL_DRAFT")

    db.close()

    result = get_memory(memory_id)
    if duplicate_warning:
        result["duplicate_warning"] = duplicate_warning
    return result


@router.get("")
def get_memories(status: str = None):
    """List all memories."""
    return {"memories": list_memories(status)}


@router.get("/{memory_id}")
def get_memory_by_id(memory_id: str):
    """Get a single memory record."""
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.patch("/{memory_id}/approve")
def approve(memory_id: str, req: ApproveRequest):
    """Approve a memory record (role-gated)."""
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory["status"] not in ("DRAFT", "PENDING_REVIEW"):
        raise HTTPException(status_code=400, detail=f"Cannot approve memory in '{memory['status']}' status")

    # Check permission
    permission = check_approval_permission(req.user_id, memory["risk_level"])
    if not permission["allowed"]:
        raise HTTPException(status_code=403, detail=permission["reason"])

    # Create pre-approval snapshot
    create_snapshot(memory_id, "PRE_APPROVAL")

    # Approve
    result = approve_memory(memory_id, req.user_id)

    # Log
    db = get_db()
    log_action(db, memory_id, req.user_id, "APPROVED", risk_level=memory["risk_level"],
               human_decision="Approved reasoning record")
    db.close()

    return result


@router.patch("/{memory_id}/reject")
def reject(memory_id: str, req: RejectRequest):
    """Reject a memory record."""
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    result = reject_memory(memory_id, req.user_id)

    db = get_db()
    log_action(db, memory_id, req.user_id, "REJECTED",
               human_decision=f"Rejected: {req.reason}")
    db.close()

    return result


@router.patch("/{memory_id}/edit")
def edit_reasoning(memory_id: str, req: EditReasoningRequest):
    """Edit reasoning record."""
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Create snapshot before edit
    create_snapshot(memory_id, "PRE_EDIT")

    result = update_memory(memory_id, reasoning=req.reasoning)

    db = get_db()
    log_action(db, memory_id, req.user_id, "EDITED",
               human_decision="Reasoning record edited",
               details={"updated_reasoning": True})
    db.close()

    return result


@router.post("/{memory_id}/rollback")
def rollback(memory_id: str, req: RollbackRequest):
    """Rollback an approved memory (admin only)."""
    # Check admin permission
    permission = check_approval_permission(req.user_id, "HIGH")
    if not permission["allowed"]:
        raise HTTPException(status_code=403, detail="Only admins can rollback memories.")

    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory["status"] != "VERIFIED":
        raise HTTPException(status_code=400, detail="Can only rollback verified memories")

    result = rollback_memory(memory_id, req.user_id, req.reason)

    db = get_db()
    log_action(db, memory_id, req.user_id, "ROLLED_BACK",
               human_decision=f"Rolled back: {req.reason}",
               details={"reason": req.reason})
    db.close()

    return result


@router.get("/{memory_id}/snapshots")
def get_memory_snapshots(memory_id: str):
    """Get all snapshots for a memory."""
    return {"snapshots": get_snapshots(memory_id)}


class SubmitForReviewRequest(PydanticBaseModel):
    user_id: str
    reviewer_id: str


class SendReminderRequest(PydanticBaseModel):
    user_id: str


@router.patch("/{memory_id}/submit-for-review")
def submit_for_review(memory_id: str, req: SubmitForReviewRequest):
    """Submit a memory for review - assigns a reviewer and changes status."""
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory["status"] != "DRAFT":
        raise HTTPException(status_code=400, detail="Can only submit DRAFT memories for review")

    now = datetime.utcnow().isoformat()
    result = update_memory(
        memory_id,
        status="PENDING_REVIEW",
        assigned_reviewer=req.reviewer_id,
        submitted_at=now,
    )

    db = get_db()
    log_action(db, memory_id, req.user_id, "HUMAN_REVIEW",
               human_decision=f"Submitted for review to {req.reviewer_id}",
               details={"assigned_reviewer": req.reviewer_id})
    db.close()

    return result


@router.patch("/{memory_id}/discard")
def discard_memory(memory_id: str, req: ApproveRequest):
    """Discard a memory (contributor decides not to submit)."""
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    result = update_memory(memory_id, status="DISCARDED")

    db = get_db()
    log_action(db, memory_id, req.user_id, "REJECTED",
               human_decision="Discarded by contributor")
    db.close()

    return result


@router.post("/{memory_id}/send-reminder")
def send_reminder(memory_id: str, req: SendReminderRequest):
    """Send a reminder to the assigned reviewer."""
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory["status"] != "PENDING_REVIEW":
        raise HTTPException(status_code=400, detail="Memory is not pending review")

    # In a real app this would send an email/notification
    # For demo, just log it
    db = get_db()
    log_action(db, memory_id, req.user_id, "USER_REQUEST",
               human_decision="Sent reminder to reviewer",
               details={"action": "reminder_sent", "reviewer": memory.get("assigned_reviewer")})
    db.close()

    return {"status": "reminder_sent", "reviewer_id": memory.get("assigned_reviewer")}


@router.post("/{memory_id}/merge")
def merge_memory(memory_id: str, req: dict):
    """Merge documents from a source memory into this memory and re-analyze.

    Used when duplicate is detected: moves docs from the new (duplicate) memory
    into the existing one, deletes the duplicate, and re-analyzes.
    """
    source_memory_id = req.get("source_memory_id")
    user_id = req.get("user_id")

    if not source_memory_id or not user_id:
        raise HTTPException(status_code=400, detail="source_memory_id and user_id required")

    target = get_memory(memory_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target memory not found")

    db = get_db()

    # Move documents from source memory to target memory
    docs_moved = db.execute(
        "UPDATE documents SET memory_id = ? WHERE memory_id = ?",
        (memory_id, source_memory_id)
    ).rowcount
    db.commit()

    # Delete the source (duplicate) memory
    db.execute("DELETE FROM action_log WHERE memory_id = ?", (source_memory_id,))
    db.execute("DELETE FROM chat_messages WHERE memory_id = ?", (source_memory_id,))
    db.execute("DELETE FROM memory_snapshots WHERE memory_id = ?", (source_memory_id,))
    db.execute("DELETE FROM memories WHERE id = ?", (source_memory_id,))
    db.commit()

    # Get ALL documents now attached to target memory
    all_docs = db.execute(
        "SELECT * FROM documents WHERE memory_id = ?", (memory_id,)
    ).fetchall()

    # Combine all document text
    documents_text = "\n\n".join([
        f"=== {doc['filename']} ===\n{doc['content']}"
        for doc in all_docs
    ])

    # Mask PII
    from backend.services.guardrail_service import detect_pii
    _, documents_text_safe = detect_pii(documents_text)

    # Create snapshot before update
    create_snapshot(memory_id, "PRE_MERGE_UPDATE")

    # Re-analyze with all documents
    try:
        analysis = analyze_documents(documents_text_safe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Re-analysis failed: {str(e)}")

    # Update memory
    change_type = analysis.get("change_type", target.get("change_type", "Unknown"))
    confidence = analysis.get("confidence", 0)
    reasoning = analysis.get("reasoning", {})

    try:
        missing_result = detect_missing_info(reasoning, change_type)
        missing_info = [item["message"] for item in missing_result.get("missing_items", [])]
    except Exception:
        missing_info = []

    update_memory(
        memory_id,
        change_type=change_type,
        confidence=confidence,
        detection_reasons=analysis.get("detection_reasons", []),
        reasoning=reasoning,
        missing_info=missing_info,
        status="DRAFT",
        approved_by=None,
        approved_at=None,
    )

    # Log
    log_action(db, memory_id, user_id, "EDITED", details={
        "action": "merged_from_duplicate",
        "source_memory_deleted": source_memory_id,
        "documents_moved": docs_moved,
        "total_documents": len(all_docs),
    }, human_decision="Merged new documents into existing memory")

    # Remove from FTS
    try:
        db.execute("DELETE FROM memory_fts WHERE memory_id = ?", (memory_id,))
    except Exception:
        pass

    db.commit()
    db.close()

    return get_memory(memory_id)


@router.post("/{memory_id}/add-documents")
def add_documents_to_memory(memory_id: str, req: GenerateMemoryRequest):
    """Add new documents to an existing memory and re-analyze.

    This allows updating a verified memory with new evidence.
    The memory goes back to DRAFT status for re-review.
    """
    memory = get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    db = get_db()

    # Get new documents
    placeholders = ",".join("?" * len(req.document_ids))
    new_docs = db.execute(
        f"SELECT * FROM documents WHERE id IN ({placeholders})",
        req.document_ids
    ).fetchall()

    if not new_docs:
        raise HTTPException(status_code=404, detail="No new documents found")

    # Link new documents to memory
    for doc_id in req.document_ids:
        db.execute("UPDATE documents SET memory_id = ? WHERE id = ?", (memory_id, doc_id))
    db.commit()

    # Get ALL documents for this memory (old + new)
    all_docs = db.execute(
        "SELECT * FROM documents WHERE memory_id = ?", (memory_id,)
    ).fetchall()

    # Combine all document text
    documents_text = "\n\n".join([
        f"=== {doc['filename']} ===\n{doc['content']}"
        for doc in all_docs
    ])

    # Mask PII
    from backend.services.guardrail_service import detect_pii
    pii_flags_docs, documents_text_safe = detect_pii(documents_text)

    # Create snapshot before update
    create_snapshot(memory_id, "PRE_UPDATE")

    # Re-analyze with all documents
    try:
        analysis = analyze_documents(documents_text_safe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Update memory with new analysis, reset to DRAFT
    change_type = analysis.get("change_type", memory.get("change_type", "Unknown"))
    confidence = analysis.get("confidence", 0)
    reasoning = analysis.get("reasoning", {})

    # Missing info
    try:
        missing_result = detect_missing_info(reasoning, change_type)
        missing_info = [item["message"] for item in missing_result.get("missing_items", [])]
    except Exception:
        missing_info = []

    update_memory(
        memory_id,
        change_type=change_type,
        confidence=confidence,
        detection_reasons=analysis.get("detection_reasons", []),
        reasoning=reasoning,
        missing_info=missing_info,
        status="DRAFT",
        approved_by=None,
        approved_at=None,
    )

    # Log the update
    log_action(db, memory_id, req.user_id, "EDITED", details={
        "action": "new_documents_added",
        "new_document_count": len(new_docs),
        "total_document_count": len(all_docs),
        "documents_added": [doc["filename"] for doc in new_docs],
    }, human_decision="Added new documents and re-analyzed")

    # Remove from FTS (needs re-approval to be queryable again)
    try:
        db.execute("DELETE FROM memory_fts WHERE memory_id = ?", (memory_id,))
    except Exception:
        pass

    db.commit()
    db.close()

    return get_memory(memory_id)


def log_action(db, memory_id, user_id, action, risk_level=None, details=None, ai_output=None, human_decision=None):
    """Log an action to the audit trail."""
    db.execute(
        """INSERT INTO action_log (id, memory_id, user_id, action, risk_level, details, ai_output, human_decision, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (str(uuid.uuid4()), memory_id, user_id, action, risk_level,
         json.dumps(details) if details else "{}", ai_output, human_decision,
         datetime.utcnow().isoformat())
    )
    db.commit()


def get_demo_analysis():
    """Fallback demo analysis when Bedrock is unavailable."""
    return {
        "change_type": "Authentication",
        "confidence": 96,
        "detection_reasons": [
            "Passkeys implementation discussed",
            "MFA migration referenced",
            "Authentication APIs mentioned",
            "Security Review conducted"
        ],
        "reasoning": {
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
                {"document": "ArchitectureDecision.pdf", "supports": "Technical implementation details and WebAuthn standard"},
                {"document": "MeetingNotes.pdf", "supports": "Team consensus and timeline agreement"},
                {"document": "RiskAssessment.pdf", "supports": "Identified risks and mitigation strategies"},
                {"document": "ApprovalEmail.pdf", "supports": "Executive sign-off and budget approval"}
            ],
            "decision_makers": ["CISO Sarah Chen", "VP Engineering Marcus Johnson", "Security Team Lead"],
            "timeline": "Q1 2026: Pilot (1000 users) → Q2 2026: Full rollout → Q3 2026: Password deprecation",
            "additional_context": "Part of broader Zero Trust initiative. Budget approved: $2.3M over 18 months."
        }
    }
