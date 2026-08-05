"""Document text extraction service."""
import io
import uuid
from datetime import datetime


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF file."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"[Error extracting PDF: {str(e)}]"


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"[Error extracting DOCX: {str(e)}]"


def extract_text_from_txt(content: bytes) -> str:
    """Extract text from TXT file."""
    return content.decode("utf-8", errors="replace").strip()


def extract_text(filename: str, content: bytes) -> str:
    """Extract text from a file based on its extension."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        return extract_text_from_pdf(content)
    elif ext == "docx":
        return extract_text_from_docx(content)
    elif ext in ("txt", "md", "csv"):
        return extract_text_from_txt(content)
    else:
        return extract_text_from_txt(content)


def save_document(db, filename: str, file_type: str, content: str, memory_id: str = None) -> dict:
    """Save a document record to the database."""
    doc_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO documents (id, memory_id, filename, file_type, content, uploaded_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (doc_id, memory_id, filename, file_type, content, datetime.utcnow().isoformat())
    )
    db.commit()
    return {"id": doc_id, "filename": filename, "file_type": file_type}
