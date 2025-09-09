import os
import uuid
import hashlib
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse, Response

from app.schemas.compare import (
    CompareRequest, CompareResponse, CompareFilesRequest,
    FileUploadResponse, ErrorResponse, SuccessResponse
)
from app.utils.document_compare import DocumentComparator
from app.utils.document_parser import document_parser
from app.utils.pdf_highlighter import pdf_highlighter
from app.utils.file_converter import file_converter
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/compare", tags=["document-compare"])

# 存储上传文件的临时缓存 (生产环境应该使用Redis或数据库)
uploaded_files_cache: Dict[str, Dict[str, Any]] = {}

async def _create_highlighted_pdf(
    file_info: Dict[str, Any],
    match_links: list,
    similarity_threshold_high: float,
    similarity_threshold_medium: float
) -> str:
    """
    创建高亮PDF文件（支持PDF和DOCX）
    
    Args:
        file_info: 文件信息
        match_links: 匹配链接数据
        similarity_threshold_high: 高相似度阈值
        similarity_threshold_medium: 中相似度阈值
        
    Returns:
        高亮PDF文件路径
    """
    try:
        filename = file_info['filename'].lower()
        
        # 处理DOCX文件：先转换为PDF
        if filename.endswith('.docx') or filename.endswith('.doc'):
            # 创建临时DOCX文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx_file:
                temp_docx_file.write(file_info['raw_content'])
                temp_docx_path = temp_docx_file.name
            
            # 转换为PDF
            converted_pdf_path = await file_converter.convert_docx_to_pdf(temp_docx_path)
            
            # 清理临时DOCX文件
            try:
                os.unlink(temp_docx_path)
            except:
                pass
                
            temp_pdf_path = converted_pdf_path
            
        else:
            # 对于PDF文件，直接使用原始内容
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_info['raw_content'])
                temp_pdf_path = temp_file.name
        
        # 准备高亮数据
        highlights = []
        for match in match_links:
            similarity = match.get('similarity', 0.0)
            if similarity >= similarity_threshold_high:
                match_type = 'high'
            elif similarity >= similarity_threshold_medium:
                match_type = 'medium'
            else:
                match_type = 'low'
            
            # 获取待查重文档的文本
            text = match.get('chunk_b', '')
            if text and text.strip():
                # 需要从pdf_highlighter模块导入HighlightMatch类
                from app.utils.pdf_highlighter import HighlightMatch
                highlights.append(HighlightMatch(
                    text=text.strip(),
                    similarity=similarity,
                    match_type=match_type
                ))
        
        # 使用注解高亮方法（保留原始PDF格式）
        highlighted_pdf_path = pdf_highlighter.highlight_pdf_text(
            pdf_path=temp_pdf_path,
            highlights=highlights
        )
        
        # 清理原始临时文件
        try:
            os.remove(temp_pdf_path)
        except:
            pass
        
        return highlighted_pdf_path
        
    except Exception as e:
        logger.error(f"创建高亮PDF失败: {str(e)}")
        # 清理临时文件
        try:
            if 'temp_pdf_path' in locals():
                os.remove(temp_pdf_path)
        except:
            pass
        raise

