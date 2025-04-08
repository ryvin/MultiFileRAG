#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
import requests
import importlib.util

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

def ensure_directories():
    """Ensure the required directories exist."""
    # Create inputs directory if it doesn't exist
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    Path(input_dir).mkdir(parents=True, exist_ok=True)
    
    # Create working directory if it doesn't exist
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Directories created/verified: {input_dir}, {working_dir}")

def check_lightrag_installed():
    """Check if LightRAG is installed."""
    try:
        # Try to import lightrag
        import lightrag
        print(f"✅ LightRAG is installed. Version: {lightrag.__version__}")
        return True
    except ImportError:
        print("❌ LightRAG is not installed.")
        return False

def start_server_directly():
    """Start the LightRAG server directly using the Python API."""
    try:
        # Import required modules
        from lightrag.api.lightrag_server import create_app, run_app
        from lightrag.api.config import global_args, parse_args
        
        # Parse arguments
        args = parse_args()
        
        # Create and run the app
        app = create_app(args)
        run_app(app, args)
        
        return True
    except ImportError as e:
        print(f"❌ Error importing LightRAG modules: {e}")
        print("Please make sure LightRAG is installed with API support.")
        return False
    except Exception as e:
        print(f"❌ Error starting server directly: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Start the MultiFileRAG server")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"), help="Server host")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "9621")), help="Server port")
    parser.add_argument("--working-dir", default=os.getenv("WORKING_DIR", "./rag_storage"), help="Working directory for RAG storage")
    parser.add_argument("--input-dir", default=os.getenv("INPUT_DIR", "./inputs"), help="Directory containing input documents")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"), help="Logging level")
    parser.add_argument("--auto-scan", action="store_true", help="Automatically scan input directory at startup")
    
    args = parser.parse_args()
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("Please start Ollama before running the server.")
        sys.exit(1)
    
    # Ensure directories exist
    ensure_directories()
    
    # Check if LightRAG is installed
    if not check_lightrag_installed():
        print("Please install LightRAG with API support:")
        print("  python install_lightrag.py")
        sys.exit(1)
    
    # Set environment variables
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    os.environ["WORKING_DIR"] = args.working_dir
    os.environ["INPUT_DIR"] = args.input_dir
    os.environ["LOG_LEVEL"] = args.log_level
    
    # Start the server directly
    print(f"Starting MultiFileRAG server on {args.host}:{args.port}...")
    
    try:
        # Try to run the server using uvicorn directly
        import uvicorn
        from lightrag.api.lightrag_server import create_app
        from lightrag.api.config import global_args, parse_args
        
        # Parse arguments
        lightrag_args = parse_args()
        
        # Set auto-scan flag
        if args.auto_scan:
            lightrag_args.auto_scan_at_startup = True
        
        # Create the app
        app = create_app(lightrag_args)
        
        # Run the app
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower()
        )
    except ImportError as e:
        print(f"❌ Error importing LightRAG modules: {e}")
        print("Please make sure LightRAG is installed with API support.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
