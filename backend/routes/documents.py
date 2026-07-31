"""Document upload routes."""
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File
from typing import List

from backend.database.connection import get_db, dict_from_row
from backend.services.document_service import extract_text
from backend.services.guardrail_service import detect_pii
from backend.services.s3_service import upload_to_s3, generate_presigned_url

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents: extract text, scan PII, store original in S3."""
    db = get_db()
    uploaded = []
    pii_warnings = []

    for file in files:
        content = await file.read()
        text = extract_text(file.filename, content)
        file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"

        # Upload original file to S3
        s3_key = upload_to_s3(content, file.filename)

        # Scan for PII in extracted text
        flags, redacted_text = detect_pii(text)
        if flags:
            pii_warnings.append({
                "filename": file.filename,
                "issues": [f["message"] for f in flags],
                "redacted": True
            })
            text = redacted_text

        # Save to DB
        doc_id = str(uuid.uuid4())
        db.execute(
            """INSERT INTO documents (id, memory_id, filename, file_type, content, s3_key, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (doc_id, None, file.filename, file_type, text, s3_key, datetime.utcnow().isoformat())
        )
        db.commit()
        uploaded.append({"id": doc_id, "filename": file.filename, "file_type": file_type, "s3_key": s3_key})

    db.close()

    result = {"documents": uploaded, "count": len(uploaded)}
    if pii_warnings:
        result["pii_warnings"] = pii_warnings
        result["message"] = f"PII detected and redacted in {len(pii_warnings)} document(s)."
    return result


@router.get("/{document_id}")
def get_document(document_id: str):
    """Get a single document with download URL."""
    db = get_db()
    row = db.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    db.close()
    if not row:
        return {"error": "Document not found"}, 404
    doc = dict_from_row(row)
    if doc.get("s3_key"):
        doc["download_url"] = generate_presigned_url(doc["s3_key"])
    return doc


@router.get("/memory/{memory_id}")
def get_documents_by_memory(memory_id: str):
    """Get all documents for a memory with download URLs."""
    db = get_db()
    rows = db.execute(
        "SELECT id, filename, file_type, s3_key, uploaded_at FROM documents WHERE memory_id = ?",
        (memory_id,)
    ).fetchall()
    db.close()
    docs = [dict_from_row(r) for r in rows]
    # Add download URLs
    for doc in docs:
        if doc.get("s3_key"):
            doc["download_url"] = generate_presigned_url(doc["s3_key"])
    return {"documents": docs}
