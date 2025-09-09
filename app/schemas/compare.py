from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class DocumentInfo(BaseModel):
    """文档信息模型"""
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="文档内容")
    html_content: str = Field(..., description="带高亮的HTML内容")
    chunks_count: int = Field(..., description="分块数量")

class MatchLink(BaseModel):
    """匹配链接模型"""
    chunk_a_id: str = Field(..., description="文档A块ID")
    chunk_b_id: str = Field(..., description="文档B块ID")
    similarity: float = Field(..., ge=0, le=1, description="相似度分数")
    match_type: str = Field(..., description="匹配类型: high, medium, low")
    link_id: str = Field(..., description="链接ID，用于前端同步滚动")

class ComparisonResult(BaseModel):
    """比较结果模型"""
    overall_similarity: float = Field(..., ge=0, le=1, description="整体相似度")
    total_matches: int = Field(..., ge=0, description="总匹配数量")
    high_similarity_matches: int = Field(..., ge=0, description="高相似度匹配数量")
    medium_similarity_matches: int = Field(..., ge=0, description="中等相似度匹配数量")
    match_links: List[MatchLink] = Field(default=[], description="匹配链接列表")

class AlgorithmParams(BaseModel):
    """算法参数模型"""
    similarity_threshold_high: float = Field(default=0.9, description="高相似度阈值")
    similarity_threshold_medium: float = Field(default=0.7, description="中等相似度阈值")
    chunk_size: int = Field(default=300, description="文本分块大小")

class ComparisonMetadata(BaseModel):
    """比较元数据模型"""
    display_mode: str = Field(default='pdf', description="前端显示模式: pdf或html")
    comparison_time: Optional[datetime] = Field(None, description="比较时间")
    algorithm_params: AlgorithmParams = Field(..., description="算法参数")
    highlighted_files: Optional[Dict[str, str]] = Field(default=None, description="高亮文件信息")

class CompareResponse(BaseModel):
    """文档比较响应模型"""
    document_a: DocumentInfo = Field(..., description="文档A信息")
    document_b: DocumentInfo = Field(..., description="文档B信息")
    comparison: ComparisonResult = Field(..., description="比较结果")
    metadata: ComparisonMetadata = Field(..., description="元数据")

class CompareRequest(BaseModel):
    """文档比较请求模型 (用于文本直接比较)"""
    text_a: str = Field(..., description="文档A内容")
    text_b: str = Field(..., description="文档B内容")
    filename_a: str = Field(default="Document A", description="文档A文件名")
    filename_b: str = Field(default="Document B", description="文档B文件名")
    similarity_threshold_high: Optional[float] = Field(default=0.9, ge=0, le=1, description="高相似度阈值")
    similarity_threshold_medium: Optional[float] = Field(default=0.7, ge=0, le=1, description="中等相似度阈值")
    chunk_size: Optional[int] = Field(default=300, ge=50, le=1000, description="文本分块大小")

class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    filename: str = Field(..., description="文件名")
    file_id: str = Field(..., description="文件ID")
    content_preview: str = Field(..., description="内容预览")
    file_size: int = Field(..., description="文件大小")
    upload_time: datetime = Field(..., description="上传时间")

class CompareFilesRequest(BaseModel):
    """文件比较请求模型"""
    file_a_id: str = Field(..., description="文档A的文件ID")
    file_b_id: str = Field(..., description="文档B的文件ID")
    similarity_threshold_high: Optional[float] = Field(default=0.9, ge=0, le=1, description="高相似度阈值")
    similarity_threshold_medium: Optional[float] = Field(default=0.7, ge=0, le=1, description="中等相似度阈值")
    chunk_size: Optional[int] = Field(default=300, ge=50, le=1000, description="文本分块大小")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误信息")
    code: Optional[str] = Field(None, description="错误代码")

class SuccessResponse(BaseModel):
    """成功响应模型"""
    message: str = Field(..., description="成功信息")
    data: Optional[Any] = Field(None, description="返回数据")