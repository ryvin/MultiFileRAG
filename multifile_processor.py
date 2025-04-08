import os
import argparse
import json
from pathlib import Path

# Required dependencies
import pandas as pd
import numpy as np
from PIL import Image

# Optional dependencies
textract = None
PyPDF2 = None

try:
    import PyPDF2
except ImportError:
    print("Warning: PyPDF2 not installed. PDF processing will be limited.")

try:
    import textract
except ImportError:
    print("Warning: textract not installed. Text extraction from some file types will be limited.")

def extract_text_from_pdf(file_path):
    """Extract text from PDF files."""
    text_content = ""

    # Check if PyPDF2 is available
    if PyPDF2 is not None:
        try:
            # First try with PyPDF2
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n\n"

            # Add metadata about the PDF
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                info = pdf_reader.metadata
                if info:
                    metadata_text = f"PDF Metadata:\n"
                    for key, value in info.items():
                        if key.startswith('/'):
                            key = key[1:]
                        metadata_text += f"{key}: {value}\n"
                    metadata_text += f"Number of pages: {len(pdf_reader.pages)}\n\n"
                    metadata_text += "PDF Content:\n"
                    text_content = metadata_text + text_content
        except Exception as e:
            print(f"Error extracting text from PDF with PyPDF2 {file_path}: {e}")
            text_content = ""

    # If PyPDF2 didn't extract much text or is not available, try textract as a fallback
    if (len(text_content.strip()) < 100) and (textract is not None):
        try:
            text_content = textract.process(file_path).decode('utf-8')
        except Exception as e2:
            print(f"Error with textract fallback: {e2}")
            if len(text_content.strip()) == 0:
                return None

    # If we have some content, return it
    if len(text_content.strip()) > 0:
        return text_content

    # If we got here, we couldn't extract any text
    print(f"Could not extract text from PDF {file_path}")
    return None

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

        # Combine all information
        full_text = f"CSV File Content:\n{csv_text}\n\nColumn Descriptions:\n"
        full_text += "\n".join(column_descriptions)

        if stats:
            full_text += "\n\nStatistical Information:\n" + "\n".join(stats)

        if corr_analysis:
            full_text += "\n\n" + "\n".join(corr_analysis)

        return full_text
    except Exception as e:
        print(f"Error extracting text from CSV {file_path}: {e}")
        return None

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

        return image_description
    except Exception as e:
        print(f"Error extracting information from image {file_path}: {e}")
        return None

def process_file(file_path):
    """Process a file based on its extension."""
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in ['.pdf']:
        print(f"Processing PDF file: {file_path}")
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.csv']:
        print(f"Processing CSV file: {file_path}")
        return extract_text_from_csv(file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        print(f"Processing image file: {file_path}")
        return extract_text_from_image(file_path)
    elif file_extension in ['.txt', '.md', '.text']:
        print(f"Processing text file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return None
    else:
        # For other file types, try textract if available
        if textract is not None:
            try:
                print(f"Processing file with textract: {file_path}")
                return textract.process(file_path).decode('utf-8')
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                return None
        else:
            print(f"Cannot process file {file_path}: textract not installed")
            return None

def process_directory(directory_path, output_directory=None):
    """Process all files in a directory."""
    if output_directory is None:
        output_directory = os.path.join(directory_path, "processed")

    os.makedirs(output_directory, exist_ok=True)

    results = {}

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Skip files in the output directory
            if os.path.abspath(file_path).startswith(os.path.abspath(output_directory)):
                continue

            # Process the file
            text_content = process_file(file_path)

            if text_content:
                # Save the processed content
                output_file = os.path.join(output_directory, f"{os.path.splitext(file)[0]}.txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text_content)

                results[file] = {
                    "status": "success",
                    "output_file": output_file,
                    "size": len(text_content)
                }
            else:
                results[file] = {
                    "status": "error",
                    "message": "Failed to process file"
                }

    # Save the results
    results_file = os.path.join(output_directory, "processing_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

def main():
    parser = argparse.ArgumentParser(description="Process PDF, CSV, and image files for LightRAG")
    parser.add_argument("--input", required=True, help="Input file or directory")
    parser.add_argument("--output", help="Output directory (default: ./processed)")

    args = parser.parse_args()

    if os.path.isfile(args.input):
        # Process a single file
        output_dir = args.output or "./processed"
        os.makedirs(output_dir, exist_ok=True)

        text_content = process_file(args.input)

        if text_content:
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(args.input))[0]}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text_content)

            print(f"Successfully processed {args.input}")
            print(f"Output saved to {output_file}")
        else:
            print(f"Failed to process {args.input}")

    elif os.path.isdir(args.input):
        # Process a directory
        output_dir = args.output or os.path.join(args.input, "processed")
        results = process_directory(args.input, output_dir)

        # Print summary
        success_count = sum(1 for result in results.values() if result["status"] == "success")
        error_count = sum(1 for result in results.values() if result["status"] == "error")

        print(f"\nProcessing complete!")
        print(f"Successfully processed: {success_count} files")
        print(f"Failed to process: {error_count} files")
        print(f"Results saved to {os.path.join(output_dir, 'processing_results.json')}")

    else:
        print(f"Input path {args.input} does not exist")

if __name__ == "__main__":
    main()
