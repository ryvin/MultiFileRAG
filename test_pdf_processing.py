#!/usr/bin/env python3
"""
Test script for enhanced PDF processing.
This script tests the enhanced PDF processing capabilities of the multifile_processor.py module.
"""

import os
import sys
from pathlib import Path

# Try to import the extract_text_from_pdf function from multifile_processor
try:
    from multifile_processor import extract_text_from_pdf
except ImportError:
    print("Error: Could not import extract_text_from_pdf from multifile_processor")
    sys.exit(1)

def test_pdf_processing(pdf_file):
    """Test PDF processing on a specific file."""
    print(f"Testing PDF processing on: {pdf_file}")
    
    if not os.path.exists(pdf_file):
        print(f"Error: File {pdf_file} does not exist")
        return
    
    # Try to extract text from the PDF
    text = extract_text_from_pdf(pdf_file)
    
    if text:
        print(f"Successfully extracted text from {pdf_file}")
        print(f"Extracted {len(text)} characters")
        print("\nFirst 500 characters of extracted text:")
        print("-" * 80)
        print(text[:500])
        print("-" * 80)
        
        # Save the extracted text to a file
        output_file = f"{os.path.splitext(pdf_file)[0]}_extracted.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved extracted text to: {output_file}")
    else:
        print(f"Failed to extract text from {pdf_file}")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_processing.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    test_pdf_processing(pdf_file)

if __name__ == "__main__":
    main()
