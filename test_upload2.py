import os
import requests
import sys
from pathlib import Path
import time

def test_upload(file_path, server_url="http://localhost:9621"):
    """Test uploading a file to the MultiFileRAG server."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Create the upload endpoint URL
    upload_url = f"{server_url}/documents/upload"
    
    # Prepare the file for upload
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        
        # Send the request
        print(f"Uploading {file_path} to {upload_url}...")
        try:
            response = requests.post(upload_url, files=files)
            
            # Check the response
            if response.status_code == 200:
                print(f"Success: {response.json()}")
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Exception during upload: {e}")
            return False

def create_test_file():
    """Create a simple test file."""
    timestamp = int(time.time())
    test_file_path = f"test_document_{timestamp}.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("This is a test document for MultiFileRAG.")
    return test_file_path

if __name__ == "__main__":
    # Create a test file if no file is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = create_test_file()
        print(f"Created test file: {file_path}")
    
    # Test uploading the file
    test_upload(file_path)
