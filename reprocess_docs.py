#!/usr/bin/env python3
"""
Simple script to reprocess failed documents using the MultiFileRAG server API.
This avoids direct LightRAG API usage which can be problematic with embedding initialization.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_failed_documents(server_url="http://localhost:9621"):
    """Get the list of failed documents from the server API."""
    try:
        # Get documents endpoint
        response = requests.get(f"{server_url}/documents")
        if response.status_code != 200:
            print(f"Error: Failed to get documents. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        # Parse the response
        data = response.json()
        failed_docs = data.get("statuses", {}).get("FAILED", [])
        return failed_docs
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def delete_document(doc_id, server_url="http://localhost:9621"):
    """Delete a document from the system."""
    try:
        # Delete document endpoint
        response = requests.delete(f"{server_url}/documents/{doc_id}")
        if response.status_code != 200:
            print(f"Error: Failed to delete document {doc_id}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print(f"Document {doc_id} deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting document {doc_id}: {str(e)}")
        return False

def reprocess_document(file_path, server_url="http://localhost:9621"):
    """Reprocess a document by uploading it again."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return False
        
        # Upload document endpoint
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(f"{server_url}/documents/upload", files=files)
            
            if response.status_code != 200:
                print(f"Error: Failed to upload file {file_path}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            print(f"File {file_path} uploaded successfully.")
            return True
    except Exception as e:
        print(f"Error uploading file {file_path}: {str(e)}")
        return False

def main():
    """Main entry point."""
    # Get server URL from environment or use default
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "9621")
    server_url = f"http://{host}:{port}"
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    
    print(f"Checking for failed documents on {server_url}...")
    
    # Get failed documents
    failed_docs = get_failed_documents(server_url)
    
    if not failed_docs:
        print("No failed documents found.")
        return
    
    print(f"Found {len(failed_docs)} failed documents.")
    
    # Ask for confirmation
    confirm = input(f"Do you want to reprocess {len(failed_docs)} failed documents? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Reprocess each failed document
    for doc in failed_docs:
        doc_id = doc.get("id")
        file_path = doc.get("file_path")
        
        if not doc_id or not file_path:
            print(f"Skipping document with missing ID or file path: {doc}")
            continue
        
        print(f"Reprocessing document: {doc_id} - {file_path}")
        
        # Get the full file path
        full_path = os.path.join(input_dir, file_path)
        
        # Delete the document
        if delete_document(doc_id, server_url):
            # Reprocess the document
            reprocess_document(full_path, server_url)
    
    print("Reprocessing complete.")

if __name__ == "__main__":
    main()
