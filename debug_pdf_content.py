#!/usr/bin/env python3
"""
调试PDF文本内容，检查为什么高亮不工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fitz  # PyMuPDF

def debug_pdf_content(pdf_path):
    """调试PDF文本内容"""
    
    print(f"=== 调试PDF内容: {pdf_path} ===")
    
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        return
    
    try:
        doc = fitz.open(pdf_path)
        print(f"PDF页数: {doc.page_count}")
        
        for page_num in range(min(3, doc.page_count)):  # 只检查前3页
            page = doc[page_num]
            text = page.get_text()
            
            print(f"\n--- 第{page_num + 1}页文本内容 ---")
            print(f"文本长度: {len(text)}")
            print(f"前300字符: {repr(text[:300])}")
            
            # 检查常见的文本特征
            lines = text.split('\n')
            print(f"行数: {len(lines)}")
            print(f"前5行:")
            for i, line in enumerate(lines[:5]):
                print(f"  {i+1}: {repr(line)}")
        
        doc.close()
        
    except Exception as e:
        print(f"调试PDF失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        debug_pdf_content(pdf_path)
    else:
        print("请提供PDF文件路径")
        print("用法: python debug_pdf_content.py <pdf文件路径>")
        sys.exit(1)