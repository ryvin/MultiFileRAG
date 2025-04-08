# MultiFileRAG

A specialized implementation of LightRAG for processing multiple file types including PDF, CSV, and image files, powered by local LLMs through Ollama. MultiFileRAG provides a complete solution for document analysis, retrieval, and question answering using local large language models.

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
  - **PDF Processing**: Extract text and metadata from PDF files with structure preservation
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

### Starting the Server

MultiFileRAG provides a web interface for easy interaction with the system. To start the server:

```bash
# Using the batch file (Windows)
start_multifilerag_server.bat

# Or using Python directly
python multifilerag_server.py
```

Then open your browser and navigate to `http://localhost:9621` to access the web interface.

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
from multifilerag_core import MultiFileRAG

async def main():
    # Initialize MultiFileRAG
    mfrag = MultiFileRAG(
        working_dir="./rag_storage",
        input_dir="./inputs",
        llm_model_name="deepseek-r1:32b",
        embedding_model_name="nomic-embed-text"
    )
    await mfrag.initialize()

    # Process a file
    mfrag.process_and_insert_file("./inputs/your_document.pdf")

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

## Query Modes

MultiFileRAG supports various query modes inherited from LightRAG:

- **naive**: Basic search without advanced techniques. Fast but less accurate.
- **local**: Focuses on context-dependent information within documents. Good for specific factual queries.
- **global**: Utilizes global knowledge across all documents. Better for general questions.
- **hybrid**: Combines local and global retrieval methods. Balances specificity and breadth.
- **mix**: Integrates knowledge graph and vector retrieval. Recommended for most cases as it provides the most comprehensive results.

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

### Common Issues

#### Installation Problems

- **Missing Dependencies**:
  ```
  Error: No module named 'xyz'
  ```
  Solution: Install the required dependencies using pip:
  ```bash
  pip install -r requirements.txt
  ```

- **LightRAG Installation Fails**:
  ```
  Error importing LightRAG modules
  ```
  Solution: Run the installation script with the correct Python environment:
  ```bash
  python install_lightrag.py
  ```

#### Server Issues

- **Ollama Connection Error**:
  ```
  Error: Ollama server is not running
  ```
  Solution: Start Ollama in a separate terminal:
  ```bash
  ollama serve
  ```

- **Port Already in Use**:
  ```
  Error: Address already in use
  ```
  Solution: Change the port in the .env file or stop the process using that port.

#### Model Issues

- **Model Not Found**:
  ```
  Error: Failed to get model
  ```
  Solution: Pull the required model using Ollama:
  ```bash
  ollama pull deepseek-r1:32b
  ollama pull nomic-embed-text
  ```

- **Embedding Dimension Mismatch**:
  ```
  Error: Embedding dim mismatch, expected: 1024, but loaded: 768
  ```
  Solution: Clear the vector database and restart with consistent dimensions:
  ```bash
  python clear_vector_db.py
  ```
  Then update the .env file with the correct dimension.

#### File Processing Issues

- **File Processing Fails**:
  ```
  Error processing file: xyz.pdf
  ```
  Solution:
  - Check file format and encoding (UTF-8 recommended)
  - Ensure file is not corrupted or password-protected
  - Try converting the file to a different format

- **Memory Errors During Processing**:
  ```
  MemoryError or Out of memory
  ```
  Solution: Reduce the chunk size in the .env file or process smaller files.

### Debugging Tips

1. **Check Logs**: Look for error messages in the terminal output
2. **Verify Models**: Ensure the required models are pulled in Ollama
3. **Check File Permissions**: Ensure the application has read/write access to the directories
4. **Restart Services**: Sometimes restarting Ollama and the MultiFileRAG server resolves issues
5. **Clean Installation**: In case of persistent issues, try a fresh installation

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
