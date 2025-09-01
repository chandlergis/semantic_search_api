import logging
import os
import tempfile
from typing import Optional
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class FileConverter:
    """文件格式转换工具"""
    
    def __init__(self):
        pass
    
    async def convert_docx_to_pdf(self, docx_path: str, output_path: Optional[str] = None) -> str:
        """
        将DOCX文件转换为PDF格式
        
        Args:
            docx_path: DOCX文件路径
            output_path: 输出PDF路径，如果为None则生成临时文件
            
        Returns:
            转换后的PDF文件路径
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(docx_path):
                raise ValueError(f"DOCX文件不存在: {docx_path}")
            
            # 生成输出路径
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(docx_path))[0]
                output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp_files")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{base_name}_converted.pdf")
            
            # 使用不同的转换方法
            pdf_path = await self._convert_with_libreoffice(docx_path, output_path)
            
            if pdf_path and os.path.exists(pdf_path):
                logger.info(f"DOCX转PDF成功: {docx_path} -> {pdf_path}")
                return pdf_path
            else:
                raise RuntimeError("DOCX转PDF失败")
                
        except Exception as e:
            logger.error(f"DOCX转PDF失败: {str(e)}")
            raise
    
    async def _convert_with_libreoffice(self, docx_path: str, output_path: str) -> str:
        """使用LibreOffice进行转换（轻量级方案中不使用）"""
        # 在轻量级方案中，我们直接使用python方案
        return await self._convert_with_python(docx_path, output_path)
    
    async def _convert_with_python(self, docx_path: str, output_path: str) -> str:
        """使用python-docx读取内容，然后通过HTML转PDF"""
        try:
            # 尝试导入python-docx
            try:
                from docx import Document
            except ImportError:
                logger.warning("python-docx未安装，无法进行DOCX处理")
                raise RuntimeError("请安装python-docx以支持DOCX文件处理")
            
            # 读取DOCX内容
            doc = Document(docx_path)
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            
            # 构建简单的HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Converted Document</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
                    p {{ margin-bottom: 16px; }}
                </style>
            </head>
            <body>
                {"<p>".join(full_text)}
            </body>
            </html>
            """
            
            # 使用weasyprint将HTML转换为PDF
            try:
                from weasyprint import HTML
                HTML(string=html_content).write_pdf(output_path)
                
                if os.path.exists(output_path):
                    logger.info(f"DOCX转PDF成功: {output_path}")
                    return output_path
                else:
                    raise RuntimeError("HTML转PDF失败")
                    
            except ImportError:
                logger.warning("weasyprint未安装，使用纯文本方案")
                # 如果weasyprint不可用，创建简单的文本PDF
                return await self._create_simple_text_pdf(full_text, output_path)
                
        except Exception as e:
            logger.error(f"DOCX转PDF失败: {str(e)}")
            raise
    
    async def _create_simple_text_pdf(self, text_lines: list, output_path: str) -> str:
        """创建简单的文本PDF（备用方案）"""
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
            pdf.set_font('DejaVu', size=12)
            
            for line in text_lines:
                pdf.multi_cell(0, 10, line)
            
            pdf.output(output_path)
            return output_path
            
        except ImportError:
            logger.error("fpdf未安装，无法创建PDF")
            raise RuntimeError("请安装weasyprint或fpdf以支持PDF转换")
        except Exception as e:
            logger.error(f"创建简单PDF失败: {str(e)}")
            raise
    
    def is_docx_file(self, filename: str) -> bool:
        """检查文件是否为DOCX格式"""
        return filename.lower().endswith(('.docx', '.doc'))
    
    def is_pdf_file(self, filename: str) -> bool:
        """检查文件是否为PDF格式"""
        return filename.lower().endswith('.pdf')

# 全局转换器实例
file_converter = FileConverter()