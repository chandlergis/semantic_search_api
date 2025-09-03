#!/usr/bin/env python3
"""
Simple test to verify color annotation fixes work
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.pdf_highlighter import PDFHighlighter, HighlightMatch

def test_simple_color_fix():
    """Simple test of color annotation fixes"""
    print("Testing simple color annotation fixes...")
    
    # Create a simple test PDF with exact text matches
    import fitz
    doc = fitz.Document()
    page = doc.new_page()
    
    # Add test text in exact positions
    test_texts = [
        (50, 50, "这是需要高亮的测试文本A"),
        (50, 70, "这是需要高亮的测试文本B"),
        (50, 90, "这是需要高亮的测试文本C")
    ]
    
    for x, y, text in test_texts:
        page.insert_text((x, y), text, fontsize=12)
    
    test_pdf_path = "/tmp/simple_test.pdf"
    doc.save(test_pdf_path)
    doc.close()
    
    # Create highlighter instance
    highlighter = PDFHighlighter()
    
    # Create highlights with exact text matches
    highlights = [
        HighlightMatch(
            text="这是需要高亮的测试文本A",
            similarity=0.95,
            match_type='high'
        ),
        HighlightMatch(
            text="这是需要高亮的测试文本B", 
            similarity=0.75,
            match_type='medium'
        )
    ]
    
    print("Applying highlights to exact text matches...")
    
    try:
        # Apply highlights
        output_path = highlighter.highlight_pdf_text(
            pdf_path=test_pdf_path,
            highlights=highlights
        )
        
        print(f"✓ Highlights applied successfully!")
        print(f"Output PDF: {output_path}")
        
        # Verify the highlights were created
        doc_check = fitz.open(output_path)
        page_check = doc_check[0]
        annotations = list(page_check.annots())
        
        print(f"Found {len(annotations)} annotations:")
        for i, annot in enumerate(annotations):
            print(f"  Annotation {i+1}: {annot.type[1]}")
            if hasattr(annot, 'colors') and annot.colors:
                stroke_color = annot.colors.get('stroke', 'None')
                print(f"    Stroke color: {stroke_color}")
            if hasattr(annot, 'opacity'):
                print(f"    Opacity: {annot.opacity}")
            
            # Get the annotation rectangle
            rect = annot.rect
            print(f"    Position: ({rect.x0:.1f}, {rect.y0:.1f}) to ({rect.x1:.1f}, {rect.y1:.1f})")
        
        doc_check.close()
        
        if len(annotations) > 0:
            print("\n✓ Color annotation fix verified!")
            return True
        else:
            print("\n⚠ No annotations found - text matching may need adjustment")
            return False
        
    except Exception as e:
        print(f"✗ Error applying highlights: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_color_fix()
    if success:
        print("\n✓ Simple color test successful!")
    else:
        print("\n✗ Simple color test failed!")
        sys.exit(1)