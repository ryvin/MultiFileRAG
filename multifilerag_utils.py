#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiFileRAG Utilities Module

This module provides common utility functions for the MultiFileRAG system,
including API interaction, Ollama status checking, and directory management.

These utilities are used by both the main application and utility scripts.
"""

import os
import sys
import json
import requests
import subprocess
import platform
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===== API Interaction Functions =====

def get_server_url() -> str:
    """
    Get the server URL from environment variables or use default.

    Returns:
        str: The server URL (e.g., "http://localhost:9621")
    """
    # Always use localhost for client connections, even if server binds to 0.0.0.0
    host = "localhost"
    port = os.getenv("PORT", "9621")
    return f"http://{host}:{port}"

def get_documents(server_url: Optional[str] = None) -> Optional[Dict]:
    """
    Get all documents from the server API.

    Args:
        server_url: The server URL (default: from environment variables)

    Returns:
        Optional[Dict]: Document data or None if there was an error
    """
    if server_url is None:
        server_url = get_server_url()

    try:
        response = requests.get(f"{server_url}/documents", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to get documents. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_document_counts(server_url: Optional[str] = None) -> Dict:
    """
    Get document counts by status.

    Args:
        server_url: The server URL (default: from environment variables)

    Returns:
        Dict: Document counts by status or error information
    """
    if server_url is None:
        server_url = get_server_url()

    try:
        data = get_documents(server_url)
        if not data:
            return {"error": "Failed to get documents"}

        counts = {
            "PENDING": len(data.get("statuses", {}).get("PENDING", [])),
            "PROCESSING": len(data.get("statuses", {}).get("PROCESSING", [])),
            "PROCESSED": len(data.get("statuses", {}).get("PROCESSED", [])),
            "FAILED": len(data.get("statuses", {}).get("FAILED", []))
        }
        counts["TOTAL"] = sum(counts.values())
        return counts
    except Exception as e:
        return {"error": str(e)}

def get_documents_by_status(status: str, server_url: Optional[str] = None) -> List[Dict]:
    """
    Get documents with a specific status.

    Args:
        status: The status to filter by (PENDING, PROCESSING, PROCESSED, FAILED)
        server_url: The server URL (default: from environment variables)

    Returns:
        List[Dict]: List of documents with the specified status
    """
    if server_url is None:
        server_url = get_server_url()

    data = get_documents(server_url)
    if not data:
        return []

    return data.get("statuses", {}).get(status, [])

def get_failed_documents(server_url: Optional[str] = None) -> List[Dict]:
    """
    Get failed documents.

    Args:
        server_url: The server URL (default: from environment variables)

    Returns:
        List[Dict]: List of failed documents
    """
    return get_documents_by_status("FAILED", server_url)

def get_pipeline_status(server_url: Optional[str] = None) -> Dict:
    """
    Get the current pipeline status from the server.

    Args:
        server_url: The server URL (default: from environment variables)

    Returns:
        Dict: Pipeline status information or error details
    """
    if server_url is None:
        server_url = get_server_url()

    try:
        response = requests.get(f"{server_url}/documents/pipeline_status", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status code: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

def delete_document(doc_id: str, server_url: Optional[str] = None) -> bool:
    """
    Delete a document from the system.

    Args:
        doc_id: The document ID to delete
        server_url: The server URL (default: from environment variables)

    Returns:
        bool: True if successful, False otherwise
    """
    if server_url is None:
        server_url = get_server_url()

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

def upload_document(file_path: str, server_url: Optional[str] = None) -> bool:
    """
    Upload a document to the system.

    Args:
        file_path: Path to the file to upload
        server_url: The server URL (default: from environment variables)

    Returns:
        bool: True if successful, False otherwise
    """
    if server_url is None:
        server_url = get_server_url()

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

def scan_for_documents(server_url: Optional[str] = None) -> bool:
    """
    Trigger a scan for new documents.

    Args:
        server_url: The server URL (default: from environment variables)

    Returns:
        bool: True if successful, False otherwise
    """
    if server_url is None:
        server_url = get_server_url()

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

def get_graph(label: str = "*", server_url: Optional[str] = None) -> Optional[Dict]:
    """
    Get the knowledge graph from the server.

    Args:
        label: The label to filter by (default: "*" for all)
        server_url: The server URL (default: from environment variables)

    Returns:
        Optional[Dict]: Knowledge graph data or None if there was an error
    """
    if server_url is None:
        server_url = get_server_url()

    try:
        response = requests.get(f"{server_url}/graphs?label={label}", timeout=30)
        if response.status_code != 200:
            print(f"Error: Failed to get knowledge graph. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def query(query_text: str, mode: str = "hybrid", server_url: Optional[str] = None) -> str:
    """
    Query the RAG system.

    Args:
        query_text: The query text
        mode: Query mode (naive, local, global, hybrid, mix)
        server_url: The server URL (default: from environment variables)

    Returns:
        str: The response text or error message
    """
    if server_url is None:
        server_url = get_server_url()

    try:
        response = requests.post(
            f"{server_url}/query",
            json={"query": query_text, "mode": mode},
            timeout=60
        )

        if response.status_code != 200:
            return f"Error: Failed to query. Status code: {response.status_code}, Response: {response.text}"

        result = response.json()
        return result.get("response", "No response received")
    except Exception as e:
        return f"Error querying: {str(e)}"

# ===== Ollama Interaction Functions =====

def check_ollama_status(ollama_host: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check if Ollama is running and get its version.

    Args:
        ollama_host: The Ollama host URL (default: from environment variables)

    Returns:
        Tuple[bool, str]: (is_running, version_or_error_message)
    """
    if ollama_host is None:
        ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")

    try:
        response = requests.get(f"{ollama_host}/api/version")
        if response.status_code == 200:
            data = response.json()
            return True, data.get("version", "Unknown")
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_model_status(model_name: str, ollama_host: Optional[str] = None) -> Tuple[bool, Union[Dict, str]]:
    """
    Check if a model is available in Ollama.

    Args:
        model_name: The model name to check
        ollama_host: The Ollama host URL (default: from environment variables)

    Returns:
        Tuple[bool, Union[Dict, str]]: (is_available, model_info_or_error_message)
    """
    if ollama_host is None:
        ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")

    try:
        response = requests.get(f"{ollama_host}/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])

            # Check if the model exists
            for model in models:
                if model.get("name") == model_name:
                    return True, model

            return False, "Model not found"
        else:
            return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_nvidia_gpu() -> Tuple[bool, Union[Dict, str]]:
    """
    Check if NVIDIA GPU is available and get its information.

    Returns:
        Tuple[bool, Union[Dict, str]]: (is_available, gpu_info_or_error_message)
    """
    try:
        # Check if nvidia-smi is available
        if platform.system() == "Windows":
            result = subprocess.run(["where", "nvidia-smi"], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "NVIDIA System Management Interface (nvidia-smi) not found."
        else:
            result = subprocess.run(["which", "nvidia-smi"], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "NVIDIA System Management Interface (nvidia-smi) not found."

        # Run nvidia-smi to get GPU information
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version,cuda_version", "--format=csv,noheader"], capture_output=True, text=True)

        if result.returncode != 0:
            return False, f"Failed to run nvidia-smi: {result.stderr}"

        # Parse the output
        gpu_info = result.stdout.strip().split(',')
        if len(gpu_info) >= 3:
            return True, {
                "name": gpu_info[0].strip(),
                "memory": gpu_info[1].strip(),
                "driver_version": gpu_info[2].strip(),
                "cuda_version": gpu_info[3].strip() if len(gpu_info) > 3 else "Unknown"
            }
        else:
            return False, f"Unexpected output from nvidia-smi: {result.stdout}"
    except Exception as e:
        return False, str(e)

# ===== File and Directory Management =====

def ensure_directories() -> None:
    """
    Ensure the required directories exist.

    Creates the input and working directories if they don't exist.
    """
    # Create inputs directory if it doesn't exist
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    Path(input_dir).mkdir(parents=True, exist_ok=True)

    # Create working directory if it doesn't exist
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    Path(working_dir).mkdir(parents=True, exist_ok=True)

    print(f"✅ Directories created/verified: {input_dir}, {working_dir}")

def check_graph_file() -> bool:
    """
    Check if the knowledge graph file exists and has content.

    Returns:
        bool: True if the file exists and has content, False otherwise
    """
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    graph_file = os.path.join(working_dir, "graph_chunk_entity_relation.graphml")

    if os.path.exists(graph_file):
        file_size = os.path.getsize(graph_file)
        print(f"Graph file exists: {graph_file}")
        print(f"File size: {file_size} bytes")

        if file_size == 0:
            print("WARNING: Graph file is empty. No entities or relationships were extracted.")
            return False
        elif file_size < 1000:
            print("WARNING: Graph file is very small. Few entities or relationships were extracted.")
            return True
        else:
            print("Graph file has sufficient content.")
            return True
    else:
        print(f"WARNING: Graph file does not exist: {graph_file}")
        print("This indicates that no entities or relationships were extracted.")
        return False

def restart_server() -> bool:
    """
    Restart the MultiFileRAG server.

    Returns:
        bool: True if successful, False otherwise
    """
    print("Restarting the MultiFileRAG server...")

    try:
        if os.path.exists("restart_server.bat"):
            subprocess.run(["restart_server.bat"], shell=True)
            return True
        else:
            # Try to find the server process and kill it
            if platform.system() == 'Windows':  # Windows
                subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq MultiFileRAG Server"], shell=True)
            else:  # Linux/Mac
                subprocess.run(["pkill", "-f", "multifilerag_server.py"], shell=True)

            # Wait for the process to terminate
            time.sleep(5)

            # Start the server again
            if os.path.exists("multifilerag_server.py"):
                subprocess.Popen(["python", "multifilerag_server.py"], shell=True)
                print("Server restarted.")
                return True
            else:
                print("Could not find multifilerag_server.py. Please restart the server manually.")
                return False
    except Exception as e:
        print(f"Error restarting server: {str(e)}")
        print("Please restart the server manually.")
        return False

# ===== Utility Functions =====

def print_document_status(data: Optional[Dict]) -> None:
    """
    Print document status in a readable format.

    Args:
        data: Document data from get_documents()
    """
    if not data:
        print("No document data available.")
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

def wait_for_processing(doc_name: str, timeout: int = 300, server_url: Optional[str] = None) -> bool:
    """
    Wait for documents to be processed.

    Args:
        doc_name: Document name pattern to match
        timeout: Maximum time to wait in seconds
        server_url: The server URL (default: from environment variables)

    Returns:
        bool: True if all matching documents are processed, False otherwise
    """
    print(f"Waiting for documents matching '{doc_name}' to be processed...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Get document statuses
            data = get_documents(server_url)
            if not data:
                print("Error checking document status.")
                time.sleep(10)
                continue

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

# ===== Main Function =====

def main():
    """
    Main function for testing the utilities module.
    """
    print("MultiFileRAG Utilities Module")
    print("This module provides common utility functions for the MultiFileRAG system.")
    print("It is not intended to be run directly, but can be imported by other scripts.")

    # Test Ollama status
    print("\nChecking Ollama status...")
    ollama_running, ollama_version = check_ollama_status()
    if ollama_running:
        print(f"✅ Ollama is running. Version: {ollama_version}")
    else:
        print(f"❌ Ollama is not running. Error: {ollama_version}")

    # Test server connection
    print("\nChecking server connection...")
    server_url = get_server_url()
    print(f"Server URL: {server_url}")

    pipeline_status = get_pipeline_status()
    if "error" in pipeline_status:
        print(f"❌ Server is not running. Error: {pipeline_status['error']}")
    else:
        print(f"✅ Server is running. Pipeline status: {pipeline_status}")

    # Test document counts
    print("\nChecking document counts...")
    counts = get_document_counts()
    if "error" in counts:
        print(f"❌ Failed to get document counts. Error: {counts['error']}")
    else:
        print(f"✅ Document counts: {counts}")

if __name__ == "__main__":
    main()
