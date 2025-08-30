from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 搜索请求
class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 10
    top_k_chunks: Optional[int] = 10
    bm25_weight: Optional[float] = 0.6
    tfidf_weight: Optional[float] = 0.4
    project_id: Optional[str] = None  # 限制在特定项目内搜索

class SearchByFile(BaseModel):
    top_k: Optional[int] = 10
    top_k_chunks: Optional[int] = 10
    bm25_weight: Optional[float] = 0.6
    tfidf_weight: Optional[float] = 0.4
    project_id: Optional[str] = None

# chunk搜索结果
class ChunkSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    chunk_index: int
    bm25_score: float
    tfidf_score: float
    final_score: float

# 文档搜索结果（聚合chunk结果）
class DocumentSearchResult(BaseModel):
    document_id: str
    document_title: str
    file_type: str
    max_score: float
    avg_score: float
    matched_chunks_count: int
    top_chunks: List[ChunkSearchResult]

# 搜索响应
class SearchResponse(BaseModel):
    query: str
    total_chunks: int
    total_documents: int
    chunks: List[ChunkSearchResult]
    documents: List[DocumentSearchResult]
    search_time_ms: float
    message: Optional[str] = None

# 相似文档匹配（保留原有功能）
class MatchResult(BaseModel):
    query_document_id: str
    matched_document_id: str
    similarity_score: float
    created_at: datetime

# 废弃的SearchResult（保留兼容性）
class SearchResult(BaseModel):
    id: str
    score: float
    content: str
