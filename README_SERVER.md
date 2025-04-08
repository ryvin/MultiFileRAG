# MultiFileRAG Server

A specialized implementation of LightRAG for processing PDF, CSV, and image files with a web UI.

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

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure Ollama is installed and running:
   ```
   ollama serve
   ```

3. Pull the required models:
   ```
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

## Usage

### Using the Server

Start the MultiFileRAG server:

```
python multifilerag_server.py --auto-scan
```

Access the web UI at http://localhost:9621

### Using the CLI

Process files:
```
python multifilerag_cli.py process
```

Process a specific file:
```
python multifilerag_cli.py process --file path/to/file.pdf
```

Query the system:
```
python multifilerag_cli.py query "What are the main topics in these documents?"
```

Query with a specific mode:
```
python multifilerag_cli.py query "What are the main topics in these documents?" --mode mix
```

Stream the response:
```
python multifilerag_cli.py query "What are the main topics in these documents?" --stream
```

### Using the Batch File (Windows)

```
start_multifilerag.bat
```

## Query Modes

- **naive**: Basic search without advanced techniques
- **local**: Focuses on context-dependent information
- **global**: Utilizes global knowledge
- **hybrid**: Combines local and global retrieval methods
- **mix**: Integrates knowledge graph and vector retrieval (recommended for most cases)

## Troubleshooting

If you encounter any issues:

1. Make sure Ollama is running:
   ```
   ollama serve
   ```

2. Check if the required models are installed:
   ```
   ollama list
   ```

3. Verify that all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

4. Check the .env file for proper configuration

## License

This project is licensed under the MIT License.
