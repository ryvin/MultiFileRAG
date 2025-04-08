#!/usr/bin/env python3
"""
Simple script to check document status using the MultiFileRAG server API.
This avoids direct LightRAG API usage which can be problematic with embedding initialization.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_document_status(server_url="http://localhost:9621"):
    """Get the status of all documents from the server API."""
    try:
        # Get documents endpoint
        response = requests.get(f"{server_url}/documents")
        if response.status_code != 200:
            print(f"Error: Failed to get documents. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        # Parse the response
        data = response.json()
        return data
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def print_document_status(data):
    """Print document status in a readable format."""
    if not data:
        return
    
    # Get status counts
    statuses = data.get("statuses", {})
    pending = statuses.get("PENDING", [])
    processing = statuses.get("PROCESSING", [])
    processed = statuses.get("PROCESSED", [])
    failed = statuses.get("FAILED", [])
    
    # Print summary
    print("\n=== Document Status Summary ===")
    print(f"PENDING:    {len(pending)}")
    print(f"PROCESSING: {len(processing)}")
    print(f"PROCESSED:  {len(processed)}")
    print(f"FAILED:     {len(failed)}")
    print(f"TOTAL:      {len(pending) + len(processing) + len(processed) + len(failed)}")
    
    # Ask if user wants to see details
    show_details = input("\nDo you want to see document details? (y/n): ")
    if show_details.lower() != 'y':
        return
    
    # Print details for each status
    status_groups = [
        ("PENDING", pending),
        ("PROCESSING", processing),
        ("PROCESSED", processed),
        ("FAILED", failed)
    ]
    
    for status_name, docs in status_groups:
        if docs:
            print(f"\n=== {status_name} Documents ===")
            for doc in docs:
                doc_id = doc.get("id", "Unknown")
                file_path = doc.get("file_path", "Unknown")
                created_at = doc.get("created_at", "Unknown")
                updated_at = doc.get("updated_at", "Unknown")
                error = doc.get("error", "")
                
                print(f"ID: {doc_id}")
                print(f"  File: {file_path}")
                print(f"  Created: {created_at}")
                print(f"  Updated: {updated_at}")
                if error:
                    print(f"  Error: {error}")
                print()

def main():
    """Main entry point."""
    # Get server URL from environment or use default
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "9621")
    server_url = f"http://{host}:{port}"
    
    print(f"Checking document status on {server_url}...")
    
    # Get document status
    data = get_document_status(server_url)
    
    # Print document status
    if data:
        print_document_status(data)
    else:
        print("Failed to get document status.")
        print("Make sure the MultiFileRAG server is running.")

if __name__ == "__main__":
    main()
