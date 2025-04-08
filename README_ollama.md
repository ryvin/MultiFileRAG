# MultiFileRAG

A specialized implementation of LightRAG for processing multiple file types including CSV files and images, using local LLMs via Ollama.

## Overview

MultiFileRAG extends the capabilities of [LightRAG](https://github.com/HKUDS/LightRAG) to work with various file types, with a special focus on CSV files and images. It provides enhanced data analysis, visualization, and querying capabilities, all powered by local LLMs through Ollama.

## Features

- **Local LLM Integration**: Uses Ollama to run models locally without relying on external APIs
- **CSV Processing**: Extract text, statistics, and insights from CSV files
- **Image Processing**: Extract metadata and descriptions from image files
- **Data Visualization**: Generate visualizations for CSV data
- **Advanced Querying**: Query across multiple file types using LightRAG's various modes

## Scripts

### 1. csv_image_processor_ollama.py

A basic script for processing CSV files and images with LightRAG using Ollama.

**Features:**
- Basic CSV text extraction with statistics
- Basic image metadata extraction
- Simple querying capabilities
- Ollama integration for local LLM processing

### 2. advanced_csv_image_processor_ollama.py

An advanced script with enhanced data analysis and visualization capabilities, using Ollama.

**Features:**
- Advanced CSV analysis with correlation detection
- Data visualization (histograms, scatter plots, correlation heatmaps)
- Enhanced image analysis with color distribution
- Comprehensive querying capabilities
- Ollama integration for local LLM processing

## Requirements

- Python 3.10+
- LightRAG (installed from the original repository)
- Ollama (installed and running locally)
- pandas
- numpy
- matplotlib
- seaborn
- Pillow
- unstructured
- requests

## Installation

1. Clone the LightRAG repository:
   ```
   git clone https://github.com/HKUDS/LightRAG.git
   ```

2. Install the required dependencies:
   ```
   pip install pandas numpy matplotlib seaborn Pillow textract requests
   ```

3. Install and set up Ollama:
   ```
   # Download and install Ollama from https://ollama.com/

   # Pull the required models
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

4. Copy the MultiFileRAG scripts to your working directory.

## Usage

### Basic CSV and Image Processing with Ollama

```python
python csv_image_processor_ollama.py
```

This will:
1. Create a sample CSV file with employee data
2. Download a sample image
3. Process both files with LightRAG using Ollama
4. Run several queries to demonstrate the capabilities

### Advanced CSV and Image Processing with Ollama

```python
python advanced_csv_image_processor_ollama.py
```

This will:
1. Create a sample CSV file with employee data
2. Download a sample image
3. Process both files with enhanced analysis using Ollama
4. Generate visualizations for the CSV data
5. Run comprehensive queries to demonstrate the advanced capabilities

## Customization

You can modify the scripts to:
- Use different Ollama models (change the `llm_model_name` parameter)
- Adjust the context window size (modify the `num_ctx` option)
- Process your own CSV files and images
- Customize the queries
- Add support for additional file types

## License

This project is licensed under the MIT License - see the LICENSE file for details.
