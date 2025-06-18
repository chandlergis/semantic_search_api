from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.db.base import Base

class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String, primary_key=True, index=True)
    query_document_id = Column(String, ForeignKey('documents.id', ondelete="SET NULL"))
    query_chunk_id = Column(String, ForeignKey('chunks.id', ondelete="SET NULL"))
    matched_document_id = Column(String, ForeignKey('documents.id', ondelete="SET NULL"))
    matched_chunk_id = Column(String, ForeignKey('chunks.id', ondelete="SET NULL"))
    similarity_score = Column(Float)
    user_id = Column(String, ForeignKey('users.id', ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
