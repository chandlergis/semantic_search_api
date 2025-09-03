from uuid import uuid4
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.projects import Project, ProjectDocument
from app.models.documents import Document
from app.schemas.projects import ProjectCreate, ProjectRead, ProjectUpdate, ProjectWithDocuments, ProjectList

class ProjectService:
    def create_project(self, db: Session, user_id: str, project: ProjectCreate) -> ProjectRead:
        """创建项目"""
        # 检查同名项目
        existing_project = db.query(Project).filter(
            Project.name == project.name,
            Project.owner_id == user_id
        ).first()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project with this name already exists"
            )
        
        db_project = Project(
            id=str(uuid4()),
            name=project.name,
            description=project.description,
            owner_id=user_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return ProjectRead.from_orm(db_project)
    
    def get_project(self, db: Session, project_id: str, user_id: str) -> Optional[ProjectRead]:
        """获取项目详情"""
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if project:
            return ProjectRead.from_orm(project)
        return None
    
    def update_project(self, db: Session, project_id: str, user_id: str, project_update: ProjectUpdate) -> Optional[ProjectRead]:
        """更新项目"""
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if not project:
            return None
        
        # 检查名称是否重复
        if project_update.name and project_update.name != project.name:
            existing_project = db.query(Project).filter(
                Project.name == project_update.name,
                Project.owner_id == user_id,
                Project.id != project_id
            ).first()
            
            if existing_project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project with this name already exists"
                )
        
        # 更新字段
        if project_update.name is not None:
            project.name = project_update.name
        if project_update.description is not None:
            project.description = project_update.description
        
        db.commit()
        db.refresh(project)
        return ProjectRead.from_orm(project)
            
    def list_projects(self, db: Session, user_id: str, page: int = 1, per_page: int = 20) -> ProjectList:
        """获取项目列表"""
        # 获取项目和文档数量
        query = db.query(
            Project,
            func.count(Document.id).label('document_count')
        ).outerjoin(
            Document, Document.project_id == Project.id
        ).filter(
            Project.owner_id == user_id
        ).group_by(Project.id).order_by(Project.created_at.desc())
        
        total = query.count()
        projects_with_count = query.offset((page - 1) * per_page).limit(per_page).all()
        
        projects = []
        for project, document_count in projects_with_count:
            project_dict = ProjectRead.from_orm(project).dict()
            project_dict['document_count'] = document_count
            projects.append(ProjectWithDocuments(**project_dict))
        
        return ProjectList(
            projects=projects,
            total=total,
            page=page,
            per_page=per_page
        )
    
    def delete_project(self, db: Session, project_id: str, user_id: str) -> bool:
        """删除项目"""
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if project:
            # 将项目下的文档的project_id设为NULL
            db.query(Document).filter(
                Document.project_id == project_id
            ).update({Document.project_id: None})
            
            # 删除项目
            db.delete(project)
            db.commit()
            return True
        
        return False
    
    def add_document_to_project(self, db: Session, project_id: str, document_id: str, user_id: str) -> bool:
        """将文档添加到项目"""
        # 验证项目存在且属于用户
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # 验证文档存在且属于用户
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # 更新文档的project_id
        document.project_id = project_id
        db.commit()
        return True
    
    def remove_document_from_project(self, db: Session, project_id: str, document_id: str, user_id: str) -> bool:
        """从项目中移除文档"""
        # 验证项目存在且属于用户
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # 验证文档存在且属于该项目
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.project_id == project_id,
            Document.owner_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found in this project"
            )
        
        # 移除文档的project_id
        document.project_id = None
        db.commit()
        return True
    
    def get_project_documents(self, db: Session, project_id: str, user_id: str, page: int = 1, per_page: int = 20):
        """获取项目下的文档列表"""
        # 验证项目存在且属于用户
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # 获取项目下的文档
        query = db.query(Document).filter(
            Document.project_id == project_id,
            Document.owner_id == user_id
        ).order_by(Document.created_at.desc())
        
        total = query.count()
        documents = query.offset((page - 1) * per_page).limit(per_page).all()
        
        from app.schemas.documents import DocumentRead, DocumentList
        return DocumentList(
            documents=[DocumentRead.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            per_page=per_page
        )

project_service = ProjectService()
