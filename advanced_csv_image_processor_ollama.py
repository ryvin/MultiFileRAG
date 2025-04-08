import os
import sys
import asyncio
import tempfile
import shutil
import textract
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
WORKING_DIR = "./advanced_rag_data"
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)

# Create a directory for generated visualizations
VISUALIZATIONS_DIR = os.path.join(WORKING_DIR, "visualizations")
if not os.path.exists(VISUALIZATIONS_DIR):
    os.makedirs(VISUALIZATIONS_DIR)

# Set up logging
setup_logger("lightrag", level="INFO")

# Function to extract text from CSV files with enhanced analysis
def extract_text_from_csv(file_path):
    """Extract text from CSV files with enhanced analysis."""
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
            stats.append(f"  - Standard Deviation: {df[column].std()}")
        
        # Add correlation analysis for numeric columns
        corr_analysis = []
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            corr_matrix = df.select_dtypes(include=[np.number]).corr()
            corr_analysis.append("Correlation Analysis:")
            
            # Find strong correlations
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:  # Only report strong correlations
                        strength = "strong positive" if corr_value > 0.7 else "moderate positive" if corr_value > 0 else "strong negative" if corr_value < -0.7 else "moderate negative"
                        corr_analysis.append(f"  - {col1} and {col2} have a {strength} correlation ({corr_value:.2f})")
        
        # Generate visualizations for the data
        visualization_paths = generate_visualizations(df, os.path.basename(file_path))
        
        # Combine all information
        full_text = f"CSV File Content:\n{csv_text}\n\nColumn Descriptions:\n"
        full_text += "\n".join(column_descriptions)
        
        if stats:
            full_text += "\n\nStatistical Information:\n" + "\n".join(stats)
        
        if corr_analysis:
            full_text += "\n\n" + "\n".join(corr_analysis)
        
        if visualization_paths:
            full_text += "\n\nVisualizations Generated:\n"
            for desc, path in visualization_paths:
                full_text += f"  - {desc}: {path}\n"
        
        return full_text
    except Exception as e:
        print(f"Error extracting text from CSV {file_path}: {e}")
        return None

# Function to generate visualizations for CSV data
def generate_visualizations(df, base_filename):
    """Generate visualizations for the CSV data."""
    visualization_paths = []
    
    try:
        # Set the style for the plots
        sns.set(style="whitegrid")
        
        # 1. Generate histogram for each numeric column
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for column in numeric_columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(df[column], kde=True)
            plt.title(f'Distribution of {column}')
            plt.xlabel(column)
            plt.ylabel('Frequency')
            
            # Save the plot
            filename = f"{base_filename.split('.')[0]}_{column}_histogram.png"
            filepath = os.path.join(VISUALIZATIONS_DIR, filename)
            plt.savefig(filepath)
            plt.close()
            
            visualization_paths.append((f"Histogram of {column}", filepath))
        
        # 2. Generate scatter plots for pairs of numeric columns (limit to first 3 columns to avoid too many plots)
        if len(numeric_columns) > 1:
            for i in range(min(3, len(numeric_columns))):
                for j in range(i+1, min(3, len(numeric_columns))):
                    col1 = numeric_columns[i]
                    col2 = numeric_columns[j]
                    
                    plt.figure(figsize=(10, 6))
                    sns.scatterplot(x=df[col1], y=df[col2])
                    plt.title(f'Scatter Plot: {col1} vs {col2}')
                    plt.xlabel(col1)
                    plt.ylabel(col2)
                    
                    # Save the plot
                    filename = f"{base_filename.split('.')[0]}_{col1}_vs_{col2}_scatter.png"
                    filepath = os.path.join(VISUALIZATIONS_DIR, filename)
                    plt.savefig(filepath)
                    plt.close()
                    
                    visualization_paths.append((f"Scatter plot of {col1} vs {col2}", filepath))
        
        # 3. Generate a correlation heatmap if there are multiple numeric columns
        if len(numeric_columns) > 1:
            plt.figure(figsize=(10, 8))
            corr_matrix = df[numeric_columns].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
            plt.title('Correlation Matrix')
            
            # Save the plot
            filename = f"{base_filename.split('.')[0]}_correlation_heatmap.png"
            filepath = os.path.join(VISUALIZATIONS_DIR, filename)
            plt.savefig(filepath)
            plt.close()
            
            visualization_paths.append(("Correlation heatmap", filepath))
        
        # 4. Generate a bar plot for categorical columns (if any)
        categorical_columns = df.select_dtypes(include=['object']).columns
        for column in categorical_columns[:2]:  # Limit to first 2 categorical columns
            if df[column].nunique() <= 10:  # Only for columns with a reasonable number of categories
                plt.figure(figsize=(12, 6))
                value_counts = df[column].value_counts()
                sns.barplot(x=value_counts.index, y=value_counts.values)
                plt.title(f'Count of {column} Categories')
                plt.xlabel(column)
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                
                # Save the plot
                filename = f"{base_filename.split('.')[0]}_{column}_barplot.png"
                filepath = os.path.join(VISUALIZATIONS_DIR, filename)
                plt.savefig(filepath)
                plt.close()
                
                visualization_paths.append((f"Bar plot of {column} categories", filepath))
        
        return visualization_paths
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        return visualization_paths

