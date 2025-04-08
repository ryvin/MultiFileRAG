#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import nest_asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import json

# Apply nest_asyncio to allow nested event loops (needed for Jupyter notebooks)
nest_asyncio.apply()

# Import LightRAG components
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc, logger
from lightrag.kg.shared_storage import initialize_pipeline_status

# Import our file processors
from multifile_processor import (
    extract_text_from_pdf,
    extract_text_from_csv,
    extract_text_from_image,
    process_file
)

class MultiFileRAG:
    """MultiFileRAG class that integrates LightRAG with PDF, CSV, and image processing."""
    
    def __init__(
        self,
        working_dir: str = "./rag_storage",
        input_dir: str = "./inputs",
        llm_model_name: str = "llama3",
        embedding_model_name: str = "nomic-embed-text",
        ollama_host: str = "http://localhost:11434",
        log_level: str = "INFO"
    ):
        """Initialize the MultiFileRAG instance.
        
        Args:
            working_dir: Directory for storing RAG data
            input_dir: Directory containing input files
            llm_model_name: Name of the Ollama LLM model
            embedding_model_name: Name of the Ollama embedding model
            ollama_host: URL of the Ollama server
            log_level: Logging level
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
        """Initialize the LightRAG instance."""
        # Determine embedding dimension based on model
        embedding_dim = 768  # Default for nomic-embed-text
        if self.embedding_model_name == "bge-m3":
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
            self.rag.insert(text_content, description=f"Content from {os.path.basename(file_path)}")
            
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
    ) -> Union[str, asyncio.AsyncGenerator]:
        """Query the RAG system.
        
        Args:
            query_text: The query text
            mode: Query mode (naive, local, global, hybrid, mix)
            stream: Whether to stream the response
            
        Returns:
            String response or async generator for streaming
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
    """Print a streaming response."""
    async for chunk in stream:
        print(chunk, end="", flush=True)

# Helper function to initialize and return a MultiFileRAG instance
async def create_multifilerag(
    working_dir: str = "./rag_storage",
    input_dir: str = "./inputs",
    llm_model_name: str = "llama3",
    embedding_model_name: str = "nomic-embed-text",
    ollama_host: str = "http://localhost:11434",
    log_level: str = "INFO"
) -> MultiFileRAG:
    """Create and initialize a MultiFileRAG instance."""
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

# Example usage
def main():
    # Get environment variables or use defaults
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    input_dir = os.getenv("INPUT_DIR", "./inputs")
    llm_model_name = os.getenv("LLM_MODEL", "llama3")
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    ollama_host = os.getenv("LLM_BINDING_HOST", "http://localhost:11434")
    
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
