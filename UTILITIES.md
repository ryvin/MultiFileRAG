# MultiFileRAG Utilities Module

The `multifilerag_utils.py` module provides a comprehensive set of utilities for interacting with the MultiFileRAG system. This document describes the available functions and how to use them.

## Table of Contents

- [API Interaction Functions](#api-interaction-functions)
- [Ollama Interaction Functions](#ollama-interaction-functions)
- [File and Directory Management](#file-and-directory-management)
- [Utility Functions](#utility-functions)
- [Usage Examples](#usage-examples)

## API Interaction Functions

These functions allow you to interact with the MultiFileRAG server API.

### `get_server_url()`

Get the server URL from environment variables or use default.

```python
from multifilerag_utils import get_server_url

# Get server URL
server_url = get_server_url()  # Returns "http://localhost:9621" by default
```

### `get_documents(server_url=None)`

Get all documents from the server API.

```python
from multifilerag_utils import get_documents

# Get all documents
docs = get_documents()  # Uses default server URL
```

### `get_document_counts(server_url=None)`

Get document counts by status.

```python
from multifilerag_utils import get_document_counts

# Get document counts
counts = get_document_counts()
print(f"Processed: {counts.get('PROCESSED', 0)}")
print(f"Failed: {counts.get('FAILED', 0)}")
```

### `get_documents_by_status(status, server_url=None)`

Get documents with a specific status.

```python
from multifilerag_utils import get_documents_by_status

# Get failed documents
failed_docs = get_documents_by_status("FAILED")
```

### `get_failed_documents(server_url=None)`

Get failed documents.

```python
from multifilerag_utils import get_failed_documents

# Get failed documents
failed_docs = get_failed_documents()
```

### `get_pipeline_status(server_url=None)`

Get the current pipeline status from the server.

```python
from multifilerag_utils import get_pipeline_status

# Get pipeline status
status = get_pipeline_status()
if "error" not in status:
    print(f"Pipeline busy: {status.get('busy', False)}")
    print(f"Current job: {status.get('job_name', 'None')}")
```

### `delete_document(doc_id, server_url=None)`

Delete a document from the system.

```python
from multifilerag_utils import delete_document

# Delete a document
success = delete_document("document_id_123")
```

### `upload_document(file_path, server_url=None)`

Upload a document to the system.

```python
from multifilerag_utils import upload_document

# Upload a document
success = upload_document("./inputs/document.pdf")
```

### `scan_for_documents(server_url=None)`

Trigger a scan for new documents.

```python
from multifilerag_utils import scan_for_documents

# Scan for new documents
success = scan_for_documents()
```

### `get_graph(label="*", server_url=None)`

Get the knowledge graph from the server.

```python
from multifilerag_utils import get_graph

# Get the knowledge graph
graph = get_graph()
```

### `query(query_text, mode="hybrid", server_url=None)`

Query the RAG system.

```python
from multifilerag_utils import query

# Query the system
response = query("What is in the document?", mode="mix")
print(response)
```

## Ollama Interaction Functions

These functions allow you to interact with Ollama.

### `check_ollama_status(ollama_host=None)`

Check if Ollama is running and get its version.

```python
from multifilerag_utils import check_ollama_status

# Check if Ollama is running
is_running, version = check_ollama_status()
if is_running:
    print(f"Ollama is running. Version: {version}")
else:
    print(f"Ollama is not running: {version}")
```

### `check_model_status(model_name, ollama_host=None)`

Check if a model is available in Ollama.

```python
from multifilerag_utils import check_model_status

# Check if a model is available
is_available, model_info = check_model_status("deepseek-r1:32b")
if is_available:
    print(f"Model is available: {model_info}")
else:
    print(f"Model is not available: {model_info}")
```

### `check_nvidia_gpu()`

Check if NVIDIA GPU is available and get its information.

```python
from multifilerag_utils import check_nvidia_gpu

# Check if NVIDIA GPU is available
is_available, gpu_info = check_nvidia_gpu()
if is_available:
    print(f"GPU: {gpu_info.get('name')}")
    print(f"Memory: {gpu_info.get('memory')}")
else:
    print(f"GPU not available: {gpu_info}")
```

## File and Directory Management

These functions help with file and directory management.

### `ensure_directories()`

Ensure the required directories exist.

```python
from multifilerag_utils import ensure_directories

# Create required directories
ensure_directories()
```

### `check_graph_file()`

Check if the knowledge graph file exists and has content.

```python
from multifilerag_utils import check_graph_file

# Check if the knowledge graph file exists
has_content = check_graph_file()
```

### `restart_server()`

Restart the MultiFileRAG server.

```python
from multifilerag_utils import restart_server

# Restart the server
success = restart_server()
```

## Utility Functions

These are helper functions for common tasks.

### `print_document_status(data)`

Print document status in a readable format.

```python
from multifilerag_utils import get_documents, print_document_status

# Get documents and print their status
docs = get_documents()
print_document_status(docs)
```

### `wait_for_processing(doc_name, timeout=300, server_url=None)`

Wait for documents to be processed.

```python
from multifilerag_utils import wait_for_processing

# Wait for a document to be processed
success = wait_for_processing("resume.pdf", timeout=600)
```

## Usage Examples

### Checking System Status

```python
from multifilerag_utils import check_ollama_status, get_document_counts, get_pipeline_status

# Check if Ollama is running
is_running, version = check_ollama_status()
if not is_running:
    print(f"Ollama is not running: {version}")
    exit(1)

# Get document counts
counts = get_document_counts()
print(f"Document counts: {counts}")

# Get pipeline status
status = get_pipeline_status()
print(f"Pipeline status: {status}")
```

### Processing Documents

```python
from multifilerag_utils import upload_document, wait_for_processing, query

# Upload a document
success = upload_document("./inputs/document.pdf")
if not success:
    print("Failed to upload document")
    exit(1)

# Wait for the document to be processed
success = wait_for_processing("document.pdf", timeout=600)
if not success:
    print("Document processing timed out")
    exit(1)

# Query the document
response = query("What is in the document?", mode="mix")
print(response)
```

### Reprocessing Failed Documents

```python
from multifilerag_utils import get_failed_documents, delete_document, upload_document

# Get failed documents
failed_docs = get_failed_documents()
print(f"Found {len(failed_docs)} failed documents")

# Reprocess each failed document
for doc in failed_docs:
    doc_id = doc.get("id")
    file_path = doc.get("file_path")
    
    print(f"Reprocessing document: {file_path}")
    
    # Delete the document
    if delete_document(doc_id):
        # Upload the document again
        upload_document(file_path)
```

### Monitoring Document Processing

```python
import time
from multifilerag_utils import get_document_counts, get_pipeline_status

# Monitor document processing
while True:
    # Get document counts
    counts = get_document_counts()
    
    # Get pipeline status
    status = get_pipeline_status()
    
    # Print status
    print(f"Document counts: {counts}")
    print(f"Pipeline status: {status}")
    
    # Wait before checking again
    time.sleep(10)
```

## Testing

The utilities module includes a comprehensive test suite in `test_multifilerag_utils.py`. You can run the tests with:

```bash
python -m unittest test_multifilerag_utils.py
```

This will verify that all the utility functions are working correctly.
