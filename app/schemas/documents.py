from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class DocumentStatus(str, Enum):
    PENDING_PROCESS = "PENDING_PROCESS"
    PROCESSING = "PROCESSING"
    PENDING_CHUNK = "PENDING_CHUNK"
    SYNCING = "SYNCING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class FileType(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    PPTX = "PPTX"
    XLSX = "XLSX"
    HTML = "HTML"
    TXT = "TXT"
    CSV = "CSV"
    JSON = "JSON"
    XML = "XML"

class DocumentBase(BaseModel):
    title: Optional[str] = None
    source_info: Optional[dict] = None

class DocumentCreate(DocumentBase):
    filename: str
    original_filename: str
    file_type: FileType
    file_size: int
    project_id: Optional[str] = None

class DocumentRead(DocumentBase):
    id: str
    filename: str
    original_filename: str
    file_type: FileType
    file_size: int
    status: DocumentStatus
    owner_id: str
    project_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    project_id: Optional[str] = None

class DocumentList(BaseModel):
    documents: list[DocumentRead]
    total: int
    page: int
    per_page: int
