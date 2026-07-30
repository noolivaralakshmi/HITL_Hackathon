"""Document upload routes."""
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from backend.database.connection import get_db, dict_from_row
from backend.services.document_service import extract_text, save_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents and extract text content."""
    db = get_db()
    uploaded = []

    for file in files:
        content = await file.read()
        text = extract_text(file.filename, content)
        file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"

        doc = save_document(db, file.filename, file_type, text)
        uploaded.append(doc)

    db.close()
    return {"documents": uploaded, "count": len(uploaded)}


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
