from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(ENUM('PDF', 'DOCX', 'PPTX', 'XLSX', 'HTML', 'TXT', 'CSV', 'JSON', 'XML', name='file_type'))
    file_size = Column(BigInteger)
    file_path = Column(String)
    title = Column(String)
    source_info = Column(JSONB)
    raw_content = Column(Text)
    processed_content = Column(Text)
    content_hash = Column(String)
    source_file_hash = Column(String)
    status = Column(ENUM('PENDING_PROCESS', 'PROCESSING', 'PENDING_CHUNK', 'SYNCING', 'COMPLETED', 'FAILED', name='document_status'))
    error_log = Column(Text)
    owner_id = Column(String, ForeignKey('users.id'))
    project_id = Column(String, ForeignKey('projects.id'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey('documents.id', ondelete="CASCADE"))
    content = Column(Text)
    chunk_index = Column(Integer)
    token_count = Column(Integer)
    vector_id = Column(String)
