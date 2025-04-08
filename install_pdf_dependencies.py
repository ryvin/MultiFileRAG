#!/usr/bin/env python3
"""
Script to install PDF processing dependencies for MultiFileRAG.

This script installs the necessary dependencies for robust PDF processing,
including unstructured and pdfplumber.
"""

import os
import sys
import subprocess
import platform

def install_dependencies():
    """Install PDF processing dependencies."""
    print("Installing PDF processing dependencies...")
    
    # Define the dependencies to install
    dependencies = [
        "PyPDF2>=3.0.0",
        "unstructured>=0.10.0",
        "unstructured[pdf]>=0.10.0",
        "pdfplumber>=0.10.0"
    ]
    
    # Install dependencies
    for dependency in dependencies:
        print(f"Installing {dependency}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
            print(f"✅ Successfully installed {dependency}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dependency}: {e}")
    
    print("\nInstallation complete!")
    print("You can now process problematic PDFs with the enhanced PDF processing capabilities.")

if __name__ == "__main__":
    install_dependencies()
