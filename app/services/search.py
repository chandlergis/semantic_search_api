import time
import logging
from typing import List, Dict, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import UploadFile

from app.models.documents import Document, Chunk
from app.schemas.search import (
    SearchQuery, SearchByFile, SearchResponse, 
    ChunkSearchResult, DocumentSearchResult
)
from app.utils.hybrid_search import search_engine
from app.utils.document_parser import document_parser

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self._index_built = False
        self._last_index_update = 0
    
    def _ensure_index_updated(self, db: Session, user_id: str, project_id: Optional[str] = None):
        """确保搜索索引是最新的"""
        try:
            # 获取用户的所有chunks
            query = db.query(
                Chunk.id,
                Chunk.content,
                Chunk.document_id,
                Document.title.label('document_title')
            ).join(Document, Chunk.document_id == Document.id).filter(
                Document.owner_id == user_id,
                Document.status == 'COMPLETED'
            )
            
            # 如果指定了项目，只搜索该项目下的文档
            if project_id:
                query = query.filter(Document.project_id == project_id)
            
            chunks_data = []
            for chunk_id, content, doc_id, doc_title in query.all():
                chunks_data.append({
                    'id': chunk_id,
                    'content': content,
                    'document_id': doc_id,
                    'document_title': doc_title or 'Untitled'
                })
            
            logger.info(f"为用户 {user_id} 构建搜索索引，共 {len(chunks_data)} 个chunks")
            
            # 构建索引
            search_engine.build_index(chunks_data)
            self._index_built = True
            self._last_index_update = time.time()
            
        except Exception as e:
            logger.error(f"构建搜索索引失败: {e}")
            raise
    
    def search_by_text(self, db: Session, user_id: str, query: SearchQuery, project_id: Optional[str] = None) -> SearchResponse:
        # 如果指定了项目，检查该项目下是否有文档
        if project_id:
            from app.models.documents import Document
            doc_count = db.query(Document).filter(
                Document.project_id == project_id,
                Document.owner_id == user_id,
                Document.status == 'COMPLETED'
            ).count()
            if doc_count == 0:
                return SearchResponse(
                    query=query.query,
                    total_chunks=0,
                    total_documents=0,
                    chunks=[],
                    documents=[],
                    search_time_ms=0,
                    message=f"项目 {project_id} 下没有可搜索的文档"
                )
        """根据文本查询搜索文档，支持按项目过滤"""
        start_time = time.time()
        
        try:
            # 更新搜索索引
            self._ensure_index_updated(db, user_id, project_id)
            
            # 更新搜索引擎权重
            search_engine.bm25_weight = query.bm25_weight
            search_engine.tfidf_weight = query.tfidf_weight
            
            # 执行搜索
            raw_results = search_engine.search(query.query, query.top_k)
            
            # 转换结果格式
            chunks = [
                ChunkSearchResult(
                    chunk_id=result['chunk_id'],
                    document_id=result['document_id'],
                    document_title=result['document_title'],
                    content=result['content'],
                    chunk_index=0,  # TODO: 从数据库获取
                    bm25_score=result['bm25_score'],
                    tfidf_score=result['tfidf_score'],
                    final_score=result['final_score']
                )
                for result in raw_results
            ]
            
            # 按文档聚合结果
            documents = self._aggregate_results_by_document(chunks)
            
            search_time = (time.time() - start_time) * 1000
            
            return SearchResponse(
                query=query.query,
                total_chunks=len(chunks),
                total_documents=len(documents),
                chunks=chunks,
                documents=documents,
                search_time_ms=search_time
            )
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    async def search_by_file(self, db: Session, user_id: str, file: UploadFile, search_params: SearchByFile) -> SearchResponse:
        """根据上传文件搜索相似文档"""
        start_time = time.time()
        
        try:
            # 解析上传的文件
            file_content = await file.read()
            query_text = await document_parser.convert_upload_to_markdown(
                file_content, file.filename
            )
            
            if not query_text or len(query_text.strip()) < 10:
                raise ValueError("上传文件解析失败或内容过少")
            
            logger.info(f"解析上传文件成功，内容长度: {len(query_text)}")
            
            # 更新搜索索引
            self._ensure_index_updated(db, user_id, search_params.project_id)
            
            # 更新搜索引擎权重
            search_engine.bm25_weight = search_params.bm25_weight
            search_engine.tfidf_weight = search_params.tfidf_weight
            
            # 执行搜索
            raw_results = search_engine.search(query_text, search_params.top_k)
            
            # 转换结果格式
            chunks = [
                ChunkSearchResult(
                    chunk_id=result['chunk_id'],
                    document_id=result['document_id'],
                    document_title=result['document_title'],
                    content=result['content'],
                    chunk_index=0,
                    bm25_score=result['bm25_score'],
                    tfidf_score=result['tfidf_score'],
                    final_score=result['final_score']
                )
                for result in raw_results
            ]
            
            # 按文档聚合结果
            documents = self._aggregate_results_by_document(chunks)
            
            search_time = (time.time() - start_time) * 1000
            
            return SearchResponse(
                query=f"文件搜索: {file.filename}",
                total_chunks=len(chunks),
                total_documents=len(documents),
                chunks=chunks,
                documents=documents,
                search_time_ms=search_time
            )
            
        except Exception as e:
            logger.error(f"文件搜索失败: {e}")
            raise
    
    def _aggregate_results_by_document(self, chunks: List[ChunkSearchResult]) -> List[DocumentSearchResult]:
        """按文档聚合chunk搜索结果"""
        doc_groups = defaultdict(list)
        
        # 按文档ID分组
        for chunk in chunks:
            doc_groups[chunk.document_id].append(chunk)
        
        documents = []
        for doc_id, doc_chunks in doc_groups.items():
            if not doc_chunks:
                continue
            
            # 计算文档级别的分数
            scores = [chunk.final_score for chunk in doc_chunks]
            max_score = max(scores)
            avg_score = sum(scores) / len(scores)
            
            # 取前3个最相似的chunks
            top_chunks = sorted(doc_chunks, key=lambda x: x.final_score, reverse=True)[:3]
            
            # 获取文档信息
            first_chunk = doc_chunks[0]
            
            documents.append(DocumentSearchResult(
                document_id=doc_id,
                document_title=first_chunk.document_title,
                file_type="Unknown",  # TODO: 从数据库获取
                max_score=max_score,
                avg_score=avg_score,
                matched_chunks_count=len(doc_chunks),
                top_chunks=top_chunks
            ))
        
        # 按最高分数排序
        documents.sort(key=lambda x: x.max_score, reverse=True)
        
        return documents
    
    def rebuild_index(self, db: Session, user_id: str):
        """重新构建用户的搜索索引"""
        logger.info(f"手动重建用户 {user_id} 的搜索索引")
        self._ensure_index_updated(db, user_id)
        return {"message": "搜索索引重建成功"}

search_service = SearchService()