# Function to extract text description from an image with enhanced analysis
def extract_text_from_image(file_path):
    """Create a detailed text description of an image."""
    try:
        # Open the image
        img = Image.open(file_path)
        
        # Get basic image information
        width, height = img.size
        format_type = img.format
        mode = img.mode
        
        # Calculate aspect ratio
        aspect_ratio = width / height
        
        # Analyze color distribution
        color_analysis = ""
        if mode == "RGB" or mode == "RGBA":
            # Convert image to RGB if it's RGBA
            if mode == "RGBA":
                img = img.convert("RGB")
            
            # Get color histogram
            hist = img.histogram()
            r_hist = hist[0:256]
            g_hist = hist[256:512]
            b_hist = hist[512:768]
            
            # Calculate average RGB values
            total_pixels = width * height
            r_avg = sum(i * count for i, count in enumerate(r_hist)) / total_pixels
            g_avg = sum(i * count for i, count in enumerate(g_hist)) / total_pixels
            b_avg = sum(i * count for i, count in enumerate(b_hist)) / total_pixels
            
            color_analysis = f"Color Analysis:\n"
            color_analysis += f"  - Average RGB: ({r_avg:.1f}, {g_avg:.1f}, {b_avg:.1f})\n"
            
            # Determine dominant color range
            if r_avg > g_avg and r_avg > b_avg:
                color_analysis += "  - Dominant color range: Red\n"
            elif g_avg > r_avg and g_avg > b_avg:
                color_analysis += "  - Dominant color range: Green\n"
            elif b_avg > r_avg and b_avg > g_avg:
                color_analysis += "  - Dominant color range: Blue\n"
            else:
                color_analysis += "  - No dominant color range\n"
            
            # Determine if image is bright or dark
            brightness = (r_avg + g_avg + b_avg) / 3
            if brightness > 200:
                color_analysis += "  - Image is very bright\n"
            elif brightness > 150:
                color_analysis += "  - Image is bright\n"
            elif brightness > 100:
                color_analysis += "  - Image has moderate brightness\n"
            elif brightness > 50:
                color_analysis += "  - Image is dark\n"
            else:
                color_analysis += "  - Image is very dark\n"
        
        # Create a text description
        image_description = f"Image Information:\n"
        image_description += f"Filename: {os.path.basename(file_path)}\n"
        image_description += f"Format: {format_type}\n"
        image_description += f"Mode: {mode}\n"
        image_description += f"Dimensions: {width} x {height} pixels\n"
        image_description += f"Aspect Ratio: {aspect_ratio:.2f}\n"
        image_description += f"File Size: {os.path.getsize(file_path) / 1024:.1f} KB\n"
        
        if color_analysis:
            image_description += f"\n{color_analysis}"
        
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
        print(f"First 200 characters: {csv_content[:200]}..." if len(csv_content) > 200 else csv_content)
        
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
        print(f"Description: {image_description[:200]}..." if len(image_description) > 200 else image_description)
        
        # Insert the image description into LightRAG
        rag.insert(image_description, ids=[file_id])
        return True
    else:
        print(f"Failed to extract description from image {file_path}")
        return False

def create_sample_csv(temp_dir):
    """Create a sample CSV file for demonstration."""
    csv_path = os.path.join(temp_dir, "employee_data.csv")
    
    # Create sample data
    data = {
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Davis', 
                'Eva Wilson', 'Frank Miller', 'Grace Lee', 'Henry Taylor', 'Ivy Martinez'],
        'Age': [30, 28, 35, 42, 25, 33, 45, 29, 38, 31],
        'Department': ['Engineering', 'Data Science', 'Project Management', 'Marketing', 'Design', 
                      'Engineering', 'Finance', 'Data Science', 'Sales', 'Customer Support'],
        'Salary': [85000, 92000, 105000, 110000, 78000, 88000, 120000, 95000, 82000, 75000],
        'Years_Experience': [5, 4, 10, 15, 3, 7, 18, 5, 12, 6],
        'Performance_Score': [4.2, 4.5, 3.8, 4.7, 3.9, 4.1, 4.3, 4.6, 3.5, 4.0]
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
        if await process_csv(rag, csv_path, "employee_data.csv"):
            processed_files.append("employee_data.csv")
        
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
            
            # Query about the CSV data - basic information
            print("\nQuery about the CSV data (basic information):")
            print(
                rag.query(
                    "What departments are represented in the employee data and how many employees are in each?", 
                    param=QueryParam(mode="mix")
                )
            )
            
            # Query about the CSV data - statistical analysis
            print("\nQuery about the CSV data (statistical analysis):")
            print(
                rag.query(
                    "What is the relationship between years of experience and salary? Is there a correlation?", 
                    param=QueryParam(mode="mix")
                )
            )
            
            # Query about the CSV data - insights
            print("\nQuery about the CSV data (insights):")
            print(
                rag.query(
                    "Based on the employee data, what insights can you provide about performance scores across different departments?", 
                    param=QueryParam(mode="mix")
                )
            )
            
            # Query about the image
            print("\nQuery about the image:")
            print(
                rag.query(
                    "Describe the image in detail, including its dimensions, format, and color characteristics.", 
                    param=QueryParam(mode="mix")
                )
            )
            
            # Query about all processed files
            print("\nQuery about all processed files:")
            print(
                rag.query(
                    "Summarize all the information that has been processed, including both the employee data and the image.", 
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
