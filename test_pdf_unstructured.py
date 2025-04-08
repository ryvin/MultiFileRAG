#!/usr/bin/env python3
"""
Test PDF processing with unstructured.
"""

import os
import sys
from pathlib import Path

# Check if a file path was provided
if len(sys.argv) < 2:
    print("Usage: python test_pdf_unstructured.py <pdf_file>")
    sys.exit(1)

pdf_file = sys.argv[1]

# Check if the file exists
if not os.path.exists(pdf_file):
    print(f"Error: File {pdf_file} does not exist")
    sys.exit(1)

print(f"Processing PDF file: {pdf_file}")

try:
    # Import unstructured
    from unstructured.partition.pdf import partition_pdf
    
    # Process the PDF
    print("Using unstructured.partition.pdf.partition_pdf...")
    elements = partition_pdf(pdf_file)
    
    # Print the number of elements
    print(f"Extracted {len(elements)} elements from the PDF")
    
    # Join all elements into a single text string
    text_content = "\n\n".join([str(el) for el in elements])
    
    # Print the first 500 characters
    print("\nFirst 500 characters of extracted text:")
    print("-" * 80)
    print(text_content[:500])
    print("-" * 80)
    
    # Save the extracted text to a file
    output_file = f"{os.path.splitext(pdf_file)[0]}_unstructured.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text_content)
    
    print(f"Saved extracted text to: {output_file}")
    
except ImportError:
    print("Error: unstructured.partition.pdf module not found")
    print("Please install with: pip install 'unstructured[pdf]'")
    sys.exit(1)
except Exception as e:
    print(f"Error processing PDF: {e}")
    sys.exit(1)
