#!/usr/bin/env python3
"""
Check if unstructured is installed and working.
"""

import os
import sys

print("Python version:", sys.version)
print("Python executable:", sys.executable)

# Check if unstructured is installed
try:
    import unstructured
    print("unstructured is installed.")
    try:
        print("Version:", unstructured.__version__)
    except AttributeError:
        print("Version information not available.")

    # Check if PDF-specific partitioner is available
    try:
        from unstructured.partition.pdf import partition_pdf
        print("PDF partitioner is available.")
    except ImportError:
        print("PDF partitioner is not available. You may need to install additional dependencies.")

    # Check if auto partitioner is available
    try:
        from unstructured.partition.auto import partition
        print("Auto partitioner is available.")
    except ImportError:
        print("Auto partitioner is not available. You may need to install additional dependencies.")

except ImportError:
    print("unstructured is not installed.")
    print("Please install it with: pip install 'unstructured[pdf]'")

print("\nChecking for PDF processing dependencies:")

# Check for other PDF processing libraries
try:
    import PyPDF2
    print("PyPDF2 is installed. Version:", PyPDF2.__version__)
except ImportError:
    print("PyPDF2 is not installed.")

try:
    import pdfplumber
    print("pdfplumber is installed. Version:", pdfplumber.__version__)
except ImportError:
    print("pdfplumber is not installed.")

# Check for other dependencies
print("\nChecking for other dependencies:")

try:
    import pandas
    print("pandas is installed. Version:", pandas.__version__)
except ImportError:
    print("pandas is not installed.")

try:
    import numpy
    print("numpy is installed. Version:", numpy.__version__)
except ImportError:
    print("numpy is not installed.")

try:
    from PIL import Image
    print("Pillow is installed. Version:", Image.__version__)
except ImportError:
    print("Pillow is not installed.")

print("\nDone checking dependencies.")
