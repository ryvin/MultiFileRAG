import os
import sys
import subprocess
import platform
from pathlib import Path
import requests

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required.")
        sys.exit(1)
    print(f"✅ Python version: {platform.python_version()}")

def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code == 200:
            print(f"✅ Ollama server is running. Version: {response.json().get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Ollama server returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama server is not running. Please start it with 'ollama serve'.")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama server: {e}")
        return False

def check_model_exists(model_name):
    """Check if a model exists in Ollama."""
    try:
        response = requests.get(f"http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                if model.get('name') == model_name:
                    print(f"✅ Model '{model_name}' is already pulled.")
                    return True
            print(f"❌ Model '{model_name}' is not pulled.")
            return False
        else:
            print(f"❌ Failed to get model list. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking model existence: {e}")
        return False

def pull_model(model_name):
    """Pull a model from Ollama."""
    try:
        print(f"📥 Pulling model '{model_name}'... This may take a while.")
        result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Successfully pulled model '{model_name}'.")
            return True
        else:
            print(f"❌ Failed to pull model '{model_name}'. Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")

    # Define dependencies
    dependencies = [
        "lightrag-hku[api]",  # LightRAG with API support
        "pandas>=1.5.0",      # For CSV processing
        "numpy>=1.23.0",      # For numerical operations
        "Pillow>=9.2.0",      # For image processing
        "unstructured[all-docs]>=0.17.0",    # For extracting text from various file types
        "PyPDF2>=3.0.0",      # For PDF processing
        "python-dotenv>=1.0.0" # For environment variables
    ]

    # Install dependencies
    for dependency in dependencies:
        try:
            print(f"Installing {dependency}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dependency], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {dependency}: {e}")
            sys.exit(1)

    print("✅ Dependencies installed successfully!")

def create_env_file():
    """Create .env file for LightRAG server configuration."""
    env_content = """### Server Configuration
HOST=0.0.0.0
PORT=9621
WORKERS=2

### Settings for document indexing
ENABLE_LLM_CACHE_FOR_EXTRACT=true
SUMMARY_LANGUAGE=English
MAX_PARALLEL_INSERT=2

### LLM Configuration
TIMEOUT=200
TEMPERATURE=0.0
MAX_ASYNC=4
MAX_TOKENS=32768

### Ollama LLM Configuration
LLM_BINDING=ollama
LLM_MODEL=llama3
LLM_BINDING_HOST=http://localhost:11434

### Ollama Embedding Configuration
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768

### Web UI Configuration
WEBUI_TITLE="MultiFileRAG"
WEBUI_DESCRIPTION="Process and query PDF, CSV, and image files with LightRAG"

### Storage Configuration
LIGHTRAG_KV_STORAGE=JsonKVStorage
LIGHTRAG_VECTOR_STORAGE=NanoVectorDBStorage
LIGHTRAG_GRAPH_STORAGE=NetworkXStorage
LIGHTRAG_DOC_STATUS_STORAGE=JsonDocStatusStorage

### Working Directory
WORKING_DIR=./rag_storage
INPUT_DIR=./inputs
"""

    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)

    print("✅ Created .env file with configuration for Ollama integration.")

def create_sample_files():
    """Create sample files for demonstration."""
    samples_dir = Path("./samples")
    samples_dir.mkdir(exist_ok=True)

    # Create a sample CSV file
    csv_path = samples_dir / "employee_data.csv"
    csv_content = """Name,Age,Department,Salary,Years_Experience,Performance_Score
John Doe,30,Engineering,85000,5,4.2
Jane Smith,28,Data Science,92000,4,4.5
Bob Johnson,35,Project Management,105000,10,3.8
Alice Brown,42,Marketing,110000,15,4.7
Charlie Davis,25,Design,78000,3,3.9
Eva Wilson,33,Engineering,88000,7,4.1
Frank Miller,45,Finance,120000,18,4.3
Grace Lee,29,Data Science,95000,5,4.6
Henry Taylor,38,Sales,82000,12,3.5
Ivy Martinez,31,Customer Support,75000,6,4.0"""

    with open(csv_path, "w") as f:
        f.write(csv_content)

    # Create a sample text file that will be used as a PDF
    txt_path = samples_dir / "sample_document.txt"
    txt_content = """# Sample Document

## Introduction
This is a sample document that demonstrates the capabilities of MultiFileRAG.

## Features
- Process PDF files
- Process CSV files
- Process image files
- Query across multiple file types

## How It Works
MultiFileRAG uses LightRAG to extract entities and relationships from various file types.
It then builds a knowledge graph that can be queried using natural language.

## Benefits
1. Unified interface for different file types
2. Advanced querying capabilities
3. Visualization of results
4. Integration with local LLMs via Ollama

## Conclusion
MultiFileRAG provides a powerful way to extract insights from your documents."""

    with open(txt_path, "w") as f:
        f.write(txt_content)

    print("✅ Created sample files in the 'samples' directory.")

