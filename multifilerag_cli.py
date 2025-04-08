#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import argparse
from pathlib import Path
import inspect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=False)

# Import our MultiFileRAG core
from multifilerag_core import MultiFileRAG, create_multifilerag, print_stream

async def process_files(args):
    """Process files and add them to the RAG system."""
    # Create and initialize MultiFileRAG
    mfrag = await create_multifilerag(
        working_dir=args.working_dir,
        input_dir=args.input_dir,
        llm_model_name=args.llm_model,
        embedding_model_name=args.embedding_model,
        ollama_host=args.ollama_host,
        log_level=args.log_level
    )
    
    # Process files
    if args.file:
        # Process a single file
        success = mfrag.process_and_insert_file(args.file)
        if success:
            print(f"✅ Successfully processed and inserted {args.file}")
        else:
            print(f"❌ Failed to process {args.file}")
    else:
        # Process all files in the input directory
        results = mfrag.scan_and_process_directory()
        print(f"\n✅ Processed {len(results['success'])} files successfully")
        if results['failure']:
            print(f"❌ Failed to process {len(results['failure'])} files:")
            for file in results['failure']:
                print(f"  - {file}")

async def query_rag(args):
    """Query the RAG system."""
    # Create and initialize MultiFileRAG
    mfrag = await create_multifilerag(
        working_dir=args.working_dir,
        input_dir=args.input_dir,
        llm_model_name=args.llm_model,
        embedding_model_name=args.embedding_model,
        ollama_host=args.ollama_host,
        log_level=args.log_level
    )
    
    # Execute the query
    print(f"Querying in {args.mode} mode: {args.query}")
    response = mfrag.query(args.query, mode=args.mode, stream=args.stream)
    
    # Handle streaming response
    if args.stream and (inspect.isasyncgen(response) or hasattr(response, '__aiter__')):
        await print_stream(response)
    else:
        print(response)

def main():
    parser = argparse.ArgumentParser(description="MultiFileRAG CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Common arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--working-dir", default=os.getenv("WORKING_DIR", "./rag_storage"), help="Working directory for RAG storage")
    common_parser.add_argument("--input-dir", default=os.getenv("INPUT_DIR", "./inputs"), help="Directory containing input documents")
    common_parser.add_argument("--llm-model", default=os.getenv("LLM_MODEL", "llama3"), help="LLM model name")
    common_parser.add_argument("--embedding-model", default=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"), help="Embedding model name")
    common_parser.add_argument("--ollama-host", default=os.getenv("LLM_BINDING_HOST", "http://localhost:11434"), help="Ollama host URL")
    common_parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"), help="Logging level")
    
    # Process command
    process_parser = subparsers.add_parser("process", parents=[common_parser], help="Process files and add them to the RAG system")
    process_parser.add_argument("--file", help="Process a specific file (if not specified, processes all files in input-dir)")
    
    # Query command
    query_parser = subparsers.add_parser("query", parents=[common_parser], help="Query the RAG system")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument("--mode", default="hybrid", choices=["naive", "local", "global", "hybrid", "mix"], help="Query mode")
    query_parser.add_argument("--stream", action="store_true", help="Stream the response")
    
    args = parser.parse_args()
    
    if args.command == "process":
        asyncio.run(process_files(args))
    elif args.command == "query":
        asyncio.run(query_rag(args))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
