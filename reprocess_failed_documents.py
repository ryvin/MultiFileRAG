#!/usr/bin/env python3
"""
Script to reprocess failed documents in the MultiFileRAG system.
This script identifies documents with FAILED status and reprocesses them.
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

async def reprocess_failed_documents():
    """Identify and reprocess failed documents."""
    # Get environment variables or use defaults
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    llm_model_name = os.getenv("LLM_MODEL", "deepseek-r1:32b")
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "bge-m3")
    ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")

    print(f"Working directory: {working_dir}")
    print(f"Input directory: {input_dir}")
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

    # Get failed documents
    print("Fetching documents with FAILED status...")
    failed_docs = await rag.get_docs_by_status(DocStatus.FAILED)

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
    for doc_id, doc_status in failed_docs.items():
        print(f"Reprocessing document: {doc_id} - {doc_status.file_path}")

        # Get the file path
        file_path = doc_status.file_path
        full_path = Path(input_dir) / file_path

        if not full_path.exists():
            print(f"  ❌ File not found: {full_path}")
            continue

        try:
            # Delete the document from the system
            print(f"  Removing document {doc_id} from the system...")
            await rag.adelete_document(doc_id)

            # Reprocess the document
            print(f"  Reprocessing document: {file_path}")
            await rag.apipeline_enqueue_documents(file_paths=str(file_path))
            await rag.apipeline_process_enqueue_documents()

            print(f"  ✅ Document {doc_id} reprocessed successfully.")
        except Exception as e:
            print(f"  ❌ Error reprocessing document {doc_id}: {str(e)}")

    print("Reprocessing complete.")

if __name__ == "__main__":
    asyncio.run(reprocess_failed_documents())
