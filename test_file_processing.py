import os
from multifile_processor import process_file

# Create a simple text file for testing
test_file_path = "test_upload.txt"
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write("This is a test file for MultiFileRAG.")

# Process the file
print(f"Processing test file: {test_file_path}")
result = process_file(test_file_path)

if result:
    print("File processed successfully!")
    print(f"Content: {result}")
else:
    print("Failed to process file!")

# Clean up
os.remove(test_file_path)
