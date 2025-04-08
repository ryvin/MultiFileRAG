# MultiFileRAG

A specialized implementation of LightRAG for processing multiple file types including PDF, CSV, and image files, powered by local LLMs through Ollama.

## Overview

MultiFileRAG extends the capabilities of LightRAG to provide enhanced data analysis, visualization, and querying capabilities across different file formats. It's designed to work with local LLMs through Ollama, making it ideal for privacy-conscious applications and offline use cases.

## Features

- **Local LLM Integration**: Uses Ollama to run models locally without relying on external APIs
- **Multiple File Type Support**:
  - **PDF Processing**: Extract text and metadata from PDF files
  - **CSV Processing**: Extract text, statistics, and insights from CSV files with correlation analysis
  - **Image Processing**: Extract metadata and descriptions from image files
  - **Text Files**: Process plain text files (.txt, .md)
- **Advanced Querying**: Query across multiple file types using LightRAG's various modes
- **Web UI**: User-friendly interface for uploading files and querying the system
- **CLI Interface**: Command-line tools for processing files and querying the system

## Installation

### Prerequisites

- Python 3.10 or higher
- Ollama installed and running (for local LLM support)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MultiFileRAG.git
   cd MultiFileRAG
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install optional dependencies for enhanced file processing:
   ```bash
   # For PDF processing
   pip install PyPDF2

   # For additional file type support (optional)
   pip install "unstructured[all-docs]"

   # For async support
   pip install nest_asyncio
   ```

## Usage

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

### Web Interface

Start the web server:
```bash
python multifilerag_server.py
```

Then open your browser and navigate to `http://localhost:8000` to access the web interface.

## Query Modes

MultiFileRAG supports various query modes inherited from LightRAG:

- **naive**: Basic search without advanced techniques
- **local**: Focuses on context-dependent information
- **global**: Utilizes global knowledge
- **hybrid**: Combines local and global retrieval methods
- **mix**: Integrates knowledge graph and vector retrieval (recommended for most cases)

## Directory Structure

- `inputs/`: Place your files here for processing
- `rag_storage/`: Storage for the processed data
- `multifilerag_core.py`: Core functionality
- `multifilerag_cli.py`: Command-line interface
- `multifilerag_server.py`: Web server
- `multifile_processor.py`: File processing utilities

## Example Files

The repository includes example files in the `inputs` directory:

- `sample_document.txt`: Information about the MultiFileRAG system
- `employee_data.csv`: Sample employee data for CSV processing

## File Processing Capabilities

### PDF Files
- Text extraction with metadata
- Support for multi-page documents
- Fallback mechanisms for different extraction methods

### CSV Files
- Statistical analysis (min, max, mean, median, standard deviation)
- Correlation analysis between numeric columns
- Column type detection and description

### Image Files
- Metadata extraction (dimensions, format, mode)
- Color analysis
- Brightness detection
- Aspect ratio calculation

### Text Files
- Direct text extraction
- Support for different encodings
- Markdown file support

## Troubleshooting

- **Missing Dependencies**: If you encounter errors about missing modules, install the required dependencies using pip.
- **File Processing Issues**: Make sure your files are in the correct format and encoding (UTF-8 recommended).
- **Ollama Connection**: Ensure Ollama is running and accessible.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the [LightRAG](https://github.com/HKUDS/LightRAG) project by HKUDS
- Uses [Ollama](https://github.com/ollama/ollama) for local LLM support
