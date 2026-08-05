"""Document models."""
from pydantic import BaseModel
from typing import Optional


class Document(BaseModel):
    id: str
    memory_id: Optional[str] = None
    filename: str
    file_type: str
    content: str
    uploaded_at: Optional[str] = None
