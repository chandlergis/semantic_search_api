#!/usr/bin/env python3
"""
Complete test of document comparison with fixed highlighting
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.document_compare import DocumentComparator
from utils.pdf_highlighter import PDFHighlighter, HighlightMatch
import tempfile

def test_complete_comparison():
    """Test complete document comparison with highlighting"""
    print("Testing complete document comparison with fixed highlighting...")
    
    # Create test documents with identical content
    text_a = """
这是一个测试文档，用于验证文档比对和高亮功能。
文档比对系统应该能够检测到相同的文本内容。
这是第一段相同的文本，应该被高亮显示。
这是第二段相同的文本，也应该被高亮显示。
"""

    text_b = """
这是一个测试文档，用于验证文档比对和高亮功能。
文档比对系统应该能够检测到相同的文本内容。
这是第一段相同的文本，应该被高亮显示。
这是第二段相同的文本，也应该被高亮显示。
"""

    # Create comparator
    comparator = DocumentComparator(
        similarity_threshold_high=0.9,
        similarity_threshold_medium=0.7,
        chunk_size=100
    )
    
    print("Comparing documents...")
    
    # Compare documents
    result = comparator.compare_documents(
        text_a=text_a,
        text_b=text_b,
        filename_a="测试文档A.pdf",
        filename_b="测试文档B.pdf"
    )
    
    print(f"✓ Comparison completed!")
    print(f"Overall similarity: {result['comparison']['overall_similarity']:.3f}")
    print(f"Total matches: {result['comparison']['total_matches']}")
    print(f"High similarity matches: {result['comparison']['high_similarity_matches']}")
    print(f"Medium similarity matches: {result['comparison']['medium_similarity_matches']}")
    
    # Test PDF highlighting
    print("\nTesting PDF highlighting...")
    
    # Create test PDF for highlighting
    import fitz
    doc = fitz.Document()
    page = doc.new_page()
    
    # Add the text content
    page.insert_text((50, 50), text_b, fontsize=10)
    
    test_pdf_path = "/tmp/comparison_test.pdf"
    doc.save(test_pdf_path)
    doc.close()
    
    # Create highlights from comparison results
    highlighter = PDFHighlighter()
    highlights = []
    
    for match in result['comparison']['match_links']:
        similarity = match['similarity']
        if similarity >= 0.9:
            match_type = 'high'
        elif similarity >= 0.7:
            match_type = 'medium'
        else:
            continue
        
        highlights.append(HighlightMatch(
            text=match['chunk_b'],
            similarity=similarity,
            match_type=match_type
        ))
    
    print(f"Preparing {len(highlights)} highlights...")
    
    # Apply highlights
    try:
        output_path = highlighter.highlight_pdf_text(
            pdf_path=test_pdf_path,
            highlights=highlights
        )
        
        print(f"✓ Highlights applied successfully!")
        print(f"Highlighted PDF: {output_path}")
        
        # Verify highlights
        doc_check = fitz.open(output_path)
        page_check = doc_check[0]
        annotations = list(page_check.annots())
        
        print(f"Found {len(annotations)} annotations in highlighted PDF:")
        for i, annot in enumerate(annotations):
            print(f"  Annotation {i+1}: {annot.type[1]}")
            if hasattr(annot, 'colors') and annot.colors:
                stroke_color = annot.colors.get('stroke', 'None')
                print(f"    Stroke color: {stroke_color}")
            if hasattr(annot, 'opacity'):
                print(f"    Opacity: {annot.opacity}")
        
        doc_check.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error applying highlights: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_comparison()
    if success:
        print("\n✓ Complete test successful! PDF highlighting should now work correctly.")
    else:
        print("\n✗ Test failed!")
        sys.exit(1)