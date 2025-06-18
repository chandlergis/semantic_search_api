import logging
import os
import tempfile
from typing import Optional
from markitdown import MarkItDown

# Configure logging
logger = logging.getLogger(__name__)

# 禁止的文件扩展名
FORBIDDEN_EXTENSIONS = [
    # Executable and Script Files (Security Risk)
    "exe", "msi", "bat", "cmd",  # Windows
    "dmg", "pkg", "app",  # macOS
    "bin", "sh", "run",  # Linux/Unix
    "dll", "so", "dylib",  # Dynamic libraries
    "jar", "apk",  # Java/Android packages
    "vbs", "ps1",  # Windows scripting
    "pyc", "pyo",  # Compiled Python
    # System and Configuration Files
    "sys", "drv",  # System and driver files
    "config", "ini",  # Configuration files
    # Binary Data Files
    "dat", "bin",  # Generic binary data
    "db", "sqlite", "mdb",  # Database files
    "dbf", "myd",  # Database format files
    # CAD and Specialized Technical Files
    "dxf", "dwg",  # AutoCAD files
    "stl", "obj", "3ds",  # 3D model files
    "blend",  # Blender 3D files
    # Encrypted/Protected Files
    "gpg", "asc", "pgp",  # Encrypted files
    # Virtual Machine and Container Files
    "vdi", "vmdk", "ova",  # Virtual machine disks
    "docker", "containerd",  # Container images
    # Other Binary Formats
    "class",  # Java class files
    "o", "a",  # Object and archive files
    "lib", "obj",  # Compiled library files
    "ttf", "otf",  # Font files
    "fon",  # Windows font resource
]

class DocumentParser:
    def __init__(self):
        self.markitdown = MarkItDown()
    
    def is_forbidden_file(self, filename: str) -> bool:
        """检查文件是否为禁止类型"""
        if not filename or "." not in filename:
            return False
        
        extension = filename.rsplit(".", 1)[1].lower()
        return extension in FORBIDDEN_EXTENSIONS
    
    def is_supported_file(self, filename: str) -> bool:
        """检查文件是否为支持的类型"""
        if not filename or "." not in filename:
            return False
        
        supported_extensions = {
            'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls',
            'html', 'htm', 'txt', 'csv', 'json', 'xml', 'md',
            'rtf', 'odt', 'odp', 'ods'
        }
        
        extension = filename.rsplit(".", 1)[1].lower()
        return extension in supported_extensions
    
    async def convert_file_to_markdown(self, file_path: str, original_filename: str) -> str:
        """将文件转换为Markdown格式"""
        try:
            # 检查文件是否为禁止类型
            if self.is_forbidden_file(original_filename):
                raise ValueError(f"File type not allowed: {original_filename}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            
            logger.info(f"Converting file: {file_path} (original: {original_filename})")
            
            # 使用MarkItDown转换文件
            result = self.markitdown.convert(file_path)
            
            if result and result.text_content:
                logger.info(f"Conversion successful, content length: {len(result.text_content)}")
                return result.text_content
            else:
                raise ValueError("No content extracted from file")
                
        except Exception as e:
            logger.error(f"Error converting file {file_path}: {str(e)}")
            raise ValueError(f"Failed to convert file: {str(e)}")
    
    async def convert_upload_to_markdown(self, file_content: bytes, original_filename: str) -> str:
        """将上传的文件内容转换为Markdown格式"""
        temp_file_path = None
        try:
            # 检查文件是否为禁止类型
            if self.is_forbidden_file(original_filename):
                raise ValueError(f"File type not allowed: {original_filename}")
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{original_filename}") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
                logger.info(f"Created temporary file: {temp_file_path}")
            
            # 转换文件
            markdown_content = await self.convert_file_to_markdown(temp_file_path, original_filename)
            
            return markdown_content
            
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Temporary file deleted: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_file_path}: {e}")

# 全局解析器实例
document_parser = DocumentParser()