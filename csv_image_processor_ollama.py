import os
import sys
import asyncio
import tempfile
import shutil
import textract
import requests
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO, StringIO
from pathlib import Path

# Add LightRAG to the Python path
sys.path.append(r"C:\Users\raul\Documents\augment-projects\LightRAG")

from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc, setup_logger
from lightrag.kg.shared_storage import initialize_pipeline_status

# Set up working directory
WORKING_DIR = "./csv_image_rag_data"
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)

# Set up logging
setup_logger("lightrag", level="INFO")

# Function to extract text from CSV files
def extract_text_from_csv(file_path):
    """Extract text from CSV files."""
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path)
        
        # Convert DataFrame to a string representation
        csv_text = df.to_string(index=False)
        
        # Add column descriptions
        column_descriptions = []
        for column in df.columns:
            column_descriptions.append(f"Column '{column}': Contains {df[column].dtype} values")
        
        # Add basic statistics for numeric columns
        stats = []
        for column in df.select_dtypes(include=[np.number]).columns:
            stats.append(f"Statistics for '{column}':")
            stats.append(f"  - Min: {df[column].min()}")
            stats.append(f"  - Max: {df[column].max()}")
            stats.append(f"  - Mean: {df[column].mean()}")
            stats.append(f"  - Median: {df[column].median()}")
        
        # Combine all information
        full_text = f"CSV File Content:\n{csv_text}\n\nColumn Descriptions:\n"
        full_text += "\n".join(column_descriptions)
        
        if stats:
            full_text += "\n\nStatistical Information:\n" + "\n".join(stats)
        
        return full_text
    except Exception as e:
        print(f"Error extracting text from CSV {file_path}: {e}")
        return None

# Function to extract text description from an image
def extract_text_from_image(file_path):
    """Create a text description of an image."""
    try:
        # Open the image
        img = Image.open(file_path)
        
        # Get basic image information
        width, height = img.size
        format_type = img.format
        mode = img.mode
        
        # Create a text description
        image_description = f"Image Information:\n"
        image_description += f"Filename: {os.path.basename(file_path)}\n"
        image_description += f"Format: {format_type}\n"
        image_description += f"Mode: {mode}\n"
        image_description += f"Dimensions: {width} x {height} pixels\n"
        
        # Note: In a real application, you might want to use a computer vision model
        # to generate a more detailed description of the image content
        
        return image_description
    except Exception as e:
        print(f"Error extracting information from image {file_path}: {e}")
        return None

# Function to download a file from a URL
def download_file(url, output_path):
    """Download a file from a URL to the specified output path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")
        return False

async def initialize_rag():
    """Initialize the LightRAG instance with Ollama."""
    # Initialize LightRAG with Ollama model
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,  # Use Ollama model for text generation
        llm_model_name='llama3',  # Specify the Ollama model to use
        llm_model_kwargs={"options": {"num_ctx": 32768}},  # Increase context window
        # Use Ollama embedding function
        embedding_func=EmbeddingFunc(
            embedding_dim=768,  # Dimension for nomic-embed-text
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts,
                embed_model="nomic-embed-text"  # Use nomic-embed-text for embeddings
            )
        ),
    )

    # Initialize storages and pipeline status
    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

async def process_csv(rag, file_path, file_id=None):
    """Process a CSV file and add it to the RAG system."""
    if file_id is None:
        file_id = os.path.basename(file_path)
    
    print(f"\n=== Processing CSV file: {file_id} ===")
    csv_content = extract_text_from_csv(file_path)
    
    if csv_content:
        print(f"Successfully extracted text from CSV {file_path}")
        print(f"First 100 characters: {csv_content[:100]}..." if len(csv_content) > 100 else csv_content)
        
        # Insert the extracted text into LightRAG
        rag.insert(csv_content, ids=[file_id])
        return True
    else:
        print(f"Failed to extract text from CSV {file_path}")
        return False

async def process_image(rag, file_path, file_id=None):
    """Process an image file and add its description to the RAG system."""
    if file_id is None:
        file_id = os.path.basename(file_path)
    
    print(f"\n=== Processing image file: {file_id} ===")
    image_description = extract_text_from_image(file_path)
    
    if image_description:
        print(f"Successfully extracted description from image {file_path}")
        print(f"Description: {image_description[:100]}..." if len(image_description) > 100 else image_description)
        
        # Insert the image description into LightRAG
        rag.insert(image_description, ids=[file_id])
        return True
    else:
        print(f"Failed to extract description from image {file_path}")
        return False

def create_sample_csv(temp_dir):
    """Create a sample CSV file for demonstration."""
    csv_path = os.path.join(temp_dir, "sample_data.csv")
    
    # Create sample data
    data = {
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
        'Age': [30, 28, 35, 42, 25],
        'Occupation': ['Software Engineer', 'Data Scientist', 'Project Manager', 'Marketing Director', 'UX Designer'],
        'Salary': [85000, 92000, 105000, 110000, 78000],
        'Years_Experience': [5, 4, 10, 15, 3]
    }
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    
    return csv_path

async def main():
    # Initialize RAG instance
    rag = await initialize_rag()
    
    # Create a temporary directory for files
    temp_dir = tempfile.mkdtemp()
    try:
        processed_files = []
        
        # Create and process a sample CSV file
        csv_path = create_sample_csv(temp_dir)
        if await process_csv(rag, csv_path, "sample_data.csv"):
            processed_files.append("sample_data.csv")
        
        # Download and process a sample image
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/SNice.svg/1200px-SNice.svg.png"
        image_path = os.path.join(temp_dir, "sample_image.png")
        
        print(f"\n=== Downloading image from {image_url} ===")
        if download_file(image_url, image_path):
            print(f"Successfully downloaded image to {image_path}")
            if await process_image(rag, image_path, "sample_image.png"):
                processed_files.append("sample_image.png")
        else:
            print(f"Failed to download image from {image_url}")
        
        # Run queries if files were processed
        if processed_files:
            print(f"\n=== Files processed: {', '.join(processed_files)} ===")
            
            # Query about the CSV data
            print("\nQuery about the CSV data (Mix mode):")
            print(
                rag.query(
                    "What occupations are listed in the CSV file and what are their average salaries?", 
                    param=QueryParam(mode="mix")
                )
            )
            
            # Query about the image
            print("\nQuery about the image (Mix mode):")
            print(
                rag.query(
                    "What are the dimensions and format of the image?", 
                    param=QueryParam(mode="mix")
                )
            )
            
            # Query about all processed files
            print("\nQuery about all processed files (Mix mode):")
            print(
                rag.query(
                    "What types of files have been processed and what information do they contain?", 
                    param=QueryParam(mode="mix")
                )
            )
        else:
            print("\n=== No files were processed ===")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    asyncio.run(main())
