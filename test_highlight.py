#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.pdf_highlighter import PDFHighlighter, HighlightMatch

# 创建测试PDF高亮
def test_highlight():
    highlighter = PDFHighlighter()
    
    # 创建测试高亮数据
    highlights = [
        HighlightMatch(text="测试文本", similarity=0.95, match_type="high"),
        HighlightMatch(text="另一个测试", similarity=0.75, match_type="medium"),
        HighlightMatch(text="低相似度", similarity=0.6, match_type="low")
    ]
    
    # 测试HTML方法
    try:
        # 需要先有一个测试PDF文件
        test_pdf_path = "/tmp/test.pdf"
        
        # 如果没有测试PDF，先创建一个简单的
        import fitz
        doc = fitz.Document()
        page = doc.new_page()
        page.insert_text((100, 100), "这是一个测试文本用于验证高亮功能。另一个测试内容在这里。")
        doc.save(test_pdf_path)
        doc.close()
        
        print(f"创建测试PDF: {test_pdf_path}")
        
        # 测试HTML高亮
        output_path = highlighter.highlight_with_html_colors(
            pdf_path=test_pdf_path,
            highlights=highlights
        )
        
        print(f"HTML高亮完成，输出文件: {output_path}")
        
        # 检查文件是否存在
        if os.path.exists(output_path):
            print(f"✓ 高亮PDF文件已创建: {output_path}")
            print(f"文件大小: {os.path.getsize(output_path)} bytes")
        else:
            print("✗ 高亮PDF文件未创建")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_highlight()