#!/usr/bin/env python3
"""
Check API Endpoints

This script checks the API endpoints of the MultiFileRAG server.
"""

import os
import sys
import json
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=False)

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_server_url():
    """Get the server URL from environment variables."""
    # Always use localhost for client connections
    host = "localhost"
    port = os.getenv("PORT", "9621")
    return f"http://{host}:{port}"

def check_documents_endpoint():
    """Check the /documents endpoint."""
    server_url = get_server_url()
    url = f"{server_url}/documents"

    logger.info(f"Checking endpoint: {url}")

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Response status code: {response.status_code}")

            # Check if the response has the expected structure
            if "statuses" in data:
                statuses = data["statuses"]
                total_docs = sum(len(docs) for docs in statuses.values())
                logger.info(f"Total documents: {total_docs}")

                # Print document counts by status
                for status, docs in statuses.items():
                    logger.info(f"Status '{status}': {len(docs)} documents")

                # Print details of a few documents from each status
                for status, docs in statuses.items():
                    if docs:
                        logger.info(f"\nSample documents with status '{status}':")
                        for i, doc in enumerate(docs[:3]):  # Show up to 3 documents per status
                            logger.info(f"  Document {i+1}:")
                            logger.info(f"    ID: {doc.get('id', 'N/A')}")
                            logger.info(f"    File path: {doc.get('file_path', 'N/A')}")
                            logger.info(f"    Content summary: {doc.get('content_summary', 'N/A')[:50]}...")
                            logger.info(f"    Content length: {doc.get('content_length', 'N/A')}")
                            logger.info(f"    Chunks count: {doc.get('chunks_count', 'N/A')}")
                            logger.info(f"    Created at: {doc.get('created_at', 'N/A')}")
                            logger.info(f"    Updated at: {doc.get('updated_at', 'N/A')}")
            else:
                logger.error("Response does not have the expected structure.")
                logger.info(f"Response content: {json.dumps(data, indent=2)}")
        else:
            logger.error(f"Error: Status code {response.status_code}")
            logger.error(f"Response content: {response.text}")
    except Exception as e:
        logger.error(f"Error checking endpoint: {e}")

def main():
    """Main function."""
    logger.info("Checking API endpoints...")
    check_documents_endpoint()
    logger.info("Done.")

if __name__ == "__main__":
    main()
