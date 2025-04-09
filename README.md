# MultiFileRAG

A specialized implementation of LightRAG for processing multiple file types including PDF, CSV, and image files, powered by local LLMs through Ollama. MultiFileRAG provides a complete solution for document analysis, retrieval, and question answering using local large language models.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Powered-green.svg)](https://ollama.ai/)

## Overview

MultiFileRAG extends the capabilities of [LightRAG](https://github.com/HKUDS/LightRAG) to provide enhanced data analysis, visualization, and querying capabilities across different file formats. It's designed to work with local LLMs through Ollama, making it ideal for privacy-conscious applications and offline use cases.

The system uses a Retrieval-Augmented Generation (RAG) approach to:
1. Process and index documents from various file formats
2. Create embeddings for efficient semantic search
3. Build knowledge graphs to represent relationships between document chunks
4. Provide natural language querying capabilities
5. Generate contextually relevant responses based on your documents

## Features

- **Local LLM Integration**:
  - Uses Ollama to run models locally without relying on external APIs
  - Supports multiple LLM models including DeepSeek, Llama, Mistral, and more
  - Configurable model selection through environment variables

- **Multiple File Type Support**:
  - **Enhanced PDF Processing**: Extract text and metadata from PDF files with multiple methods (PyPDF2, unstructured, pdfplumber)
  - **Robust PDF Handling**: Automatically handle problematic PDFs that cause errors in standard processors
  - **CSV Processing**: Extract text, statistics, and insights from CSV files with correlation analysis
  - **Image Processing**: Extract metadata and descriptions from image files
  - **Text Files**: Process plain text files (.txt, .md) with formatting preservation
  - **Office Documents**: Support for Word, Excel, PowerPoint files (with unstructured library)

- **Advanced Embedding & Retrieval**:
  - Multiple embedding models (nomic-embed-text, bge-m3, etc.)
  - Vector database for semantic search
  - Knowledge graph representation of document relationships
  - Multiple retrieval strategies optimized for different query types

- **Advanced Querying**:
  - Query across multiple file types using LightRAG's various modes
  - Support for complex queries with context awareness
  - Streaming responses for faster feedback

- **User Interfaces**:
  - **Web UI**: User-friendly interface for uploading files and querying the system
  - **CLI Interface**: Command-line tools for processing files and querying the system
  - **Python API**: Programmatic access for integration with other applications

- **Advanced Database Support**:
  - **PostgreSQL with pgvector**: Store vectors and key-value data with optimized similarity search
  - **Neo4j Graph Database**: Store and query complex relationships between entities
  - **Redis Cache Layer**: Fast in-memory cache for frequently accessed data
  - **Hybrid Cache System**: Two-level cache with Redis (speed) and PostgreSQL (persistence)
  - **Node.js API**: RESTful API for accessing document data and query history
  - **Docker Support**: Easy setup with Docker Compose for all database services

- **Utilities & Debugging**:
  - **Centralized Utilities**: Comprehensive utilities module for common operations
  - **Monitoring Tools**: Real-time monitoring of document processing
  - **Diagnostic Scripts**: Tools for checking system status and troubleshooting
  - **Unit Tests**: Test suite for verifying functionality

## Installation

### Prerequisites

- **Python**: Version 3.10 or higher
- **Ollama**: Installed and running (for local LLM support)
  - [Install Ollama](https://ollama.ai/download) for your platform
  - Start Ollama with `ollama serve`
- **Git**: For cloning the repository
- **Conda** (recommended): For managing the Python environment

### Setup Options

MultiFileRAG offers multiple setup options depending on your preferences:

#### Option 1: Using Conda (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MultiFileRAG.git
   cd MultiFileRAG
   ```

2. Run the setup script to create a conda environment:
   ```bash
   python setup_conda.py
   ```
   This script will:
   - Check if conda is installed
   - Create a conda environment named 'multifilerag'
   - Install all required dependencies
   - Check if Ollama is running
   - Pull required models if needed
   - Create necessary directories

3. Activate the conda environment:
   ```bash
   conda activate multifilerag
   ```

#### Option 2: Using pip

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MultiFileRAG.git
   cd MultiFileRAG
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install LightRAG with API support:
   ```bash
   python install_lightrag.py
   ```

5. Install additional dependencies for enhanced file processing:
   ```bash
   # For PDF processing
   pip install PyPDF2

   # For additional file type support
   pip install "unstructured[all-docs]"

   # For async support
   pip install nest_asyncio
   ```

### Model Setup

MultiFileRAG requires two types of models from Ollama:

1. **LLM Model** for text generation (default: deepseek-r1:32b)
2. **Embedding Model** for document indexing (default: nomic-embed-text)

Pull these models using Ollama:

```bash
# Pull the LLM model
ollama pull deepseek-r1:32b

# Pull the embedding model
ollama pull nomic-embed-text
```

You can configure which models to use in the `.env` file.

## Usage

### Database Setup

MultiFileRAG supports PostgreSQL with pgvector for vector storage, PostgreSQL for key-value storage, Neo4j for graph database, and Redis for caching. The system automatically manages these databases:

1. Make sure Docker Desktop is installed and running
2. Start the MultiFileRAG server normally:

```powershell
.\start_multifilerag_server.bat
```

The server will automatically:
- Check if database services are running
- Start any missing database services using Docker Compose
- Initialize the databases with required tables, indexes, and extensions
- Configure the hybrid cache system (Redis + PostgreSQL)

#### Manual Database Management

You can also manage the databases manually using these scripts:

- **Start Databases**: `start_databases.bat`
- **Stop Databases**: `stop_databases.bat`
- **Restart Databases**: `restart_databases.bat`
- **Check Status**: `check_database_status.bat`

#### Disabling Database Auto-Start

If you want to start the server without automatically starting the databases:

```powershell
.\start_multifilerag_server.bat --no-db-autostart
```

### Starting the Server Without Databases

MultiFileRAG provides a web interface for easy interaction with the system. To start the server:

```bash
# Using the batch file (Windows)
start_multifilerag_server.bat

# Or using Python directly
python multifilerag_server.py
```

Then open your browser and navigate to `http://localhost:9621` to access the web interface.

> **Note for Windows Users**: All PowerShell scripts (.ps1) have been converted to batch files (.bat) for better compatibility with CMD. Use the .bat files instead of the .ps1 files.

### Web Interface

The web interface provides a user-friendly way to interact with MultiFileRAG:

1. **Upload Documents**:
   - Click the "Upload" button to select files
   - Supported formats: PDF, CSV, TXT, DOCX, XLSX, PPTX, JPG, PNG, etc.
   - Files are stored in the `inputs` directory

2. **Process Documents**:
   - Click "Process" to index uploaded documents
   - The system will extract text, create embeddings, and build a knowledge graph
   - Processing status is displayed in real-time

3. **Query Documents**:
   - Enter your question in the query box
   - Select a query mode (naive, local, global, hybrid, mix)
   - Click "Submit" to get a response
   - Results show the answer along with source documents and relevance scores

4. **View Document List**:
   - See all processed documents
   - Check processing status and metadata
   - Delete documents if needed

### CLI Interface

The MultiFileRAG CLI provides commands for processing files and querying the system:

1. **Process Files**:
   ```bash
   python multifilerag_cli.py process
   ```
   This will process all files in the `inputs` directory.

   To process a specific file:
   ```bash
   python multifilerag_cli.py process --file inputs/your_file.txt
   ```

2. **Query the System**:
   ```bash
   python multifilerag_cli.py query "Your question here"
   ```

   You can specify a query mode:
   ```bash
   python multifilerag_cli.py query "Your question here" --mode mix
   ```

### Python API

You can also use MultiFileRAG programmatically in your Python code:

```python
import asyncio
from multifilerag_core import MultiFileRAG, create_multifilerag
from multifilerag_utils import get_document_counts, check_ollama_status

async def main():
    # Check if Ollama is running
    ollama_running, version = check_ollama_status()
    if not ollama_running:
        print(f"Error: Ollama is not running: {version}")
        return

    # Initialize MultiFileRAG using the convenience function
    mfrag = await create_multifilerag(
        working_dir="./rag_storage",
        input_dir="./inputs",
        llm_model_name="deepseek-r1:32b",
        embedding_model_name="nomic-embed-text"
    )

    # Process a file
    await mfrag.process_and_insert_file("./inputs/your_document.pdf")

    # Check document counts
    counts = get_document_counts()
    print(f"Document counts: {counts}")

    # Query the system
    response = mfrag.query("What is in the document?", mode="mix")
    print(response)

# Run the async function
asyncio.run(main())
```

## Configuration

### Environment Variables

MultiFileRAG uses a `.env` file for configuration. The main settings include:

```
# Server Configuration
HOST=0.0.0.0
PORT=9621

# LLM Configuration
LLM_BINDING=ollama
# Available models: llama3, llama3:8b, llama3:70b, mistral, mixtral, phi3, gemma, deepseek-r1:32b, etc.
LLM_MODEL=deepseek-r1:32b
LLM_BINDING_HOST=http://localhost:11434

# Embedding Configuration
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://localhost:11434
# Available models: nomic-embed-text, bge-m3, bge-small-en-v1.5, etc.
# Note: bge-m3 requires EMBEDDING_DIM=1024
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768

# Working Directory
WORKING_DIR=./rag_storage
INPUT_DIR=./inputs

# Database Configuration
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_GRAPH_STORAGE=PGGraphStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DATABASE=multifilerag

# Node.js Database Configuration
NODEJS_DB_HOST=localhost
NODEJS_DB_PORT=3000
NODEJS_DB_USER=admin
NODEJS_DB_PASSWORD=admin
NODEJS_DB_NAME=multifilerag_nodejs
```

### Changing Models

To change the LLM or embedding model:

1. Edit the `.env` file to set the desired model names
2. For embedding models with different dimensions (e.g., switching to bge-m3):
   - Stop the server
   - Run `python clear_vector_db.py` to clear the vector database
   - Update the `.env` file with the new model and dimension
   - Restart the server
   - Re-process your documents

### Recommended Model Combinations

- **High Performance**: deepseek-r1:32b + bge-m3
- **Balanced**: llama3 + nomic-embed-text
- **Lightweight**: phi3 + bge-small-en-v1.5

### Database Configuration

MultiFileRAG supports a comprehensive database setup with PostgreSQL (pgvector), Neo4j, and Redis:

1. Make sure Docker Desktop is installed and running
2. Update the `.env` file with the appropriate storage implementations:
   ```
   # Key-value storage with hybrid cache (Redis + PostgreSQL)
   LIGHTRAG_KV_STORAGE=HybridKVStorage
   # Vector storage with pgvector extension
   LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
   # Graph storage with Neo4j
   LIGHTRAG_GRAPH_STORAGE=Neo4jStorage
   # Document status storage with PostgreSQL
   LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
   # Cache storage with hybrid implementation
   LIGHTRAG_CACHE_STORAGE=HybridCacheStorage
   ```
3. Configure the database connections in the `.env` file:
   ```
   # PostgreSQL Configuration
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DATABASE=multifilerag

   # Neo4j Configuration
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=multifilerag

   # Redis Configuration
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_TTL=3600
   ```
4. Start the database containers using Docker Compose:
   ```powershell
   docker-compose up -d
   ```
5. Start the MultiFileRAG server with database support:
   ```powershell
   .\start_multifilerag_with_db.ps1
   ```

#### Data Processing Flow

The system uses the following data processing flow:

**Document Ingestion:**
- Documents are chunked into manageable pieces
- LLM extracts entities and relationships
- Embedding model converts chunks to vectors
- Data is stored in respective databases (PostgreSQL for vectors and key-value, Neo4j for graphs)

**Query Processing:**
- User query is analyzed to identify entities and keywords
- Query is converted to vector representation
- Vector similarity search finds relevant chunks using pgvector
- Graph traversal identifies related entities and relationships using Neo4j
- Results from both approaches are combined and ranked

**Answer Generation:**
- Retrieved context is formatted and sent to LLM
- LLM generates response based on retrieved information
- Results are cached in the hybrid cache system (Redis + PostgreSQL) for similar future queries

## Query Modes

MultiFileRAG supports various query modes inherited from LightRAG, each optimized for different types of questions and document sets:

### Available Query Modes

- **naive**:
  - Basic search without advanced techniques
  - Directly retrieves chunks based on vector similarity
  - Fast but less accurate for complex queries
  - Best for: Simple factual questions, small document sets
  - Example query: "What is the revenue for Q2 2023?"

- **local**:
  - Focuses on context-dependent information within documents
  - Retrieves chunks and their surrounding context
  - Good for specific factual queries requiring context
  - Best for: Questions about specific details within documents
  - Example query: "What were the key findings in the security audit?"

- **global**:
  - Utilizes global knowledge across all documents
  - Considers document-level relationships and metadata
  - Better for general questions spanning multiple documents
  - Best for: Broad questions, trend analysis, comparisons
  - Example query: "How have sales trends changed over the past year?"

- **hybrid**:
  - Combines local and global retrieval methods
  - Balances specificity and breadth of information
  - Good balance between accuracy and comprehensive results
  - Best for: Complex questions requiring both specific details and broader context
  - Example query: "What factors contributed to the decline in customer satisfaction and how do they relate to product changes?"

- **mix**:
  - Integrates knowledge graph and vector retrieval
  - Leverages entity relationships and semantic similarity
  - Most comprehensive but potentially slower
  - Best for: Complex questions involving relationships between entities
  - Example query: "How do the financial performance metrics relate to the organizational changes described in the annual report?"

### Optimizing Query Mode Selection

For best results:

1. **Start with hybrid mode** for most queries
2. **Use mix mode** when you need to understand relationships between entities
3. **Use local mode** for specific factual questions about a particular document
4. **Use global mode** for questions that span multiple documents
5. **Use naive mode** when you need quick results for simple questions

### Customizing TOP_K Parameter

The TOP_K parameter controls how many documents are retrieved for each query. Increasing this value will make the system consider more documents, potentially providing more comprehensive answers at the cost of processing time.

You can adjust this in the web UI under Query Settings.

## System Architecture

### Directory Structure

```
MultiFileRAG/
├── inputs/                  # Place your files here for processing
├── rag_storage/             # Storage for the processed data
│   ├── backup/              # Backup directory for vector database files
│   ├── graph_*.graphml      # Knowledge graph files
│   ├── kv_store_*.json      # Key-value stores for document data
│   └── vdb_*.json           # Vector database files
├── .env                     # Environment variables and configuration
├── .gitignore               # Git ignore file (excludes data files)
├── clear_vector_db.py       # Utility to clear vector database
├── direct_server.py         # Alternative server implementation
├── install_lightrag.py      # Script to install LightRAG
├── multifile_processor.py   # File processing utilities
├── multifilerag_cli.py      # Command-line interface
├── multifilerag_core.py     # Core functionality
├── multifilerag_server.py   # Web server
├── requirements.txt         # Python dependencies
├── setup_conda.py           # Conda environment setup script
└── start_multifilerag_server.bat  # Batch file to start the server
```

### Component Overview

1. **Core Components**:
   - `multifilerag_core.py`: The main class that integrates LightRAG with file processing
   - `multifile_processor.py`: Handles different file types and extracts text and metadata
   - `multifilerag_server.py`: Provides the web server and API endpoints

2. **Storage System**:
   - Vector Database: Stores document embeddings for semantic search
   - Knowledge Graph: Represents relationships between document chunks
   - Key-Value Stores: Maintains document content, metadata, and processing status

3. **Processing Pipeline**:
   - Document Ingestion: Files are uploaded to the inputs directory
   - Text Extraction: Content is extracted based on file type
   - Chunking: Documents are split into manageable chunks
   - Embedding: Chunks are converted to vector embeddings
   - Indexing: Embeddings are stored in the vector database
   - Knowledge Graph Construction: Relationships between chunks are identified

4. **Query Pipeline**:
   - Query Embedding: User query is converted to a vector
   - Retrieval: Relevant document chunks are retrieved based on query mode
   - Context Assembly: Retrieved chunks are assembled into context
   - Response Generation: LLM generates a response based on context and query

## File Processing Capabilities

MultiFileRAG uses the unstructured library for document processing, providing robust support for various file types:

### PDF Files
- Text extraction with layout preservation
- Support for multi-page documents
- Metadata extraction (author, creation date, etc.)
- Table detection and extraction
- Image extraction and processing
- OCR for scanned documents
- Fallback mechanisms for different extraction methods

### CSV Files
- Statistical analysis (min, max, mean, median, standard deviation)
- Correlation analysis between numeric columns
- Column type detection and description
- Outlier detection
- Data distribution analysis
- Summary generation with key insights
- Handling of large files with chunking

### Office Documents
- **Word (.docx, .doc)**:
  - Text extraction with formatting preservation
  - Table extraction
  - Header/footer processing
- **Excel (.xlsx, .xls)**:
  - Multi-sheet support
  - Formula interpretation
  - Named range handling
- **PowerPoint (.pptx, .ppt)**:
  - Slide content extraction
  - Notes extraction
  - Shape and text box handling

### Image Files
- Metadata extraction (dimensions, format, mode, EXIF data)
- Color analysis and dominant color detection
- Brightness and contrast assessment
- Aspect ratio calculation
- Basic content description
- Text extraction from images (OCR)

### Text Files
- Direct text extraction
- Support for different encodings (UTF-8, UTF-16, etc.)
- Markdown file support with structure preservation
- Code file handling with syntax awareness
- Large file chunking strategies

## Example Workflow

Here's a typical workflow for using MultiFileRAG:

1. **Start the server**:
   ```bash
   python multifilerag_server.py
   ```

2. **Upload documents**:
   - Place files in the `inputs` directory, or
   - Use the web UI to upload files

3. **Process documents**:
   - Through the web UI: Click "Process" button
   - Via CLI: `python multifilerag_cli.py process`

4. **Query your documents**:
   - Through the web UI: Enter question in the query box
   - Via CLI: `python multifilerag_cli.py query "Your question here"`

5. **Analyze results**:
   - Review the generated response
   - Check source documents and relevance scores
   - Refine your query if needed

## Troubleshooting

### Common Issues and Solutions

#### Installation Problems

- **Missing Dependencies**:
  ```
  Error: No module named 'xyz'
  ```
  **Solution**:
  - Install the required dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```
  - For specific modules, install them directly:
    ```bash
    pip install unstructured PyPDF2 pandas nest_asyncio
    ```

- **LightRAG Installation Fails**:
  ```
  Error importing LightRAG modules
  ```
  **Solution**:
  - Run the installation script with the correct Python environment:
    ```bash
    python install_lightrag.py
    ```
  - Check if you have Git installed (required for installation)
  - Ensure you have proper permissions to install packages

- **Conda Environment Issues**:
  ```
  CommandNotFoundError: Your shell has not been properly configured to use 'conda activate'.
  ```
  **Solution**:
  - Initialize conda for your shell:
    ```bash
    # For PowerShell
    conda-init

    # For Bash
    conda init bash
    ```
  - Or use the full path to conda:
    ```bash
    C:\ProgramData\anaconda3\Scripts\conda.exe activate multifilerag
    ```

#### Server Issues

- **Ollama Connection Error**:
  ```
  Error: Ollama server is not running
  ```
  **Solution**:
  - Start Ollama in a separate terminal:
    ```bash
    ollama serve
    ```
  - Check if Ollama is installed correctly
  - Verify network settings if using a remote Ollama server

- **Port Already in Use**:
  ```
  Error: Address already in use
  ```
  **Solution**:
  - Change the port in the .env file:
    ```
    PORT=9622  # Change from default 9621
    ```
  - Find and stop the process using the port:
    ```bash
    # Windows
    netstat -ano | findstr :9621
    taskkill /PID <PID> /F

    # Linux/Mac
    lsof -i :9621
    kill -9 <PID>
    ```

- **Server Crashes or Hangs**:
  **Solution**:
  - Check system resources (CPU, RAM, disk space)
  - Reduce MAX_PARALLEL_INSERT in .env to 1
  - Increase TIMEOUT value for large documents
  - Restart both Ollama and the MultiFileRAG server

#### Model Issues

- **Model Not Found**:
  ```
  Error: Failed to get model "deepseek-r1:32b"
  ```
  **Solution**:
  - Pull the required model using Ollama:
    ```bash
    ollama pull deepseek-r1:32b
    ollama pull nomic-embed-text
    ```
  - Check internet connection (required for initial model download)
  - Verify disk space (models can be several GB)

- **Embedding Dimension Mismatch**:
  ```
  Error: Embedding dim mismatch, expected: 1024, but loaded: 768
  ```
  **Solution**:
  - Clear the vector database and restart with consistent dimensions:
    ```bash
    python clear_vector_db.py
    ```
  - Update the .env file with the correct dimension:
    ```
    # For bge-m3
    EMBEDDING_MODEL=bge-m3
    EMBEDDING_DIM=1024

    # For nomic-embed-text
    EMBEDDING_MODEL=nomic-embed-text
    EMBEDDING_DIM=768
    ```

- **Model Timeout Issues**:
  ```
  Error: Request timed out after 200 seconds
  ```
  **Solution**:
  - Increase the timeout in .env:
    ```
    TIMEOUT=600  # Increase from default
    ```
  - Use a smaller model if you don't have GPU acceleration
  - Reduce MAX_PARALLEL_INSERT to 1 to avoid resource contention

#### File Processing Issues

- **File Processing Fails**:
  ```
  Error processing file: xyz.pdf
  ```
  **Solution**:
  - Check file format and encoding (UTF-8 recommended)
  - Ensure file is not corrupted or password-protected
  - Install enhanced PDF processing dependencies:
    ```bash
    python install_pdf_dependencies.py
    # Or run the batch file
    install_pdf_dependencies.bat
    ```
  - For specific file types, install additional dependencies:
    ```bash
    pip install "unstructured[pdf]"
    pip install "unstructured[docx]"
    ```

- **PDF Processing Errors (list index out of range)**:
  ```
  IndexError: list index out of range
  ```
  **Solution**:
  - This is a common error with certain PDF files that have non-standard formatting
  - The system now automatically handles these files using alternative methods
  - If you're still encountering issues, install the enhanced PDF dependencies:
    ```bash
    python install_pdf_dependencies.py
    ```
  - The system will automatically try multiple methods (PyPDF2, unstructured, pdfplumber) to extract text

- **Memory Errors During Processing**:
  ```
  MemoryError or Out of memory
  ```
  **Solution**:
  - Reduce the chunk size in the .env file
  - Process smaller files or split large files
  - Increase system swap space
  - Close other memory-intensive applications

- **Knowledge Graph Issues**:
  ```
  No entities found in knowledge graph
  ```
  **Solution**:
  - Ensure documents contain recognizable entities
  - Try reprocessing documents with a different LLM model
  - Check if the LLM model has sufficient context window
  - Use the "mix" query mode to leverage both vector search and knowledge graph

### Advanced Debugging

#### Checking Document Status

To check the status of documents in the system:

```bash
python check_docs.py
```

This will show which documents are pending, processing, processed, or failed.

#### Monitoring Processing

To monitor document processing in real-time:

```bash
python monitor_processing.py
```

This will continuously update with the current pipeline status and document counts.

#### Reprocessing Failed Documents

To reprocess documents that failed:

```bash
python reprocess_docs.py
```

This will identify failed documents and reprocess them.

#### Using the Utilities Module

The `multifilerag_utils.py` module provides a comprehensive set of utilities for interacting with the system. You can import and use these functions in your own scripts:

```python
from multifilerag_utils import get_server_url, get_documents, check_ollama_status

# Get server URL from environment variables
server_url = get_server_url()

# Check if Ollama is running
is_running, version = check_ollama_status()
if is_running:
    print(f"Ollama is running. Version: {version}")
else:
    print(f"Ollama is not running: {version}")

# Get document status
docs = get_documents(server_url)
if docs:
    print(f"Found {len(docs.get('statuses', {}).get('PROCESSED', []))} processed documents")
```

See the `test_multifilerag_utils.py` file for examples of how to use the utilities module.

### General Debugging Tips

1. **Check Logs**: Look for error messages in the terminal output
2. **Verify Models**: Ensure the required models are pulled in Ollama
3. **Check File Permissions**: Ensure the application has read/write access to the directories
4. **Restart Services**: Sometimes restarting Ollama and the MultiFileRAG server resolves issues
5. **Clean Installation**: In case of persistent issues, try a fresh installation
6. **Update Dependencies**: Ensure all dependencies are up to date
7. **Check System Resources**: Monitor CPU, RAM, and disk usage during processing
8. **Test with Smaller Files**: Verify functionality with smaller, simpler files first

## Project Structure

The MultiFileRAG project is organized into several key components:

### Core Components

- **multifilerag_core.py**: The main module that provides the MultiFileRAG class and core functionality
- **multifilerag_server.py**: Web server implementation for the REST API
- **multifilerag_cli.py**: Command-line interface for processing files and querying
- **multifilerag_utils.py**: Shared utilities for API interaction, Ollama status checking, and file operations
- **multifile_processor.py**: File processing utilities for different file types

### Utility Scripts

- **check_docs.py**: Check the status of documents in the system
- **check_document_content.py**: Check if specific documents were properly processed and their content is available
- **clear_vector_db.py**: Clear the vector database to start fresh
- **monitor_processing.py**: Monitor document processing in real-time
- **reprocess_docs.py**: Reprocess failed documents

### Setup Scripts

- **install_dependencies.py**: Install required Python dependencies
- **install_lightrag.py**: Install LightRAG from source
- **setup_conda.py**: Set up a Conda environment for MultiFileRAG
- **setup_multifilerag_server.py**: Set up and configure the MultiFileRAG server
- **setup_ollama.py**: Set up Ollama and pull required models

### Advanced Processing

- **advanced_csv_image_processor_ollama.py**: Advanced processing for CSV and image files
- **optimize_for_cpu.py**: Optimize settings for CPU-only environments
- **prepare_files.py**: Prepare files for processing

### Tests

- **test_multifilerag_utils.py**: Unit tests for the utilities module

## Performance Optimization

### Hardware Recommendations

- **CPU**: 4+ cores recommended for parallel processing
- **RAM**: 16GB minimum, 32GB+ recommended for large documents
- **Storage**: SSD recommended for faster vector database operations
- **GPU**: Optional but beneficial for faster LLM inference with Ollama

### Software Optimization

- **Model Selection**: Choose models based on your hardware capabilities
  - For lower-end hardware: Use smaller models like phi3 or llama3:8b
  - For high-end hardware: Use larger models like deepseek-r1:32b

- **Embedding Dimension**: Balance between accuracy and performance
  - Lower dimensions (384): Faster but less accurate
  - Higher dimensions (1024): More accurate but requires more resources

- **Chunk Size**: Adjust based on your documents and queries
  - Smaller chunks: Better for specific queries, less context
  - Larger chunks: Better for contextual understanding, more resource-intensive

- **Parallel Processing**: Configure MAX_PARALLEL_INSERT in .env for optimal performance

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the [LightRAG](https://github.com/HKUDS/LightRAG) project by HKUDS
- Uses [Ollama](https://github.com/ollama/ollama) for local LLM support
- Uses [unstructured](https://github.com/Unstructured-IO/unstructured) for document processing

## Recent Improvements

The MultiFileRAG codebase has undergone significant refactoring and improvements:

### Code Refactoring

- **Centralized Utilities**: Created a comprehensive `multifilerag_utils.py` module that consolidates common functionality
- **Reduced Redundancy**: Eliminated duplicate code across multiple scripts
- **Standardized Error Handling**: Implemented consistent error handling patterns
- **Improved Documentation**: Added detailed docstrings and comments

### Code Cleanup

- **Removed Redundant Files**: Deleted unnecessary and redundant scripts
- **Organized Imports**: Standardized import organization across files
- **Fixed Line Length Issues**: Improved code formatting for better readability
- **Added Unit Tests**: Created a test suite for the utilities module

### Benefits

- **Improved Maintainability**: Cleaner code structure makes maintenance easier
- **Better Error Handling**: More specific error messages help with debugging
- **Enhanced Documentation**: Better documentation makes the codebase more accessible
- **Easier Testing**: Centralized functions are easier to test

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
