#!/usr/bin/env python3
"""
Debug PDF text search functionality
"""
import fitz

def debug_pdf_search():
    """Debug PDF text search"""
    print("Debugging PDF text search functionality...")
    
    # Create a simple test PDF with Chinese text
    doc = fitz.Document()
    page = doc.new_page()
    
    # Add Chinese test text
    test_texts = [
        (50, 50, "这是需要高亮的测试文本A"),
        (50, 70, "这是需要高亮的测试文本B"),
        (50, 90, "这是需要高亮的测试文本C")
    ]
    
    for x, y, text in test_texts:
        page.insert_text((x, y), text, fontsize=12)
    
    test_pdf_path = "/tmp/debug_search.pdf"
    doc.save(test_pdf_path)
    doc.close()
    
    # Open the PDF and test search
    doc = fitz.open(test_pdf_path)
    page = doc[0]
    
    print("=== PDF Text Content ===")
    raw_text = page.get_text()
    print(f"Raw text: {repr(raw_text)}")
    
    print("\n=== Testing Search Strategies ===")
    
    # Test various search strategies
    target_texts = [
        "这是需要高亮的测试文本A",
        "需要高亮的测试文本",
        "测试文本A",
        "高亮",
        "文本"
    ]
    
    for target in target_texts:
        print(f"\nSearching for: {repr(target)}")
        
        # Direct search
        instances = page.search_for(target)
        print(f"  Direct search: {len(instances)} results")
        
        # Cleaned text search
        cleaned = ' '.join(target.split())
        if cleaned != target:
            cleaned_instances = page.search_for(cleaned)
            print(f"  Cleaned search: {len(cleaned_instances)} results")
        
        # No-space Chinese text
        if any('\u4e00' <= c <= '\u9fff' for c in target):
            no_space = target.replace(' ', '')
            if no_space != target:
                no_space_instances = page.search_for(no_space)
                print(f"  No-space search: {len(no_space_instances)} results")
    
    doc.close()
    print("\n=== Debug complete ===")

if __name__ == "__main__":
    debug_pdf_search()