#!/usr/bin/env python3
"""
Test script to verify the fixed PDF highlighting implementation
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.pdf_highlighter import PDFHighlighter, HighlightMatch
import tempfile

def test_fixed_highlighting():
    """Test the fixed highlighting implementation"""
    print("Testing fixed PDF highlighting implementation...")
    
    # Create a simple test PDF
    import fitz
    doc = fitz.Document()
    page = doc.new_page()
    
    # Add test text
    page.insert_text((50, 50), "This is test text for highlighting demonstration", fontsize=12)
    page.insert_text((50, 70), "Another line of text for testing highlight colors", fontsize=12)
    
    # Save test PDF
    test_pdf_path = "/tmp/test_document.pdf"
    doc.save(test_pdf_path)
    doc.close()
    
    # Create highlighter instance
    highlighter = PDFHighlighter()
    
    # Create test highlights
    highlights = [
        HighlightMatch(
            text="test text for highlighting",
            similarity=0.95,
            match_type='high'  # Should be red
        ),
        HighlightMatch(
            text="Another line of text",
            similarity=0.75,
            match_type='medium'  # Should be orange
        )
    ]
    
    print("Applying highlights with fixed implementation...")
    
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
                print(f"    Stroke color: {annot.colors.get('stroke', 'None')}")
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
    success = test_fixed_highlighting()
    if success:
        print("\n✓ Test completed successfully!")
    else:
        print("\n✗ Test failed!")
        sys.exit(1)