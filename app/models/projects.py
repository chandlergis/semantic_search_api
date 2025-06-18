from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ProjectDocument(Base):
    __tablename__ = "project_documents"

    project_id = Column(String, ForeignKey('projects.id', ondelete="CASCADE"), primary_key=True)
    document_id = Column(String, ForeignKey('documents.id', ondelete="CASCADE"), primary_key=True)
