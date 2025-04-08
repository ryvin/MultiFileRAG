#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiFileRAG Core Module

This module provides the core functionality for the MultiFileRAG system, integrating
LightRAG with file processing capabilities for PDF, CSV, image, and other file types.

The MultiFileRAG class handles initialization, document processing, and querying,
while utility functions support these operations. For additional utilities, see the
multifilerag_utils.py module which provides a comprehensive set of helper functions
for API interaction, Ollama status checking, and file operations.

Author: Raul Pineda
Version: 1.1.0
License: MIT
"""

import os
import sys
import asyncio
import nest_asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, AsyncGenerator
import json

# Apply nest_asyncio to allow nested event loops (needed for Jupyter notebooks)
nest_asyncio.apply()

# Import LightRAG components
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc, logger
from lightrag.kg.shared_storage import initialize_pipeline_status

# Import our file processors
try:
    from multifile_processor import (
        extract_text_from_pdf,
        extract_text_from_csv,
        extract_text_from_image,
        process_file
    )
except ImportError as e:
    print(f"Warning: Could not import multifile_processor: {e}")
    # Define dummy functions for when multifile_processor is not available
    def extract_text_from_pdf(file_path):
        """Dummy function for PDF processing when multifile_processor is not available."""
        return f"PDF processing not available: {file_path}"

    def extract_text_from_csv(file_path):
        """Dummy function for CSV processing when multifile_processor is not available."""
        return f"CSV processing not available: {file_path}"

    def extract_text_from_image(file_path):
        """Dummy function for image processing when multifile_processor is not available."""
        return f"Image processing not available: {file_path}"

    def process_file(file_path):
        """Dummy function for file processing when multifile_processor is not available."""
        return f"File processing not available: {file_path}"

class MultiFileRAG:
    """
    MultiFileRAG class that integrates LightRAG with PDF, CSV, and image processing.

    This class provides a high-level interface for working with the LightRAG system,
    with added capabilities for processing various file types including PDFs, CSVs,
    images, and more. It handles initialization of the LightRAG system, document
    processing, and querying.

    Attributes:
        working_dir (str): Directory for storing RAG data (vectors, graphs, etc.)
        input_dir (str): Directory containing input files to process
        llm_model_name (str): Name of the Ollama LLM model to use
        embedding_model_name (str): Name of the Ollama embedding model to use
        ollama_host (str): URL of the Ollama server
        rag (LightRAG): The underlying LightRAG instance
    """

    def __init__(
        self,
        working_dir: str = "./rag_storage",
        input_dir: str = "./inputs",
        llm_model_name: str = "llama3",
        embedding_model_name: str = "nomic-embed-text",
        ollama_host: str = "http://localhost:11434",
        log_level: str = "INFO"
    ):
        """
        Initialize the MultiFileRAG instance.

        Args:
            working_dir (str): Directory for storing RAG data (vectors, graphs, etc.)
            input_dir (str): Directory containing input files to process
            llm_model_name (str): Name of the Ollama LLM model to use (e.g., "llama3", "deepseek-r1:32b")
            embedding_model_name (str): Name of the Ollama embedding model to use (e.g., "nomic-embed-text", "bge-m3")
            ollama_host (str): URL of the Ollama server (default: "http://localhost:11434")
            log_level (str): Logging level (e.g., "INFO", "DEBUG", "WARNING")

        Note:
            This method only sets up the instance attributes. You must call `initialize()`
            to fully initialize the LightRAG system before using other methods.
        """
        self.working_dir = working_dir
        self.input_dir = input_dir
        self.llm_model_name = llm_model_name
        self.embedding_model_name = embedding_model_name
        self.ollama_host = ollama_host

        # Set up logging
        logging.basicConfig(format="%(levelname)s:%(message)s", level=getattr(logging, log_level))

        # Create directories if they don't exist
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        Path(input_dir).mkdir(parents=True, exist_ok=True)

        # Initialize the RAG instance
        self.rag = None

    async def initialize(self):
        """
        Initialize the LightRAG instance.

        This method creates and initializes the underlying LightRAG instance with the
        appropriate LLM and embedding models. It must be called before using any other
        methods that interact with the RAG system.

        Returns:
            self: The initialized MultiFileRAG instance (for method chaining)

        Raises:
            Exception: If there's an error initializing the LightRAG instance or its storages
        """
        # Get embedding dimension from environment variable or determine based on model
        embedding_dim = int(os.getenv("EMBEDDING_DIM", "768"))  # Default to 768 if not specified

        # Override with model-specific dimension if not explicitly set in .env
        if "EMBEDDING_DIM" not in os.environ and self.embedding_model_name == "bge-m3":
            embedding_dim = 1024

        # Create the LightRAG instance
        self.rag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=ollama_model_complete,
            llm_model_name=self.llm_model_name,
            llm_model_max_async=4,
            llm_model_max_token_size=32768,
            llm_model_kwargs={
                "host": self.ollama_host,
                "options": {"num_ctx": 32768},
            },
            embedding_func=EmbeddingFunc(
                embedding_dim=embedding_dim,
                max_token_size=8192,
                func=lambda texts: ollama_embed(
                    texts, embed_model=self.embedding_model_name, host=self.ollama_host
                ),
            ),
        )

        # Initialize storages and pipeline status
        await self.rag.initialize_storages()
        await initialize_pipeline_status()

        logger.info("MultiFileRAG initialized successfully")
        return self

    def process_and_insert_file(self, file_path: str) -> bool:
        """Process a file and insert its content into the RAG system.

        Args:
            file_path: Path to the file to process

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.rag:
            logger.error("RAG system not initialized. Call initialize() first.")
            return False

        try:
            # Process the file
            logger.info(f"Processing file: {file_path}")
            text_content = process_file(file_path)

            if not text_content:
                logger.error(f"Failed to extract content from {file_path}")
                return False

            # Insert the content into the RAG system
            logger.info(f"Inserting content from {file_path} into RAG system")
            self.rag.insert(text_content)

            logger.info(f"Successfully processed and inserted {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return False

    def scan_and_process_directory(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """Scan a directory and process all files.

        Args:
            directory: Directory to scan (defaults to input_dir)

        Returns:
            Dict with results of processing
        """
        directory = directory or self.input_dir
        results = {"success": [], "failure": []}

        logger.info(f"Scanning directory: {directory}")

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)

                # Skip hidden files and directories
                if file.startswith('.') or any(part.startswith('.') for part in Path(file_path).parts):
                    continue

                # Process the file
                success = self.process_and_insert_file(file_path)

                if success:
                    results["success"].append(file_path)
                else:
                    results["failure"].append(file_path)

        logger.info(f"Processed {len(results['success'])} files successfully, {len(results['failure'])} failures")
        return results

    def query(
        self,
        query_text: str,
        mode: str = "hybrid",
        stream: bool = False
    ) -> Union[str, AsyncGenerator]:
        """
        Query the RAG system with a natural language question.

        This method sends a query to the LightRAG system and returns a response based on
        the documents that have been processed and indexed. Different query modes offer
        different retrieval strategies optimized for different types of questions.

        Args:
            query_text (str): The natural language query or question
            mode (str): Query mode to use. Options are:
                - "naive": Basic search without advanced techniques
                - "local": Focuses on context-dependent information within documents
                - "global": Utilizes global knowledge across all documents
                - "hybrid": Combines local and global retrieval methods
                - "mix": Integrates knowledge graph and vector retrieval
            stream (bool): Whether to stream the response (True) or return it all at once (False)

        Returns:
            Union[str, AsyncGenerator]:
                - If stream=False: A string containing the complete response
                - If stream=True: An async generator that yields response chunks as they're generated

        Raises:
            ValueError: If an invalid query mode is provided
            RuntimeError: If the RAG system is not initialized
        """
        if not self.rag:
            logger.error("RAG system not initialized. Call initialize() first.")
            return "Error: RAG system not initialized"

        # Validate mode
        valid_modes = ["naive", "local", "global", "hybrid", "mix"]
        if mode not in valid_modes:
            logger.warning(f"Invalid mode: {mode}. Using 'hybrid' instead.")
            mode = "hybrid"

        # Execute the query
        logger.info(f"Executing query in {mode} mode: {query_text}")
        return self.rag.query(
            query_text,
            param=QueryParam(mode=mode, stream=stream)
        )

async def print_stream(stream):
    """
    Print a streaming response from an async generator.

    This utility function consumes an async generator (stream) and prints each
    chunk as it's received, without adding newlines between chunks. This is useful
    for displaying streaming responses from the LLM in real-time.

    Args:
        stream: An async generator that yields string chunks

    Example:
        ```python
        stream = mfrag.query("Tell me about...", stream=True)
        await print_stream(stream)
        ```
    """
    async for chunk in stream:
        print(chunk, end="", flush=True)

async def create_multifilerag(
    working_dir: str = "./rag_storage",
    input_dir: str = "./inputs",
    llm_model_name: str = "llama3",
    embedding_model_name: str = "nomic-embed-text",
    ollama_host: str = "http://localhost:11434",
    log_level: str = "INFO"
) -> MultiFileRAG:
    """
    Create and initialize a MultiFileRAG instance in a single function call.

    This is a convenience function that creates a MultiFileRAG instance and
    initializes it in one step. It's useful when you want to quickly set up
    a MultiFileRAG instance without separate creation and initialization steps.

    Args:
        working_dir: Directory for storing RAG data
        input_dir: Directory containing input files
        llm_model_name: Name of the Ollama LLM model
        embedding_model_name: Name of the Ollama embedding model
        ollama_host: URL of the Ollama server
        log_level: Logging level

    Returns:
        MultiFileRAG: An initialized MultiFileRAG instance ready to use

    Example:
        ```python
        mfrag = await create_multifilerag(
            llm_model_name="deepseek-r1:32b",
            embedding_model_name="bge-m3"
        )
        response = mfrag.query("What's in my documents?")
        ```
    """
    mfrag = MultiFileRAG(
        working_dir=working_dir,
        input_dir=input_dir,
        llm_model_name=llm_model_name,
        embedding_model_name=embedding_model_name,
        ollama_host=ollama_host,
        log_level=log_level
    )
    await mfrag.initialize()
    return mfrag

def main():
    """
    Example usage of MultiFileRAG as a standalone application.

    This function demonstrates how to use MultiFileRAG to process documents and
    perform queries. It reads configuration from environment variables, initializes
    the MultiFileRAG instance, processes documents in the input directory, and
    tests different query modes.

    This is intended as a demonstration and can be run directly with:
    ```
    python multifilerag_core.py
    ```
    """
    # Get environment variables or use defaults
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    input_dir = os.getenv("INPUT_DIR", "./inputs")

    # Get model settings from environment variables
    llm_model_name = os.getenv("LLM_MODEL", "llama3")
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # Get Ollama host from environment variable
    ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")

    print(f"Using LLM model: {llm_model_name}")
    print(f"Using embedding model: {embedding_model_name}")

    # Create and initialize MultiFileRAG
    mfrag = asyncio.run(create_multifilerag(
        working_dir=working_dir,
        input_dir=input_dir,
        llm_model_name=llm_model_name,
        embedding_model_name=embedding_model_name,
        ollama_host=ollama_host
    ))

    # Scan and process the input directory
    results = mfrag.scan_and_process_directory()

    # Print results
    print(f"\nProcessed {len(results['success'])} files successfully")
    print(f"Failed to process {len(results['failure'])} files")

    if results['success']:
        # Test query in different modes
        print("\nTesting queries in different modes:")

        for mode in ["naive", "local", "global", "hybrid", "mix"]:
            print(f"\n{mode.capitalize()} mode query:")
            response = mfrag.query("What are the main topics in these documents?", mode=mode)
            print(response)

        # Test streaming
        print("\nStreaming response:")
        stream = mfrag.query("Summarize the key points from all documents.", mode="mix", stream=True)
        if asyncio.iscoroutine(stream) or hasattr(stream, '__aiter__'):
            asyncio.run(print_stream(stream))
        else:
            print(stream)

if __name__ == "__main__":
    main()
