#!/usr/bin/env python3
"""
Script to check if specific documents were properly processed and their content is available.
"""

import os
import sys
import json
import requests
from pathlib import Path

def get_document_statuses(server_url="http://localhost:9621"):
    """Get the status of all documents from the server API."""
    try:
        response = requests.get(f"{server_url}/documents", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to get documents. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        return data
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def check_document_content(doc_name, server_url="http://localhost:9621"):
    """Check if a specific document was processed and its content is available."""
    # Get all document statuses
    data = get_document_statuses(server_url)
    if not data:
        return False
    
    # Check all statuses for the document
    statuses = data.get("statuses", {})
    all_docs = []
    for status_type, docs in statuses.items():
        all_docs.extend(docs)
    
    # Find documents matching the name
    matching_docs = [doc for doc in all_docs if doc_name.lower() in doc.get("file_path", "").lower()]
    
    if not matching_docs:
        print(f"Document '{doc_name}' not found in the system.")
        return False
    
    # Print details of matching documents
    print(f"Found {len(matching_docs)} documents matching '{doc_name}':")
    for i, doc in enumerate(matching_docs):
        doc_id = doc.get("id", "Unknown")
        file_path = doc.get("file_path", "Unknown")
        status = doc.get("status", "Unknown")
        created_at = doc.get("created_at", "Unknown")
        updated_at = doc.get("updated_at", "Unknown")
        chunks_count = doc.get("chunks_count", 0)
        error = doc.get("error", "")
        
        print(f"\n{i+1}. Document: {file_path}")
        print(f"   ID: {doc_id}")
        print(f"   Status: {status}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        print(f"   Chunks: {chunks_count}")
        if error:
            print(f"   Error: {error}")
    
    # Check if any of the documents were processed successfully
    processed_docs = [doc for doc in matching_docs if doc.get("status") == "PROCESSED"]
    if processed_docs:
        print(f"\n✅ {len(processed_docs)} out of {len(matching_docs)} documents were processed successfully.")
        return True
    else:
        print(f"\n❌ None of the matching documents were processed successfully.")
        return False

def check_text_chunks(server_url="http://localhost:9621"):
    """Check the text chunks in the system to see if they contain resume information."""
    try:
        # Query for resume-related information
        query_terms = ["resume", "Raul Pineda", "experience", "education", "skills"]
        
        for term in query_terms:
            print(f"\nSearching for chunks containing '{term}'...")
            response = requests.post(
                f"{server_url}/query", 
                json={"query": term, "mode": "naive"},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Error: Failed to query. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                continue
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Check if the response contains meaningful information
            if len(response_text) > 100:
                print(f"Found information related to '{term}':")
                print(f"Response length: {len(response_text)} characters")
                print(f"First 200 characters: {response_text[:200]}...")
            else:
                print(f"No significant information found for '{term}'")
    
    except Exception as e:
        print(f"Error querying for text chunks: {str(e)}")

def main():
    """Main entry point."""
    server_url = "http://localhost:9621"
    
    print("=== Document Content Check ===\n")
    
    # Check for resume documents
    print("Checking for resume documents...")
    resume_found = check_document_content("resume", server_url)
    
    # Check for Raul Pineda documents
    print("\nChecking for documents related to Raul Pineda...")
    raul_found = check_document_content("raul", server_url)
    
    # Check text chunks for resume content
    print("\nChecking text chunks for resume content...")
    check_text_chunks(server_url)
    
    # Print recommendations
    print("\n=== Recommendations ===")
    if not resume_found and not raul_found:
        print("1. Upload the resume documents again")
        print("2. Make sure the documents are in a supported format (PDF, DOCX)")
        print("3. Check if the LLM model is properly processing the documents")
    elif not resume_found or not raul_found:
        print("1. Some documents were found but not all")
        print("2. Try reprocessing the missing documents")
    else:
        print("1. Documents were found and processed")
        print("2. If information is still missing, try improving entity extraction")

if __name__ == "__main__":
    main()
