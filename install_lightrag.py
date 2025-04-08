#!/usr/bin/env python3
import os
import sys
import subprocess
import platform

def install_lightrag():
    """Install LightRAG with API support."""
    print("Installing LightRAG with API support...")
    
    # First try installing from PyPI
    try:
        print("Attempting to install LightRAG from PyPI...")
        subprocess.run([sys.executable, "-m", "pip", "install", "lightrag-hku[api]"], check=True)
        
        # Verify installation
        try:
            result = subprocess.run(
                ["pip", "show", "lightrag-hku"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                check=True
            )
            print(f"LightRAG installed: {result.stdout}")
            print("✅ LightRAG installed successfully!")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ LightRAG installed but verification failed.")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing LightRAG from PyPI: {e}")
        
    # If PyPI installation fails, try installing from source
    print("Installing LightRAG from source...")
    try:
        # Clone the repository if it doesn't exist
        if not os.path.exists("lightrag-repo"):
            subprocess.run(["git", "clone", "https://github.com/HKUDS/lightrag.git", "lightrag-repo"], check=True)
        
        # Install from source
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "lightrag-repo[api]"], check=True)
        
        # Verify installation
        try:
            result = subprocess.run(
                ["pip", "show", "lightrag-hku"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                check=True
            )
            print(f"LightRAG installed: {result.stdout}")
            print("✅ LightRAG installed successfully from source!")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Failed to install LightRAG properly.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing LightRAG from source: {e}")
        return False

def main():
    # Install LightRAG
    if not install_lightrag():
        print("Failed to install LightRAG.")
        sys.exit(1)
    
    print("\n✅ Installation complete!")
    print("\nTo start the MultiFileRAG server, run:")
    print("  python start_server.py")
    
    print("\nThe web UI will be available at:")
    print("  http://localhost:9621")

if __name__ == "__main__":
    main()
