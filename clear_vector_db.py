#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get working directory from .env or use default
working_dir = os.getenv("WORKING_DIR", "./rag_storage")

def clear_vector_db():
    """Clear the vector database files to allow changing embedding dimensions."""
    # Create a backup directory
    backup_dir = Path(working_dir) / "backup"
    backup_dir.mkdir(exist_ok=True)

    # Get the current timestamp for the backup folder name
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}"
    backup_path.mkdir(exist_ok=True)

    # Check for vector database files
    vector_files = [
        "vdb_chunks.json",
        "vdb_entities.json",
        "vdb_relationships.json"
    ]

    found_files = False

    # Move vector database files to backup
    for filename in vector_files:
        file_path = Path(working_dir) / filename
        if file_path.exists():
            found_files = True
            shutil.copy2(str(file_path), str(backup_path / filename))
            print(f"  Backed up {filename}")
            # Remove the original file
            file_path.unlink()
            print(f"  Removed {filename}")

    if found_files:
        print(f"Vector database cleared. Backup created at {backup_path}")
        print("You can now change the embedding model and dimension in the .env file.")
    else:
        print(f"No vector database files found in {working_dir}")
        print("You can proceed with changing the embedding model and dimension.")

if __name__ == "__main__":
    clear_vector_db()
