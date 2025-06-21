from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.projects import ProjectCreate, ProjectRead, ProjectUpdate, ProjectList
from app.schemas.documents import DocumentList
from app.services.projects import project_service
from app.db.base import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectRead)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建项目"""
    return project_service.create_project(db, current_user.id, project)

@router.get("/", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目列表"""
    return project_service.list_projects(db, current_user.id, page, per_page)

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目详情"""
    project = project_service.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新项目"""
    project = project_service.update_project(db, project_id, current_user.id, project_update)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除项目"""
    print(f"[DEBUG] 删除项目请求:")
    print(f"[DEBUG] - project_id: {project_id}")
    print(f"[DEBUG] - user_id: {current_user.id}")
    
    success = project_service.delete_project(db, project_id, current_user.id)
    print(f"[DEBUG] 删除结果: {success}")
    
    if not success:
        print(f"[DEBUG] 项目删除失败 - 项目不存在或无权限")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    print(f"[DEBUG] 项目删除成功")
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/documents/{document_id}")
async def add_document_to_project(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """将文档添加到项目"""
    project_service.add_document_to_project(db, project_id, document_id, current_user.id)
    return {"message": "Document added to project successfully"}

@router.delete("/{project_id}/documents/{document_id}")
async def remove_document_from_project(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """从项目中移除文档"""
    project_service.remove_document_from_project(db, project_id, document_id, current_user.id)
    return {"message": "Document removed from project successfully"}

@router.get("/{project_id}/documents", response_model=DocumentList)
async def get_project_documents(
    project_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目下的文档列表"""
    print(f"[DEBUG] 获取项目文档请求:")
    print(f"[DEBUG] - project_id: {project_id}")
    print(f"[DEBUG] - user_id: {current_user.id}")
    print(f"[DEBUG] - page: {page}, per_page: {per_page}")
    
    result = project_service.get_project_documents(db, project_id, current_user.id, page, per_page)
    
    print(f"[DEBUG] 获取项目文档结果:")
    print(f"[DEBUG] - 文档数量: {len(result.documents)}")
    print(f"[DEBUG] - 总数: {result.total}")
    if result.documents:
        for i, doc in enumerate(result.documents):
            print(f"[DEBUG] - 文档{i+1}: {doc.id} - {doc.filename} - project_id: {doc.project_id}")
    
    return result
