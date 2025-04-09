#!/usr/bin/env python3
"""
Fix Web UI Document Listing

This script checks and fixes issues with the web UI document listing.
"""

import os
import json
import requests
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_server_url():
    """Get the server URL."""
    return "http://localhost:9621"

def check_web_ui_config():
    """Check the web UI configuration."""
    server_url = get_server_url()
    
    # Check if the server is running
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            logger.info("Server is running.")
        else:
            logger.error(f"Server returned status code {response.status_code}.")
            return False
    except Exception as e:
        logger.error(f"Error connecting to server: {e}")
        return False
    
    # Check if the documents endpoint is working
    try:
        response = requests.get(f"{server_url}/documents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "statuses" in data:
                total_docs = sum(len(docs) for docs in data["statuses"].values())
                logger.info(f"Documents endpoint returned {total_docs} documents.")
                return True
            else:
                logger.error("Documents endpoint returned unexpected data structure.")
                return False
        else:
            logger.error(f"Documents endpoint returned status code {response.status_code}.")
            return False
    except Exception as e:
        logger.error(f"Error accessing documents endpoint: {e}")
        return False

def clear_browser_cache():
    """Provide instructions to clear the browser cache."""
    logger.info("To fix the web UI document listing issue, please clear your browser cache:")
    logger.info("1. Open your browser's developer tools (F12 or Ctrl+Shift+I)")
    logger.info("2. Go to the 'Application' or 'Storage' tab")
    logger.info("3. Select 'Clear site data' or 'Clear storage'")
    logger.info("4. Reload the page")

def main():
    """Main function."""
    logger.info("Checking web UI document listing...")
    
    # Check if the web UI config is correct
    if check_web_ui_config():
        logger.info("Web UI configuration appears to be correct.")
        logger.info("If documents are still not showing in the UI, try clearing your browser cache.")
        clear_browser_cache()
    else:
        logger.error("Web UI configuration has issues.")
    
    logger.info("Done.")

if __name__ == "__main__":
    main()
