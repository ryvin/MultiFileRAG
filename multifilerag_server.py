#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiFileRAG Server Module

This module provides the server functionality for the MultiFileRAG system.
It starts a web server that provides a REST API for interacting with the system.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=False)

def check_ollama_running():
    """Check if Ollama server is running."""
    from multifilerag_utils import check_ollama_status

    ollama_running, ollama_version = check_ollama_status()
    if ollama_running:
        print(f"✅ Ollama server is running. Version: {ollama_version}")
        return True

    print(f"❌ Ollama server is not running: {ollama_version}")
    return False

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

def ensure_directories():
    """Ensure the required directories exist."""
    from multifilerag_utils import ensure_directories as utils_ensure_directories
    utils_ensure_directories()

def start_server(args):
    """Start the LightRAG server."""
    try:
        # Import required modules
        from lightrag.api.lightrag_server import create_app
        from lightrag.api.config import parse_args
        import uvicorn

        # Set environment variables
        os.environ["HOST"] = args.host
        os.environ["PORT"] = str(args.port)
        os.environ["WORKING_DIR"] = args.working_dir
        os.environ["INPUT_DIR"] = args.input_dir
        os.environ["LOG_LEVEL"] = args.log_level

        # Parse arguments for LightRAG
        lightrag_args = parse_args()

        # Set auto-scan flag
        if args.auto_scan:
            lightrag_args.auto_scan_at_startup = True

        # Create the app
        app = create_app(lightrag_args)

        # Run the app
        print(f"Starting MultiFileRAG server on {args.host}:{args.port}...")
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower()
        )

        return True
    except ImportError as e:
        print(f"❌ Error importing LightRAG modules: {e}")
        print("Please make sure LightRAG is installed with API support.")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main entry point for the MultiFileRAG server.

    This function parses command-line arguments, checks if Ollama and LightRAG
    are properly installed, ensures required directories exist, and starts the server.
    """
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

    # Check if LightRAG is installed
    if not check_lightrag_installed():
        print("Please install LightRAG with API support:")
        print("  python install_lightrag.py")
        sys.exit(1)

    # Ensure directories exist
    ensure_directories()

    # Start the server
    if not start_server(args):
        print("Failed to start the server.")
        sys.exit(1)

if __name__ == "__main__":
    main()
