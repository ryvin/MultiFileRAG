#!/usr/bin/env python3
"""
Script to check the status of documents in the MultiFileRAG system.
This script provides a summary of document processing status.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import LightRAG
try:
    from lightrag import LightRAG
    from lightrag.base import DocStatus
except ImportError:
    print("❌ LightRAG is not installed. Please install it first.")
    sys.exit(1)

async def check_document_status():
    """Check the status of all documents in the system."""
    # Get environment variables or use defaults
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    llm_model_name = os.getenv("LLM_MODEL", "deepseek-r1:32b")
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "bge-m3")
    ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")

    print(f"Working directory: {working_dir}")
    print(f"LLM model: {llm_model_name}")
    print(f"Embedding model: {embedding_model_name}")

    # Initialize LightRAG
    print("Initializing LightRAG...")

    # Import necessary modules
    from lightrag.llm.ollama_llm import OllamaLLM
    from lightrag.embedding.ollama_embedding import OllamaEmbedding

    # Create LLM and embedding instances
    llm = OllamaLLM(model_name=llm_model_name, ollama_host=ollama_host)
    embedding = OllamaEmbedding(model_name=embedding_model_name, ollama_host=ollama_host)

    # Initialize LightRAG with the models
    rag = LightRAG(
        working_dir=working_dir,
        llm=llm,
        embedding=embedding
    )
    await rag.initialize()

    # Get documents by status
    statuses = [
        DocStatus.PENDING,
        DocStatus.PROCESSING,
        DocStatus.PROCESSED,
        DocStatus.FAILED
    ]

    status_counts = {}
    all_docs = {}

    for status in statuses:
        docs = await rag.get_docs_by_status(status)
        status_counts[status] = len(docs)
        all_docs[status] = docs

    # Print summary
    print("\n=== Document Status Summary ===")
    print(f"PENDING:    {status_counts[DocStatus.PENDING]}")
    print(f"PROCESSING: {status_counts[DocStatus.PROCESSING]}")
    print(f"PROCESSED:  {status_counts[DocStatus.PROCESSED]}")
    print(f"FAILED:     {status_counts[DocStatus.FAILED]}")
    print(f"TOTAL:      {sum(status_counts.values())}")

    # Ask if user wants to see details
    show_details = input("\nDo you want to see document details? (y/n): ")
    if show_details.lower() == 'y':
        for status in statuses:
            if status_counts[status] > 0:
                print(f"\n=== {status} Documents ===")
                for doc_id, doc_status in all_docs[status].items():
                    print(f"ID: {doc_id}")
                    print(f"  File: {doc_status.file_path}")
                    print(f"  Created: {doc_status.created_at}")
                    print(f"  Updated: {doc_status.updated_at}")
                    if doc_status.error:
                        print(f"  Error: {doc_status.error}")
                    print()

if __name__ == "__main__":
    asyncio.run(check_document_status())
