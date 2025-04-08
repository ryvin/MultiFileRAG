#!/usr/bin/env python3
"""
Process all account statement PDFs using unstructured.
"""

import os
import sys
import glob
from pathlib import Path

def process_pdf_with_unstructured(pdf_file):
    """Process a PDF file using unstructured."""
    try:
        from unstructured.partition.pdf import partition_pdf

        print(f"Processing: {pdf_file}")

        # Process the PDF
        elements = partition_pdf(pdf_file)

        # Join all elements into a single text string
        text_content = "\n\n".join([str(el) for el in elements])

        # Save the extracted text to a file
        output_file = f"{os.path.splitext(pdf_file)[0]}_unstructured.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text_content)

        print(f"Saved extracted text to: {output_file}")
        return True
    except ImportError:
        print("Error: unstructured.partition.pdf module not found")
        print("Please install with: pip install 'unstructured[pdf]'")
        return False
    except Exception as e:
        print(f"Error processing PDF {pdf_file}: {e}")
        return False

def main():
    """Main entry point."""
    # Get the inputs directory
    inputs_dir = "E:/Code/MultiFileRAG/inputs"

    # Find all account statement PDFs
    account_statements = []
    for file in os.listdir(inputs_dir):
        if file.endswith(".pdf") and ("Account Statements" in file or "1978897 Account Statements" in file):
            account_statements.append(os.path.join(inputs_dir, file))

    if not account_statements:
        print("No account statement PDFs found in the inputs directory.")
        return

    print(f"Found {len(account_statements)} account statement PDFs.")

    # Process each PDF
    success_count = 0
    error_count = 0

    for pdf_file in account_statements:
        if process_pdf_with_unstructured(pdf_file):
            success_count += 1
        else:
            error_count += 1

    print("\nProcessing complete!")
    print(f"Successfully processed: {success_count} files")
    print(f"Failed to process: {error_count} files")

if __name__ == "__main__":
    main()