def create_start_script():
    """Create a script to start the LightRAG server."""
    script_content = """#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_ollama_running():
    \"\"\"Check if Ollama server is running.\"\"\"
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code == 200:
            print(f"✅ Ollama server is running. Version: {response.json().get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Ollama server returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama server is not running. Please start it with 'ollama serve'.")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama server: {e}")
        return False

def ensure_directories():
    \"\"\"Ensure the required directories exist.\"\"\"
    # Create inputs directory if it doesn't exist
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    Path(input_dir).mkdir(parents=True, exist_ok=True)

    # Create working directory if it doesn't exist
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    Path(working_dir).mkdir(parents=True, exist_ok=True)

    print(f"✅ Directories created/verified: {input_dir}, {working_dir}")

def main():
    parser = argparse.ArgumentParser(description="Start the MultiFileRAG server")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"), help="Server host")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "9621")), help="Server port")
    parser.add_argument("--auto-scan", action="store_true", help="Automatically scan input directory at startup")

    args = parser.parse_args()

    # Check if Ollama is running
    if not check_ollama_running():
        print("Please start Ollama before running the server.")
        sys.exit(1)

    # Ensure directories exist
    ensure_directories()

    # Build the command to start the server
    cmd = [
        "lightrag-server",
        "--host", args.host,
        "--port", str(args.port)
    ]

    if args.auto_scan:
        cmd.append("--auto-scan-at-startup")

    # Start the server
    print(f"Starting MultiFileRAG server on {args.host}:{args.port}...")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

    # Write start script
    with open("start_server.py", "w") as f:
        f.write(script_content)

    # Make it executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod("start_server.py", 0o755)

    print("✅ Created start_server.py script.")

def create_readme():
    """Create a README file for the MultiFileRAG server."""
    readme_content = """# MultiFileRAG Server

A specialized implementation of LightRAG for processing PDF, CSV, and image files.

## Overview

MultiFileRAG extends the capabilities of [LightRAG](https://github.com/HKUDS/LightRAG) to work with various file types, with a special focus on PDF, CSV, and image files. It provides enhanced data analysis, visualization, and querying capabilities, all powered by local LLMs through Ollama.

## Features

- **Local LLM Integration**: Uses Ollama to run models locally without relying on external APIs
- **PDF Processing**: Extract text and insights from PDF files
- **CSV Processing**: Extract text, statistics, and insights from CSV files
- **Image Processing**: Extract metadata and descriptions from image files
- **Advanced Querying**: Query across multiple file types using LightRAG's various modes
- **Web UI**: User-friendly interface for uploading files and querying the system

## Requirements

- Python 3.10+
- Ollama (installed and running locally)
- Required Python packages (installed by setup script)

## Installation

1. Run the setup script:
   ```
   python setup_multifilerag_server.py
   ```

2. This will:
   - Check if Ollama is running
   - Pull required Ollama models (llama3, nomic-embed-text)
   - Install LightRAG with API support
   - Install dependencies for PDF, CSV, and image processing
   - Create configuration files
   - Create sample files for demonstration

## Usage

1. Start the MultiFileRAG server:
   ```
   python start_server.py
   ```

2. Access the web UI at:
   ```
   http://localhost:9621
   ```

3. Upload files:
   - Use the "Documents" tab to upload PDF, CSV, and image files
   - The system will automatically process the files and extract entities and relationships

4. Query the system:
   - Use the "Query" tab to ask questions about your documents
   - The system will return answers based on the extracted knowledge

## Query Modes

- **naive**: Basic search without advanced techniques
- **local**: Focuses on context-dependent information
- **global**: Utilizes global knowledge
- **hybrid**: Combines local and global retrieval methods
- **mix**: Integrates knowledge graph and vector retrieval (recommended for most cases)

## Sample Files

The setup script creates sample files in the `samples` directory:
- `employee_data.csv`: A sample CSV file with employee data
- `sample_document.txt`: A sample text file that can be converted to PDF

## License

This project is licensed under the MIT License.
"""

    # Write README file
    with open("README_server.md", "w") as f:
        f.write(readme_content)

    print("✅ Created README_server.md file.")

def main():
    print("🔍 Setting up MultiFileRAG server...")

    # Check Python version
    check_python_version()

    # Check if Ollama is running
    if not check_ollama_running():
        print("Please start Ollama before continuing.")
        sys.exit(1)

    # Check and pull required models
    required_models = ["llama3", "nomic-embed-text"]
    for model in required_models:
        if not check_model_exists(model):
            print(f"\n📋 Need to pull model '{model}'")
            if not pull_model(model):
                print(f"❌ Failed to pull model '{model}'. Please try manually: ollama pull {model}")
                sys.exit(1)

    # Install dependencies
    install_dependencies()

    # Create .env file
    create_env_file()

    # Create sample files
    create_sample_files()

    # Create start script
    create_start_script()

    # Create README
    create_readme()

    # Create directories
    Path("./inputs").mkdir(exist_ok=True)
    Path("./rag_storage").mkdir(exist_ok=True)

    print("\n✅ Setup complete!")
    print("\nTo start the MultiFileRAG server, run:")
    print("  python start_server.py")
    print("\nThe web UI will be available at:")
    print("  http://localhost:9621")
    print("\nYou can upload PDF, CSV, and image files through the web UI.")
    print("Sample files are available in the 'samples' directory.")

if __name__ == "__main__":
    main()
