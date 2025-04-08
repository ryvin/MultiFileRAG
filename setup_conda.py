#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from pathlib import Path
import argparse

def check_conda_installed():
    """Check if conda is installed."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["where", "conda"], capture_output=True, text=True)
        else:
            result = subprocess.run(["which", "conda"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Conda is installed.")
            return True
        else:
            print("❌ Conda is not installed or not in PATH.")
            return False
    except Exception as e:
        print(f"❌ Error checking conda installation: {e}")
        return False

def create_conda_environment():
    """Create a conda environment for MultiFileRAG."""
    print("Creating conda environment for MultiFileRAG...")
    
    try:
        # Check if environment already exists
        result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
        if "multifilerag" in result.stdout:
            print("⚠️ Conda environment 'multifilerag' already exists.")
            response = input("Do you want to recreate it? (y/n): ")
            if response.lower() != 'y':
                print("Using existing environment.")
                return True
            else:
                # Remove existing environment
                subprocess.run(["conda", "env", "remove", "-n", "multifilerag", "-y"], check=True)
        
        # Create environment from environment.yml
        if os.path.exists("environment.yml"):
            subprocess.run(["conda", "env", "create", "-f", "environment.yml"], check=True)
        else:
            # Create environment manually
            subprocess.run(["conda", "create", "-n", "multifilerag", "python=3.10", "-y"], check=True)
            
            # Install conda packages
            subprocess.run([
                "conda", "install", "-n", "multifilerag",
                "pandas", "numpy", "matplotlib", "seaborn", "pillow", "requests", "python-dotenv",
                "-y"
            ], check=True)
            
            # Install pip packages
            if platform.system() == "Windows":
                pip_cmd = ["conda", "run", "-n", "multifilerag", "pip", "install"]
            else:
                pip_cmd = ["conda", "run", "-n", "multifilerag", "pip", "install"]
            
            pip_packages = [
                "lightrag-hku[api]",
                "textract>=1.6.3",
                "PyPDF2>=3.0.0",
                "fastapi>=0.104.0",
                "uvicorn>=0.23.2",
                "python-multipart>=0.0.6",
                "pydantic>=2.4.2",
                "httpx>=0.25.0",
                "jinja2>=3.1.2",
                "aiofiles>=23.2.1"
            ]
            
            subprocess.run(pip_cmd + pip_packages, check=True)
        
        print("✅ Conda environment 'multifilerag' created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating conda environment: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_ollama_running():
    """Check if Ollama server is running."""
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

def check_model_exists(model_name):
    """Check if a model exists in Ollama."""
    try:
        import requests
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

def ensure_directories():
    """Ensure the required directories exist."""
    # Create inputs directory if it doesn't exist
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    Path(input_dir).mkdir(parents=True, exist_ok=True)
    
    # Create working directory if it doesn't exist
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Directories created/verified: {input_dir}, {working_dir}")

def main():
    parser = argparse.ArgumentParser(description="Set up conda environment for MultiFileRAG")
    parser.add_argument("--skip-ollama-check", action="store_true", help="Skip checking Ollama installation")
    
    args = parser.parse_args()
    
    print("🔍 Setting up conda environment for MultiFileRAG...")
    
    # Check if conda is installed
    if not check_conda_installed():
        print("Please install conda before continuing.")
        print("Visit https://docs.conda.io/en/latest/miniconda.html for installation instructions.")
        sys.exit(1)
    
    # Create conda environment
    if not create_conda_environment():
        print("Failed to create conda environment.")
        sys.exit(1)
    
    # Check if Ollama is running (if not skipped)
    if not args.skip_ollama_check:
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
    
    # Ensure directories exist
    ensure_directories()
    
    print("\n✅ Setup complete!")
    print("\nTo activate the conda environment, run:")
    if platform.system() == "Windows":
        print("  conda activate multifilerag")
    else:
        print("  conda activate multifilerag")
    
    print("\nTo start the MultiFileRAG server, run:")
    print("  python start_server.py")
    
    print("\nThe web UI will be available at:")
    print("  http://localhost:9621")

if __name__ == "__main__":
    main()
