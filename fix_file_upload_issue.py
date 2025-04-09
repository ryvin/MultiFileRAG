#!/usr/bin/env python3
"""
Fix File Upload Issue

This script fixes the issue with file uploads reporting that files already exist.
"""

import os
import json
import requests
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_postgres_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "multifilerag"),
            database=os.getenv("POSTGRES_DATABASE", "multifilerag")
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return None

def check_file_exists(file_path):
    """Check if a file exists in the document status table."""
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if the file exists
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM lightrag_doc_status
                WHERE file_path = %s
            """, (file_path,))
            result = cursor.fetchone()
            return result['count'] > 0
    except Exception as e:
        logger.error(f"Error checking if file exists: {e}")
        return False
    finally:
        conn.close()

def delete_file(file_path):
    """Delete a file from the document status table."""
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return False

    try:
        with conn.cursor() as cursor:
            # Delete the file
            cursor.execute("""
                DELETE FROM lightrag_doc_status
                WHERE file_path = %s
            """, (file_path,))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False
    finally:
        conn.close()

def list_all_files():
    """List all files in the document status table."""
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get all file paths
            cursor.execute("""
                SELECT id, file_path, status
                FROM lightrag_doc_status
                ORDER BY file_path
            """)
            files = cursor.fetchall()
            return files
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return []
    finally:
        conn.close()

def main():
    """Main function."""
    logger.info("Fixing file upload issue...")
    
    # List all files
    files = list_all_files()
    if not files:
        logger.info("No files found in the document status table.")
        return
    
    logger.info(f"Found {len(files)} files in the document status table:")
    for file in files:
        logger.info(f"ID: {file['id']}, Path: {file['file_path']}, Status: {file['status']}")
    
    # Ask for a file path to delete
    file_path = input("\nEnter the file path to delete (or 'q' to quit): ")
    if file_path.lower() == 'q':
        logger.info("No changes made.")
        return
    
    # Check if the file exists
    if check_file_exists(file_path):
        logger.info(f"File '{file_path}' exists in the document status table.")
        
        # Ask for confirmation
        confirm = input(f"Are you sure you want to delete '{file_path}'? (y/n): ")
        if confirm.lower() != 'y':
            logger.info("No changes made.")
            return
        
        # Delete the file
        if delete_file(file_path):
            logger.info(f"File '{file_path}' deleted successfully.")
        else:
            logger.error(f"Failed to delete file '{file_path}'.")
    else:
        logger.info(f"File '{file_path}' does not exist in the document status table.")

if __name__ == "__main__":
    main()
