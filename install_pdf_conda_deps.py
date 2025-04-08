#!/usr/bin/env python3
"""
Script to install PDF processing dependencies for MultiFileRAG in a conda environment.
"""

import os
import sys
import subprocess
import platform

def install_dependencies():
    """Install PDF processing dependencies in the conda environment."""
    print("Installing PDF processing dependencies in conda environment...")
    
    # Check if we're in a conda environment
    if not os.environ.get('CONDA_PREFIX'):
        print("Error: Not running in a conda environment. Please activate your conda environment first.")
        print("Use: conda activate multifilerag")
        return False
    
    # Define the dependencies to install
    dependencies = [
        "PyPDF2",
        "unstructured",
        "pdfplumber"
    ]
    
    # Install dependencies
    for dependency in dependencies:
        print(f"Installing {dependency}...")
        try:
            if dependency == "unstructured":
                # Install unstructured with PDF support
                subprocess.check_call([sys.executable, "-m", "pip", "install", "unstructured[pdf]"])
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
            print(f"✅ Successfully installed {dependency}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dependency}: {e}")
            return False
    
    print("\nInstallation complete!")
    print("You can now process problematic PDFs with the enhanced PDF processing capabilities.")
    return True

def main():
    """Main entry point."""
    success = install_dependencies()
    if not success:
        print("\nInstallation failed. Please try the following manual steps:")
        print("1. Activate your conda environment: conda activate multifilerag")
        print("2. Install the dependencies manually:")
        print("   pip install PyPDF2")
        print("   pip install unstructured[pdf]")
        print("   pip install pdfplumber")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
