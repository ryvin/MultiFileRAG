#!/usr/bin/env python3
import os
import sys
import subprocess
import platform

def install_dependencies():
    """Install required dependencies in the conda environment."""
    print("Installing required dependencies...")

    # Define dependencies
    conda_packages = [
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "pillow",
        "requests",
        "python-dotenv"
    ]

    pip_packages = [
        "lightrag-hku[api]",
        "unstructured[all-docs]>=0.17.0",
        "PyPDF2>=3.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.23.2",
        "python-multipart>=0.0.6",
        "pydantic>=2.4.2",
        "httpx>=0.25.0",
        "jinja2>=3.1.2",
        "aiofiles>=23.2.1"
    ]

    # Install conda packages
    print("Installing conda packages...")
    try:
        subprocess.run(["conda", "install", "-y"] + conda_packages, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing conda packages: {e}")
        return False

    # Install pip packages
    print("Installing pip packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install"] + pip_packages, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing pip packages: {e}")
        return False

    print("✅ Dependencies installed successfully!")
    return True

def main():
    # Check if running in conda environment
    if "CONDA_PREFIX" not in os.environ:
        print("❌ This script should be run within the conda environment.")
        print("Please activate the conda environment first:")
        print("  conda activate multifilerag")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies.")
        sys.exit(1)

    print("\n✅ Setup complete!")
    print("\nTo start the MultiFileRAG server, run:")
    print("  python start_server.py")

    print("\nThe web UI will be available at:")
    print("  http://localhost:9621")

if __name__ == "__main__":
    main()
