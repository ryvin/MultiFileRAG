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
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=False)

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def check_and_start_databases(auto_start=True):
    """Check if databases are running and start them if needed."""
    try:
        # Import the database manager
        from database_manager import get_database_manager

        # Get the database manager instance
        db_manager = get_database_manager()

        # Check if databases are running
        status = db_manager.check_all_services()
        all_running = all(status.values())

        if all_running:
            logger.info("All database services are already running.")
            return True

        # Log which services are not running
        for service, running in status.items():
            if not running:
                logger.info(f"Database service {service} is not running.")

        # Start databases if auto_start is enabled
        if auto_start:
            logger.info("Starting database services...")
            success = db_manager.start_services()
            if success:
                logger.info("Database services started successfully.")
                return True
            else:
                logger.warning("Failed to start database services. Continuing anyway...")
                return False
        else:
            logger.warning("Database services are not running and auto-start is disabled.")
            return False
    except ImportError:
        logger.warning("Database manager not found. Skipping database check.")
        return True
    except Exception as e:
        logger.error(f"Error checking/starting databases: {e}")
        return False

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
    parser.add_argument("--no-db-autostart", action="store_true", help="Disable automatic database startup")

    args = parser.parse_args()

    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

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

    # Check and start databases if needed
    if not args.no_db_autostart:
        logger.info("Checking database services...")
        if not check_and_start_databases(auto_start=True):
            logger.warning("Some database services could not be started. Continuing anyway...")
    else:
        logger.info("Database auto-start is disabled. Skipping database check.")

    # Start the server
    if not start_server(args):
        print("Failed to start the server.")
        sys.exit(1)

if __name__ == "__main__":
    main()
