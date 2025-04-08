# MultiFileRAG

A specialized implementation of LightRAG for processing PDF, CSV, and image files.

## Overview

MultiFileRAG extends the capabilities of [LightRAG](https://github.com/HKUDS/LightRAG) to work with various file types, with a special focus on PDF, CSV, and image files. It provides enhanced data analysis, visualization, and querying capabilities, all powered by local LLMs through Ollama.

## Features

- **Local LLM Integration**: Uses Ollama to run models locally without relying on external APIs
- **PDF Processing**: Extract text and insights from PDF files
- **CSV Processing**: Extract text, statistics, and insights from CSV files
- **Image Processing**: Extract metadata and descriptions from image files
- **Advanced Querying**: Query across multiple file types using LightRAG's various modes
- **Web UI**: User-friendly interface for uploading files and querying the system

## Installation

1. Run the setup script:
   ```
   python setup_multifilerag_server.py
   ```

2. This will:
   - Check if Ollama is running
   - Pull required Ollama models (llama3, nomic-embed-text)
   - Install LightRAG with API support
   - Install dependencies for PDF, CSV, and image processing
   - Create configuration files
   - Create sample files for demonstration

## Usage

### Preparing Files

You can prepare files for LightRAG using the `prepare_files.py` script:

```
python prepare_files.py --input your_files_directory
```

This will:
- Process PDF, CSV, and image files
- Copy them to the inputs directory
- Convert other file types to text if possible

### Starting the Server

Start the MultiFileRAG server:

```
python start_server.py --auto-scan
```

Access the web UI at:

```
http://localhost:9621
```

### Using the Web UI

1. Upload files:
   - Use the "Documents" tab to upload PDF, CSV, and image files
   - The system will automatically process the files and extract entities and relationships

2. Query the system:
   - Use the "Query" tab to ask questions about your documents
   - The system will return answers based on the extracted knowledge

### Query Modes

- **naive**: Basic search without advanced techniques
- **local**: Focuses on context-dependent information
- **global**: Utilizes global knowledge
- **hybrid**: Combines local and global retrieval methods
- **mix**: Integrates knowledge graph and vector retrieval (recommended for most cases)

## License

This project is licensed under the MIT License.
