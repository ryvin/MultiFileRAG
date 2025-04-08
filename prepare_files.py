import os
import sys
import shutil
import argparse
from pathlib import Path
from multifile_processor import process_file

def copy_to_inputs(file_path, input_dir="./inputs"):
    """Copy a file to the inputs directory."""
    # Create inputs directory if it doesn't exist
    Path(input_dir).mkdir(parents=True, exist_ok=True)
    
    # Copy the file
    dest_path = os.path.join(input_dir, os.path.basename(file_path))
    shutil.copy2(file_path, dest_path)
    
    return dest_path

def process_and_copy(file_path, input_dir="./inputs"):
    """Process a file and copy it to the inputs directory."""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # If it's a PDF, CSV, or image, copy it directly
    if file_extension in ['.pdf', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        dest_path = copy_to_inputs(file_path, input_dir)
        print(f"Copied {file_path} to {dest_path}")
        return dest_path
    
    # For other file types, process them first
    text_content = process_file(file_path)
    
    if text_content:
        # Create a text file with the processed content
        output_file = os.path.join(input_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text_content)
        
        print(f"Processed {file_path} and saved to {output_file}")
        return output_file
    else:
        print(f"Failed to process {file_path}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Prepare files for LightRAG")
    parser.add_argument("--input", required=True, help="Input file or directory")
    parser.add_argument("--input-dir", default="./inputs", help="LightRAG input directory (default: ./inputs)")
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        # Process a single file
        process_and_copy(args.input, args.input_dir)
    
    elif os.path.isdir(args.input):
        # Process a directory
        processed_files = []
        failed_files = []
        
        for root, _, files in os.walk(args.input):
            for file in files:
                file_path = os.path.join(root, file)
                
                result = process_and_copy(file_path, args.input_dir)
                
                if result:
                    processed_files.append(file_path)
                else:
                    failed_files.append(file_path)
        
        # Print summary
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {len(processed_files)} files")
        print(f"Failed to process: {len(failed_files)} files")
        
        if failed_files:
            print("\nFailed files:")
            for file in failed_files:
                print(f"  - {file}")
    
    else:
        print(f"Input path {args.input} does not exist")
    
    print(f"\nTo start the LightRAG server and process these files, run:")
    print(f"  python start_server.py --auto-scan")

if __name__ == "__main__":
    main()