@router.post("/text", response_model=CompareResponse)
async def compare_text_documents(request: CompareRequest):
    """
    比较两个文本文档
    """
    try:
        logger.info(f"开始比较文本文档: {request.filename_a} vs {request.filename_b}")
        
        # 创建文档比对器实例
        comparator = DocumentComparator(
            similarity_threshold_high=request.similarity_threshold_high,
            similarity_threshold_medium=request.similarity_threshold_medium,
            chunk_size=request.chunk_size
        )
        
        # 执行文档比较
        result = comparator.compare_documents(
            text_a=request.text_a,
            text_b=request.text_b,
            filename_a=request.filename_a,
            filename_b=request.filename_b
        )
        
        # 添加比较时间
        result['metadata']['comparison_time'] = datetime.now()
        
        logger.info(f"文档比较完成，整体相似度: {result['comparison']['overall_similarity']:.3f}")
        
        return CompareResponse(**result)
        
    except Exception as e:
        logger.error(f"文档比较失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文档比较失败: {str(e)}")

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file_for_comparison(file: UploadFile = File(...)):
    """
    上传文件用于比较
    """
    try:
        # 检查文件大小
        file_content = await file.read()
        file_size = len(file_content)
        
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 50 * 1024 * 1024)  # 默认50MB
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"文件太大，最大允许 {max_size // (1024*1024)}MB"
            )
        
        # 检查文件类型
        if not document_parser.is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.filename}"
            )
        
        if document_parser.is_forbidden_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"禁止的文件类型: {file.filename}"
            )
        
        # 生成文件ID
        file_id = str(uuid.uuid4())
        
        # 转换文件为文本
        logger.info(f"开始解析文件: {file.filename}")
        text_content = await document_parser.convert_upload_to_markdown(file_content, file.filename)
        
        # 生成内容预览 (前500字符)
        content_preview = text_content[:500] + "..." if len(text_content) > 500 else text_content
        
        # 存储文件信息到缓存
        uploaded_files_cache[file_id] = {
            'filename': file.filename,
            'content': text_content,
            'raw_content': file_content,  # 存储原始文件内容
            'file_size': file_size,
            'upload_time': datetime.now(),
            'file_hash': hashlib.md5(file_content).hexdigest()
        }
        
        logger.info(f"文件上传成功: {file.filename}, ID: {file_id}")
        
        return FileUploadResponse(
            filename=file.filename,
            file_id=file_id,
            content_preview=content_preview,
            file_size=file_size,
            upload_time=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    下载已上传的文件
    """
    if file_id not in uploaded_files_cache:
        raise HTTPException(status_code=404, detail=f"文件未找到: {file_id}")

    file_info = uploaded_files_cache[file_id]
    file_content = file_info.get('raw_content')
    filename = file_info.get('filename')

    if not file_content or not filename:
        raise HTTPException(status_code=404, detail="文件内容不可用")

    media_type = "application/octet-stream"
    if filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".doc"):
        media_type = "application/msword"
    elif filename.endswith(".txt"):
        media_type = "text/plain"

    # 正确处理Unicode文件名
    from urllib.parse import quote
    filename_encoded = quote(filename)
    headers = {
        "Content-Disposition": f"inline; filename*=utf-8''{filename_encoded}"
    }
    return Response(content=file_content, media_type=media_type, headers=headers)

@router.get("/download/{file_id}/highlighted")
async def download_highlighted_file(file_id: str):
    """
    下载高亮版本的PDF文件
    """
    highlighted_file_id = f"{file_id}_highlighted"
    
    logger.info(f"请求高亮文件: {file_id}, 缓存键: {highlighted_file_id}")
    logger.info(f"缓存中的文件键: {list(uploaded_files_cache.keys())}")
    
    if highlighted_file_id not in uploaded_files_cache:
        logger.warning(f"高亮文件未找到: {highlighted_file_id}")
        raise HTTPException(status_code=404, detail=f"高亮文件未找到: {file_id}")

    file_info = uploaded_files_cache[highlighted_file_id]
    file_content = file_info.get('raw_content')
    filename = file_info.get('filename')

    if not file_content or not filename:
        logger.warning(f"高亮文件内容不可用: {highlighted_file_id}")
        raise HTTPException(status_code=404, detail="高亮文件内容不可用")

    logger.info(f"返回高亮文件: {filename}, 大小: {len(file_content)} bytes")
    
    # 高亮PDF始终使用PDF媒体类型
    media_type = "application/pdf"

    # 正确处理Unicode文件名
    from urllib.parse import quote
    filename_encoded = quote(filename)
    headers = {
        "Content-Disposition": f"inline; filename*=utf-8''{filename_encoded}"
    }
    return Response(content=file_content, media_type=media_type, headers=headers)


@router.post("/files", response_model=CompareResponse) 
async def compare_uploaded_files(request: CompareFilesRequest):
    """
    比较已上传的文件
    """
    try:
        # 检查文件是否存在
        if request.file_a_id not in uploaded_files_cache:
            raise HTTPException(status_code=404, detail=f"文件A未找到: {request.file_a_id}")
        
        if request.file_b_id not in uploaded_files_cache:
            raise HTTPException(status_code=404, detail=f"文件B未找到: {request.file_b_id}")
        
        # 获取文件信息
        file_a_info = uploaded_files_cache[request.file_a_id]
        file_b_info = uploaded_files_cache[request.file_b_id]
        
        logger.info(f"开始比较已上传文件: {file_a_info['filename']} vs {file_b_info['filename']}")
        
        # 创建文档比对器实例
        comparator = DocumentComparator(
            similarity_threshold_high=request.similarity_threshold_high,
            similarity_threshold_medium=request.similarity_threshold_medium,
            chunk_size=request.chunk_size
        )
        
        # 执行文档比较
        result = comparator.compare_documents(
            text_a=file_a_info['content'],
            text_b=file_b_info['content'],
            filename_a=file_a_info['filename'],
            filename_b=file_b_info['filename']
        )
        
        # 根据文件类型决定显示模式和高亮行为
        highlighted_file_ids = {}
        filename_b = file_b_info['filename'].lower()

        if filename_b.endswith('.pdf'):
            result['metadata']['display_mode'] = 'pdf'
            try:
                logger.info(f"为文件B生成高亮PDF: {file_b_info['filename']}")
                highlighted_pdf_path = await _create_highlighted_pdf(
                    file_b_info, 
                    result['comparison']['match_links'],
                    request.similarity_threshold_high,
                    request.similarity_threshold_medium
                )
                
                if highlighted_pdf_path:
                    highlighted_file_id = f"{request.file_b_id}_highlighted"
                    with open(highlighted_pdf_path, 'rb') as f:
                        highlighted_content = f.read()
                    
                    uploaded_files_cache[highlighted_file_id] = {
                        'filename': f"highlighted_{file_b_info['filename']}",
                        'raw_content': highlighted_content,
                        # ... 其他元数据 ...
                    }
                    highlighted_file_ids['file_b'] = highlighted_file_id
                    logger.info(f"✓ 高亮PDF已生成并缓存: {highlighted_file_id}")

            except Exception as e:
                logger.warning(f"生成高亮PDF失败: {str(e)}")
                # 如果PDF高亮失败，回退到HTML模式
                result['metadata']['display_mode'] = 'html'
        else:
            # 对于其他支持的文件类型，使用HTML模式
            result['metadata']['display_mode'] = 'html'
            logger.info(f"文件类型 '{os.path.splitext(filename_b)[1]}' 使用HTML模式展示比对结果")

        # 添加通用元数据
        result['metadata']['comparison_time'] = datetime.now()
        if highlighted_file_ids:
            result['metadata']['highlighted_files'] = highlighted_file_ids
        
        # 调试日志：检查最终的metadata内容
        logger.info(f"最终metadata内容: {result['metadata']}")
        
        logger.info(f"文件比较完成，整体相似度: {result['comparison']['overall_similarity']:.3f}")
        
        return CompareResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件比较失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件比较失败: {str(e)}")

@router.get("/files/{file_id}", response_model=FileUploadResponse)
async def get_uploaded_file_info(file_id: str):
    """
    获取已上传文件的信息
    """
    if file_id not in uploaded_files_cache:
        raise HTTPException(status_code=404, detail=f"文件未找到: {file_id}")
    
    file_info = uploaded_files_cache[file_id]
    content_preview = file_info['content'][:500] + "..." if len(file_info['content']) > 500 else file_info['content']
    
    return FileUploadResponse(
        filename=file_info['filename'],
        file_id=file_id,
        content_preview=content_preview,
        file_size=file_info['file_size'],
        upload_time=file_info['upload_time']
    )

@router.delete("/files/{file_id}", response_model=SuccessResponse)
async def delete_uploaded_file(file_id: str):
    """
    删除已上传的文件
    """
    if file_id not in uploaded_files_cache:
        raise HTTPException(status_code=404, detail=f"文件未找到: {file_id}")
    
    filename = uploaded_files_cache[file_id]['filename']
    del uploaded_files_cache[file_id]
    
    logger.info(f"文件删除成功: {filename}, ID: {file_id}")
    
    return SuccessResponse(message=f"文件删除成功: {filename}")

@router.get("/files", response_model=Dict[str, FileUploadResponse])
async def list_uploaded_files():
    """
    列出所有已上传的文件
    """
    result = {}
    for file_id, file_info in uploaded_files_cache.items():
        content_preview = file_info['content'][:500] + "..." if len(file_info['content']) > 500 else file_info['content']
        
        result[file_id] = FileUploadResponse(
            filename=file_info['filename'],
            file_id=file_id,
            content_preview=content_preview,
            file_size=file_info['file_size'],
            upload_time=file_info['upload_time']
        )
    
    return result

@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "service": "document-compare"}

# 错误处理 - 在FastAPI中，异常处理应该在应用级别设置，而不是路由级别
# 这里移除路由级别的异常处理