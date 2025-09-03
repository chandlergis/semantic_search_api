from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, Form, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.search import SearchQuery, SearchByFile, SearchResponse
from app.services.search import search_service
from app.db.base import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/search", tags=["search"])

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "deepseek"

@router.post("/text", response_model=SearchResponse)
async def search_by_text(
    query: SearchQuery = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """文本搜索接口"""
    try:
        return search_service.search_by_text(
            db, 
            current_user.id, 
            query,
            project_id=query.project_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )

@router.post("/file", response_model=SearchResponse)
async def search_by_file(
    file: UploadFile,
    top_k: Optional[int] = Form(10),
    bm25_weight: Optional[float] = Form(0.6),
    tfidf_weight: Optional[float] = Form(0.4),
    project_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """文件搜索接口"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供文件"
        )
    
    search_params = SearchByFile(
        top_k=top_k,
        bm25_weight=bm25_weight,
        tfidf_weight=tfidf_weight,
        project_id=project_id
    )
    
    try:
        return await search_service.search_by_file(db, current_user.id, file, search_params)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件搜索失败: {str(e)}"
        )

@router.post("/rebuild-index")
async def rebuild_search_index(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """重建搜索索引"""
    try:
        return search_service.rebuild_index(db, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重建索引失败: {str(e)}"
        )

@router.get("/status")
async def get_search_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取搜索系统状态"""
    try:
        # 统计用户的文档和chunk数量
        from app.models.documents import Document, Chunk
        
        total_documents = db.query(Document).filter(
            Document.owner_id == current_user.id,
            Document.status == 'COMPLETED'
        ).count()
        
        total_chunks = db.query(Chunk).join(
            Document, Chunk.document_id == Document.id
        ).filter(
            Document.owner_id == current_user.id,
            Document.status == 'COMPLETED'
        ).count()
        
        return {
            "user_id": current_user.id,
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "index_built": search_service._index_built,
            "last_index_update": search_service._last_index_update
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取状态失败: {str(e)}"
        )

@router.get("/models", response_model=List[ModelInfo])
async def get_models():
    """获取可用模型列表"""
    return [
        {"id": "deepseek-chat", "object": "model", "owned_by": "deepseek"},
        {"id": "deepseek-reasoner", "object": "model", "owned_by": "deepseek"}
    ]
