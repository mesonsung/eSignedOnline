from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    SIGNED = "signed"

class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    status: DocumentStatus = DocumentStatus.UPLOADED

class DocumentCreate(DocumentBase):
    uploaded_by: str

class DocumentSign(BaseModel):
    document_id: str
    signed_by: str
    signature_data: str  # Base64 encoded signature image

class DocumentInDB(DocumentBase):
    id: Optional[str] = None
    uploaded_by: str
    signed_by: Optional[str] = None
    signed_filename: Optional[str] = None
    signed_file_path: Optional[str] = None
    signature_data: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Document(DocumentBase):
    id: Optional[str] = None
    uploaded_by: str
    signed_by: Optional[str] = None
    signed_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime
