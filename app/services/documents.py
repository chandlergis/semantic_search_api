import os
import hashlib
import aiofiles
from uuid import uuid4
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models.documents import Document, Chunk
from app.schemas.documents import DocumentCreate, DocumentRead, DocumentStatus, FileType, DocumentList
from app.core.config import settings
from app.utils.document_parser import document_parser
from app.utils.hybrid_search import ChunkProcessor

class DocumentService:
    def __init__(self):
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        # 初始化分块处理器
        self.chunk_processor = ChunkProcessor()
    
    def check_duplicate_by_hash(self, db: Session, file_hash: str, user_id: str) -> Optional[Document]:
        """根据文件哈希检查重复文件"""
        return db.query(Document).filter(
            Document.source_file_hash == file_hash,
            Document.owner_id == user_id
        ).first()
    
    def get_file_type(self, filename: str) -> FileType:
        """根据文件扩展名确定文件类型"""
        ext = filename.lower().split('.')[-1]
        type_mapping = {
            'pdf': FileType.PDF,
            'docx': FileType.DOCX,
            'doc': FileType.DOCX,
            'pptx': FileType.PPTX,
            'ppt': FileType.PPTX,
            'xlsx': FileType.XLSX,
            'xls': FileType.XLSX,
            'html': FileType.HTML,
            'htm': FileType.HTML,
            'txt': FileType.TXT,
            'csv': FileType.CSV,
            'json': FileType.JSON,
            'xml': FileType.XML
        }
        return type_mapping.get(ext, FileType.TXT)
    
    async def upload_and_process_document(self, db: Session, file: UploadFile, user_id: str, project_id: Optional[str] = None) -> DocumentRead:
        """上传并处理文档"""
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # 文件类型验证
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        if document_parser.is_forbidden_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed: {file.filename}"
            )
        
        if not document_parser.is_supported_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported: {file.filename}"
            )
        
        # 验证项目是否存在且属于当前用户
        if project_id:
            from app.models.projects import Project
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.owner_id == user_id
            ).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found or you don't have permission"
                )
        
        # 读取文件内容并计算哈希
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        # 检查文件是否已存在（去重）
        existing_doc = db.query(Document).filter(
            Document.source_file_hash == file_hash,
            Document.owner_id == user_id
        ).first()
        
        if existing_doc:
            # 如果文件已存在，返回现有文档
            return DocumentRead.from_orm(existing_doc)
        
        # 生成文件ID和路径
        file_id = str(uuid4())
        file_type = self.get_file_type(file.filename)
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
        filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # 创建数据库记录
        db_document = Document(
            id=file_id,
            filename=filename,
            original_filename=file.filename,
            file_type=file_type,
            file_size=len(content),
            file_path=file_path,
            source_file_hash=file_hash,
            status=DocumentStatus.PENDING_PROCESS,
            owner_id=user_id,
            project_id=project_id
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # 异步处理文档
        await self._process_document_async(db, db_document)
        
        return DocumentRead.from_orm(db_document)
    
    async def _process_document_async(self, db: Session, document: Document):
        """异步处理文档内容"""
        try:
            # 更新状态为处理中
            document.status = DocumentStatus.PROCESSING
            db.commit()
            
            # 使用本地文档解析器
            processed_content = await document_parser.convert_file_to_markdown(
                document.file_path, 
                document.original_filename
            )
            
            if processed_content:
                # 生成内容哈希
                content_hash = hashlib.sha256(processed_content.encode()).hexdigest()
                
                # 更新文档记录
                document.processed_content = processed_content
                document.content_hash = content_hash
                document.title = document.title or document.original_filename.split('.')[0]
                document.status = DocumentStatus.PENDING_CHUNK
                
                # 进行分块处理
                await self._create_chunks(db, document, processed_content)
                
                # 标记为完成
                document.status = DocumentStatus.COMPLETED
            else:
                document.status = DocumentStatus.FAILED
                document.error_log = "No content extracted from document"
                    
        except ValueError as e:
            document.status = DocumentStatus.FAILED
            document.error_log = f"Document parsing error: {str(e)}"
        except Exception as e:
            document.status = DocumentStatus.FAILED
            document.error_log = f"Processing error: {str(e)}"
        
        finally:
            db.commit()
    
    async def _create_chunks(self, db: Session, document: Document, content: str):
        """创建文档分块"""
        try:
            # 分割文本为chunks
            chunks = self.chunk_processor.split_text_into_chunks(content)
            
            # 删除现有的chunks（如果有）
            db.query(Chunk).filter(Chunk.document_id == document.id).delete()
            
            # 创建新的chunks
            for i, chunk_content in enumerate(chunks):
                if chunk_content.strip():  # 只处理非空chunks
                    # 计算token数量（简单估算：中文按字符数，英文按单词数）
                    token_count = self._estimate_token_count(chunk_content)
                    
                    chunk = Chunk(
                        id=str(uuid4()),
                        document_id=document.id,
                        content=chunk_content.strip(),
                        chunk_index=i,
                        token_count=token_count
                    )
                    db.add(chunk)
            
            db.commit()
            
        except Exception as e:
            raise ValueError(f"Failed to create chunks: {str(e)}")
    
    def _estimate_token_count(self, text: str) -> int:
        """估算token数量"""
        if not text:
            return 0
        
        # 简单估算：中文字符 + 英文单词
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.split()) - chinese_chars
        
        return chinese_chars + english_words
    
    def get_document(self, db: Session, document_id: str, user_id: str) -> Optional[DocumentRead]:
        """获取文档详情"""
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if document:
            return DocumentRead.from_orm(document)
        return None
    
    def get_document_with_error(self, db: Session, document_id: str, user_id: str) -> Optional[Document]:
        """获取包含错误信息的文档"""
        return db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
    
    def list_documents(self, db: Session, user_id: str, project_id: Optional[str] = None, page: int = 1, per_page: int = 20) -> DocumentList:
        """获取用户文档列表"""
        query = db.query(Document).filter(Document.owner_id == user_id)
        
        if project_id:
            query = query.filter(Document.project_id == project_id)
        
        total = query.count()
        documents = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return DocumentList(
            documents=[DocumentRead.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            per_page=per_page
        )
    
    def delete_document(self, db: Session, document_id: str, user_id: str) -> bool:
        """删除文档"""
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.owner_id == user_id
        ).first()
        
        if document:
            # 删除文件
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # 删除数据库记录
            db.delete(document)
            db.commit()
            return True
        
        return False

document_service = DocumentService()
