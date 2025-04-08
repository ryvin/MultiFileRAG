import os
import sys
import requests
import subprocess
import platform

def check_ollama_installed():
    """Check if Ollama is installed on the system."""
    system = platform.system()
    
    if system == "Windows":
        try:
            # Check if Ollama is in the PATH
            result = subprocess.run(["where", "ollama"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama is installed.")
                return True
            else:
                print("❌ Ollama is not installed or not in PATH.")
                return False
        except Exception as e:
            print(f"❌ Error checking Ollama installation: {e}")
            return False
    else:  # Linux or macOS
        try:
            # Check if Ollama is in the PATH
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama is installed.")
                return True
            else:
                print("❌ Ollama is not installed or not in PATH.")
                return False
        except Exception as e:
            print(f"❌ Error checking Ollama installation: {e}")
            return False

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

def main():
    print("🔍 Checking Ollama setup...")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("\n📋 Please install Ollama:")
        print("   - Visit https://ollama.com/download")
        print("   - Follow the installation instructions for your platform")
        sys.exit(1)
    
    # Check if Ollama server is running
    if not check_ollama_running():
        print("\n📋 Please start the Ollama server:")
        print("   - Windows: Start Ollama from the Start Menu")
        print("   - macOS/Linux: Run 'ollama serve' in a terminal")
        sys.exit(1)
    
    # Required models
    required_models = ["llama3", "nomic-embed-text"]
    
    # Check and pull required models
    for model in required_models:
        if not check_model_exists(model):
            print(f"\n📋 Need to pull model '{model}'")
            if not pull_model(model):
                print(f"❌ Failed to pull model '{model}'. Please try manually: ollama pull {model}")
                sys.exit(1)
    
    print("\n✅ Ollama setup is complete! You can now run the MultiFileRAG scripts.")

if __name__ == "__main__":
    main()
