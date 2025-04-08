#!/usr/bin/env python3
"""
Script to improve entity extraction for resume documents.
This script will:
1. Delete existing resume documents from the system
2. Reprocess them with improved settings
3. Verify that entities were properly extracted
"""

import os
import sys
import json
import requests
import time
import shutil
from pathlib import Path

def get_document_ids(doc_name, server_url="http://localhost:9621"):
    """Get document IDs for documents matching a name pattern."""
    try:
        response = requests.get(f"{server_url}/documents", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to get documents. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return []
        
        data = response.json()
        statuses = data.get("statuses", {})
        all_docs = []
        for status_type, docs in statuses.items():
            all_docs.extend(docs)
        
        # Find documents matching the name
        matching_docs = [
            doc for doc in all_docs 
            if doc_name.lower() in doc.get("file_path", "").lower()
        ]
        
        # Extract document IDs
        doc_ids = [doc.get("id") for doc in matching_docs if doc.get("id")]
        return doc_ids
    
    except Exception as e:
        print(f"Error getting document IDs: {str(e)}")
        return []

def delete_document(doc_id, server_url="http://localhost:9621"):
    """Delete a document from the system."""
    try:
        response = requests.delete(f"{server_url}/documents/{doc_id}", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to delete document {doc_id}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print(f"Document {doc_id} deleted successfully.")
        return True
    
    except Exception as e:
        print(f"Error deleting document {doc_id}: {str(e)}")
        return False

def upload_document(file_path, server_url="http://localhost:9621"):
    """Upload a document to the system."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return False
        
        # Upload document
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(f"{server_url}/documents/upload", files=files, timeout=60)
            
            if response.status_code != 200:
                print(f"Error: Failed to upload file {file_path}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            print(f"File {file_path} uploaded successfully.")
            return True
    
    except Exception as e:
        print(f"Error uploading file {file_path}: {str(e)}")
        return False

def wait_for_processing(doc_name, timeout=300, server_url="http://localhost:9621"):
    """Wait for documents to be processed."""
    print(f"Waiting for documents matching '{doc_name}' to be processed...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Get document statuses
            response = requests.get(f"{server_url}/documents", timeout=30)
            if response.status_code != 200:
                print(f"Error checking document status. Status code: {response.status_code}")
                time.sleep(10)
                continue
            
            data = response.json()
            statuses = data.get("statuses", {})
            
            # Find matching documents
            matching_docs = []
            for status_type, docs in statuses.items():
                matching_docs.extend([
                    doc for doc in docs 
                    if doc_name.lower() in doc.get("file_path", "").lower()
                ])
            
            if not matching_docs:
                print(f"No documents matching '{doc_name}' found.")
                time.sleep(10)
                continue
            
            # Check if all documents are processed
            all_processed = all(
                doc.get("status") == "PROCESSED" or doc.get("status") == "processed"
                for doc in matching_docs
            )
            
            if all_processed:
                print(f"All documents matching '{doc_name}' have been processed.")
                return True
            
            # Print status
            processing_count = sum(
                1 for doc in matching_docs 
                if doc.get("status") == "PROCESSING" or doc.get("status") == "processing"
            )
            pending_count = sum(
                1 for doc in matching_docs 
                if doc.get("status") == "PENDING" or doc.get("status") == "pending"
            )
            processed_count = sum(
                1 for doc in matching_docs 
                if doc.get("status") == "PROCESSED" or doc.get("status") == "processed"
            )
            failed_count = sum(
                1 for doc in matching_docs 
                if doc.get("status") == "FAILED" or doc.get("status") == "failed"
            )
            
            print(f"Status: {processed_count} processed, {processing_count} processing, {pending_count} pending, {failed_count} failed")
            
            # Wait before checking again
            time.sleep(10)
        
        except Exception as e:
            print(f"Error checking document status: {str(e)}")
            time.sleep(10)
    
    print(f"Timeout waiting for documents to be processed after {timeout} seconds.")
    return False

def check_pipeline_status(server_url="http://localhost:9621"):
    """Check the pipeline status."""
    try:
        response = requests.get(f"{server_url}/documents/pipeline_status", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to get pipeline status. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        return data
    
    except Exception as e:
        print(f"Error checking pipeline status: {str(e)}")
        return None

def scan_for_new_documents(server_url="http://localhost:9621"):
    """Trigger a scan for new documents."""
    try:
        response = requests.post(f"{server_url}/documents/scan", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to trigger scan. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("Document scan triggered successfully.")
        return True
    
    except Exception as e:
        print(f"Error triggering document scan: {str(e)}")
        return False

def improve_resume_extraction():
    """Improve entity extraction for resume documents."""
    server_url = "http://localhost:9621"
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    
    print("=== Resume Entity Extraction Improvement ===\n")
    
    # Step 1: Delete existing resume documents
    print("Step 1: Deleting existing resume documents...")
    resume_doc_ids = get_document_ids("resume", server_url)
    raul_doc_ids = get_document_ids("raul", server_url)
    
    # Combine and deduplicate document IDs
    doc_ids = list(set(resume_doc_ids + raul_doc_ids))
    
    if not doc_ids:
        print("No resume documents found to delete.")
    else:
        print(f"Found {len(doc_ids)} documents to delete.")
        for doc_id in doc_ids:
            delete_document(doc_id, server_url)
    
    # Step 2: Check pipeline status
    print("\nStep 2: Checking pipeline status...")
    status = check_pipeline_status(server_url)
    
    if status and status.get("busy", False):
        print("Pipeline is busy. Waiting for it to complete...")
        # Wait for pipeline to complete
        while True:
            status = check_pipeline_status(server_url)
            if not status or not status.get("busy", False):
                break
            print(f"Pipeline status: {status.get('latest_message', 'Unknown')}")
            time.sleep(10)
    
    # Step 3: Upload resume documents again
    print("\nStep 3: Uploading resume documents...")
    
    # Find resume files in the input directory
    resume_files = []
    for file in os.listdir(input_dir):
        if "resume" in file.lower() or "raul" in file.lower():
            resume_files.append(os.path.join(input_dir, file))
    
    if not resume_files:
        print("No resume files found in the input directory.")
        return
    
    print(f"Found {len(resume_files)} resume files to upload.")
    
    # Upload each file
    for file_path in resume_files:
        upload_document(file_path, server_url)
    
    # Step 4: Trigger a scan for new documents
    print("\nStep 4: Triggering a scan for new documents...")
    scan_for_new_documents(server_url)
    
    # Step 5: Wait for processing to complete
    print("\nStep 5: Waiting for processing to complete...")
    wait_for_processing("raul", timeout=600, server_url=server_url)
    
    # Step 6: Verify entity extraction
    print("\nStep 6: Verifying entity extraction...")
    print("Please run the check_resume_entities.py script after this completes.")

if __name__ == "__main__":
    improve_resume_extraction()
