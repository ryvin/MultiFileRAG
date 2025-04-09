#!/usr/bin/env python3
"""
Fix File Upload Issue

This script checks for duplicate file entries in the document status table
and provides options to fix them.
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=False)

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

def find_duplicate_files():
    """Find duplicate file entries in the document status table."""
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return None

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Find duplicate file paths
            cursor.execute("""
                SELECT file_path, COUNT(*) as count
                FROM lightrag_doc_status
                GROUP BY file_path
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            return duplicates
    except Exception as e:
        logger.error(f"Error finding duplicate files: {e}")
        return None
    finally:
        conn.close()

def list_all_files():
    """List all files in the document status table."""
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return None

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
        return None
    finally:
        conn.close()

def delete_document(doc_id):
    """Delete a document from the document status table."""
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return False

    try:
        with conn.cursor() as cursor:
            # Delete the document
            cursor.execute("""
                DELETE FROM lightrag_doc_status
                WHERE id = %s
            """, (doc_id,))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function."""
    logger.info("Checking for duplicate file entries...")
    
    # List all files
    files = list_all_files()
    if not files:
        logger.info("No files found in the document status table.")
        return
    
    logger.info(f"Found {len(files)} files in the document status table:")
    for file in files:
        logger.info(f"ID: {file['id']}, Path: {file['file_path']}, Status: {file['status']}")
    
    # Find duplicate files
    duplicates = find_duplicate_files()
    if not duplicates:
        logger.info("No duplicate file entries found.")
        return
    
    logger.info(f"Found {len(duplicates)} duplicate file entries:")
    for duplicate in duplicates:
        logger.info(f"File: {duplicate['file_path']}, Count: {duplicate['count']}")
    
    # Ask if user wants to delete duplicates
    choice = input("Do you want to delete duplicate entries? (y/n): ")
    if choice.lower() != 'y':
        logger.info("No changes made.")
        return
    
    # Delete duplicates
    for duplicate in duplicates:
        file_path = duplicate['file_path']
        logger.info(f"Processing duplicates for file: {file_path}")
        
        # Get all documents with this file path
        conn = get_postgres_connection()
        if not conn:
            logger.error("Failed to connect to PostgreSQL database.")
            continue
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, status
                    FROM lightrag_doc_status
                    WHERE file_path = %s
                    ORDER BY status
                """, (file_path,))
                docs = cursor.fetchall()
                
                # Keep the document with the highest status (processed > processing > pending)
                # Status order: pending < processing < processed
                status_order = {'pending': 0, 'processing': 1, 'processed': 2, 'failed': -1}
                docs_sorted = sorted(docs, key=lambda x: status_order.get(x['status'], -1), reverse=True)
                
                # Keep the first document (highest status)
                keep_doc = docs_sorted[0]
                logger.info(f"Keeping document with ID: {keep_doc['id']} (Status: {keep_doc['status']})")
                
                # Delete the rest
                for doc in docs_sorted[1:]:
                    logger.info(f"Deleting document with ID: {doc['id']} (Status: {doc['status']})")
                    delete_document(doc['id'])
        except Exception as e:
            logger.error(f"Error processing duplicates for file {file_path}: {e}")
        finally:
            conn.close()
    
    logger.info("Duplicate entries deleted successfully.")

if __name__ == "__main__":
    main()
