#!/usr/bin/env python3
"""
Test using document parser for text extraction and then highlighting
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.document_parser import document_parser
from utils.document_compare import DocumentComparator
from utils.pdf_highlighter import PDFHighlighter, HighlightMatch
import tempfile

async def test_with_parser():
    """Test using document parser for proper text extraction"""
    print("Testing document comparison with proper parser text extraction...")
    
    # Create a test PDF file
    import fitz
    doc = fitz.Document()
    page = doc.new_page()
    
    # Add test content
    test_content = """
这是一个测试文档，用于验证文档比对和高亮功能。
文档比对系统应该能够检测到相同的文本内容。
这是第一段相同的文本，应该被高亮显示。
这是第二段相同的文本，也应该被高亮显示。
"""
    
    page.insert_text((50, 50), test_content, fontsize=12)
    
    # Save PDF
    test_pdf_path = "/tmp/parser_test.pdf"
    doc.save(test_pdf_path)
    doc.close()
    
    # Read the PDF content back
    with open(test_pdf_path, 'rb') as f:
        pdf_content = f.read()
    
    print("Using document parser to extract text...")
    
    # Use document parser to extract text (like the actual system does)
    try:
        markdown_content = await document_parser.convert_upload_to_markdown(
            pdf_content, "test.pdf"
        )
        
        print(f"✓ Parser extracted text length: {len(markdown_content)}")
        print(f"First 200 chars: {repr(markdown_content[:200])}")
        
        # Create a second identical document for comparison
        text_a = markdown_content
        text_b = markdown_content  # Same content
        
        # Compare documents
        comparator = DocumentComparator()
        result = comparator.compare_documents(
            text_a=text_a,
            text_b=text_b,
            filename_a="文档A.pdf",
            filename_b="文档B.pdf"
        )
        
        print(f"✓ Comparison completed!")
        print(f"Overall similarity: {result['comparison']['overall_similarity']:.3f}")
        print(f"Total matches: {result['comparison']['total_matches']}")
        
        # Now test highlighting on the original PDF
        if result['comparison']['total_matches'] > 0:
            print("\nTesting PDF highlighting with matched text...")
            
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
                
                # Use the actual text from the match
                highlights.append(HighlightMatch(
                    text=match['chunk_b'],
                    similarity=similarity,
                    match_type=match_type
                ))
            
            print(f"Preparing {len(highlights)} highlights from matches...")
            
            # Apply highlights to original PDF
            output_path = highlighter.highlight_pdf_text(
                pdf_path=test_pdf_path,
                highlights=highlights
            )
            
            print(f"✓ Highlights applied! Output: {output_path}")
            
            # Verify annotations
            doc_check = fitz.open(output_path)
            page_check = doc_check[0]
            annotations = list(page_check.annots())
            
            print(f"Found {len(annotations)} annotations:")
            for i, annot in enumerate(annotations):
                print(f"  Annotation {i+1}: {annot.type[1]}")
            
            doc_check.close()
            
            if len(annotations) > 0:
                print("\n✓ Success! PDF highlighting is working correctly.")
                return True
            else:
                print("\n⚠ No annotations found - text matching issue persists")
                return False
        else:
            print("\n⚠ No matches found in comparison")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_with_parser()
    if success:
        print("\n✓ Test with parser successful!")
    else:
        print("\n✗ Test with parser failed!")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())