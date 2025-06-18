from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.documents import DocumentRead, DocumentList
from app.services.documents import document_service
from app.db.base import get_db
from app.services.users import user_service
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """上传文档"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    return await document_service.upload_and_process_document(
        db=db,
        file=file,
        user_id=current_user.id,
        project_id=project_id
    )

@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取文档详情"""
    document = document_service.get_document(db, document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.get("/{document_id}/error")
async def get_document_error(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取文档错误信息"""
    document = document_service.get_document_with_error(db, document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {"error_log": document.error_log, "status": document.status}

@router.get("/", response_model=DocumentList)
async def list_documents(
    project_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取文档列表"""
    return document_service.list_documents(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        page=page,
        per_page=per_page
    )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除文档"""
    success = document_service.delete_document(db, document_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {"message": "Document deleted successfully"}
