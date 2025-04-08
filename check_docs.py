#!/usr/bin/env python3
"""
Simple script to check document status using the MultiFileRAG server API.
This script uses the multifilerag_utils module for API interaction.
"""

from multifilerag_utils import get_documents, print_document_status, get_server_url

def main():
    """Main entry point."""
    # Get server URL from environment or use default
    server_url = get_server_url()

    print(f"Checking document status on {server_url}...")

    # Get document status
    data = get_documents(server_url)

    # Print document status
    if data:
        print_document_status(data)
    else:
        print("Failed to get document status.")
        print("Make sure the MultiFileRAG server is running.")

if __name__ == "__main__":
    main()
