"""Document upload routes."""
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from backend.database.connection import get_db, dict_from_row
from backend.services.document_service import extract_text, save_document
from backend.services.guardrail_service import detect_pii

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents, extract text, scan for PII, and redact if found."""
    db = get_db()
    uploaded = []
    pii_warnings = []

    for file in files:
        content = await file.read()
        text = extract_text(file.filename, content)
        file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"

        # Scan for PII in document content
        flags, redacted_text = detect_pii(text)
        if flags:
            pii_warnings.append({
                "filename": file.filename,
                "issues": [f["message"] for f in flags],
                "redacted": True
            })
            # Store the redacted version — never store raw PII
            text = redacted_text

        doc = save_document(db, file.filename, file_type, text)
        uploaded.append(doc)

    db.close()

    result = {"documents": uploaded, "count": len(uploaded)}
    if pii_warnings:
        result["pii_warnings"] = pii_warnings
        result["message"] = f"PII detected and redacted in {len(pii_warnings)} document(s). Sensitive information has been removed."

    return result


@router.get("/{document_id}")
def get_document(document_id: str):
    """Get a single document."""
    db = get_db()
    row = db.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    db.close()
    if not row:
        return {"error": "Document not found"}, 404
    return dict_from_row(row)


@router.get("/memory/{memory_id}")
def get_documents_by_memory(memory_id: str):
    """Get all documents for a memory."""
    db = get_db()
    rows = db.execute(
        "SELECT id, filename, file_type, uploaded_at FROM documents WHERE memory_id = ?",
        (memory_id,)
    ).fetchall()
    db.close()
    return {"documents": [dict_from_row(r) for r in rows]}
