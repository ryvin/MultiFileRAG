#!/usr/bin/env python3
"""
Simple script to reprocess failed documents using the MultiFileRAG server API.
This script uses the multifilerag_utils module for API interaction.
"""

import os
from multifilerag_utils import (
    get_failed_documents, delete_document,
    upload_document, get_server_url
)

def main():
    """Main entry point for reprocessing failed documents."""
    # Get server URL from environment or use default
    server_url = get_server_url()

    print(f"Checking for failed documents on {server_url}...")

    # Get failed documents
    failed_docs = get_failed_documents(server_url)

    if not failed_docs:
        print("No failed documents found.")
        return

    print(f"Found {len(failed_docs)} failed documents.")

    # Process each failed document
    for doc in failed_docs:
        doc_id = doc.get("id")
        file_path = doc.get("file_path")
        error = doc.get("error", "Unknown error")

        print(f"\nReprocessing document: {file_path}")
        print(f"Error: {error}")

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist. Skipping.")
            continue

        # Delete the document
        if delete_document(doc_id, server_url):
            # Reprocess the document
            upload_document(file_path, server_url)

    print("Reprocessing complete.")

if __name__ == "__main__":
    main()
