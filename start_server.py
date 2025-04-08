#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import argparse
from pathlib import Path
import requests

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
    
    # Build the command to start the server
    cmd = [
        "lightrag-server",
        "--host", args.host,
        "--port", str(args.port),
        "--working-dir", args.working_dir,
        "--input-dir", args.input_dir,
        "--log-level", args.log_level
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
