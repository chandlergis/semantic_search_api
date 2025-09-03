from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectRead(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ProjectWithDocuments(ProjectRead):
    document_count: int

class ProjectList(BaseModel):
    projects: List[ProjectWithDocuments]
    total: int
    page: int
    per_page: int
