#!/usr/bin/env python3
"""
Fix MultiFileRAG Issues

This script fixes various issues with the MultiFileRAG system:
1. Document status table schema issues
2. Missing files in the GUI
3. File upload issues
"""

import os
import sys
import json
import time
import logging
import psycopg2
import requests
import subprocess
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_postgres_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        # Use Docker container name as host
        conn = psycopg2.connect(
            host="multifilerag-postgres",
            port="5432",
            user="postgres",
            password="multifilerag",
            database="multifilerag"
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return None

def fix_document_status_schema():
    """Fix the document status table schema."""
    logger.info("Fixing document status table schema...")
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return False

    try:
        with conn.cursor() as cursor:
            # Check if the table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'lightrag_doc_status'
                );
            """)
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                logger.error("The lightrag_doc_status table does not exist.")
                return False

            # Get the current columns
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'lightrag_doc_status';
            """)
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            # Define the required columns and their types
            required_columns = {
                'id': 'character varying',
                'workspace': 'character varying',
                'content': 'text',
                'content_summary': 'text',
                'content_length': 'integer',
                'chunks_count': 'integer',
                'status': 'character varying',
                'file_path': 'text',
                'created_at': 'timestamp without time zone',
                'updated_at': 'timestamp without time zone'
            }

            # Check if any required columns are missing
            missing_columns = []
            for col_name, col_type in required_columns.items():
                if col_name not in column_names:
                    missing_columns.append((col_name, col_type))

            # Add missing columns
            for col_name, col_type in missing_columns:
                logger.info(f"Adding missing column: {col_name} ({col_type})")
                cursor.execute(f"""
                    ALTER TABLE lightrag_doc_status
                    ADD COLUMN {col_name} {col_type};
                """)

            # Check if content_summary is varchar(255) and change it to text if needed
            for col_name, col_type, max_length in columns:
                if col_name == 'content_summary' and col_type == 'character varying':
                    logger.info("Changing content_summary from varchar to text")
                    cursor.execute("""
                        ALTER TABLE lightrag_doc_status
                        ALTER COLUMN content_summary TYPE text;
                    """)

            conn.commit()

            # Update any NULL values
            cursor.execute("""
                UPDATE lightrag_doc_status
                SET content = COALESCE(content, 'Document content not available'),
                    content_summary = COALESCE(content_summary, 'Document content not available'),
                    content_length = COALESCE(content_length, 0),
                    chunks_count = COALESCE(chunks_count, 0)
                WHERE content IS NULL OR content_summary IS NULL OR content_length IS NULL OR chunks_count IS NULL;
            """)
            conn.commit()

            logger.info("Document status table schema fixed successfully.")
            return True
    except Exception as e:
        logger.error(f"Error fixing document status schema: {e}")
        return False
    finally:
        conn.close()

def fix_document_status_records():
    """Fix document status records."""
    logger.info("Fixing document status records...")
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return False

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if there are any records with NULL content or content_summary
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM lightrag_doc_status
                WHERE content IS NULL OR content_summary IS NULL
            """)
            result = cursor.fetchone()
            null_count = result['count']

            if null_count > 0:
                logger.info(f"Found {null_count} records with NULL content or content_summary.")

                # Update records with NULL content or content_summary
                cursor.execute("""
                    UPDATE lightrag_doc_status
                    SET content = COALESCE(content, 'Document content not available'),
                        content_summary = COALESCE(content_summary, 'Document content not available')
                    WHERE content IS NULL OR content_summary IS NULL
                """)
                conn.commit()
                logger.info(f"Updated {null_count} records.")
            else:
                logger.info("No records with NULL content or content_summary found.")

            # Check if there are any records with NULL content_length
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM lightrag_doc_status
                WHERE content_length IS NULL
            """)
            result = cursor.fetchone()
            null_length_count = result['count']

            if null_length_count > 0:
                logger.info(f"Found {null_length_count} records with NULL content_length.")

                # Update records with NULL content_length
                cursor.execute("""
                    UPDATE lightrag_doc_status
                    SET content_length = COALESCE(content_length, 0)
                    WHERE content_length IS NULL
                """)
                conn.commit()
                logger.info(f"Updated {null_length_count} records.")
            else:
                logger.info("No records with NULL content_length found.")

            logger.info("Document status records fixed successfully.")
            return True
    except Exception as e:
        logger.error(f"Error fixing document status records: {e}")
        return False
    finally:
        conn.close()

def fix_duplicate_files():
    """Fix duplicate file entries."""
    logger.info("Fixing duplicate file entries...")
    conn = get_postgres_connection()
    if not conn:
        logger.error("Failed to connect to PostgreSQL database.")
        return False

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

            if not duplicates:
                logger.info("No duplicate file entries found.")
                return True

            logger.info(f"Found {len(duplicates)} duplicate file entries:")
            for duplicate in duplicates:
                logger.info(f"File: {duplicate['file_path']}, Count: {duplicate['count']}")

                # Get all documents with this file path
                cursor.execute("""
                    SELECT id, status
                    FROM lightrag_doc_status
                    WHERE file_path = %s
                    ORDER BY status
                """, (duplicate['file_path'],))
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
                    cursor.execute("""
                        DELETE FROM lightrag_doc_status
                        WHERE id = %s
                    """, (doc['id'],))

            conn.commit()
            logger.info("Duplicate file entries fixed successfully.")
            return True
    except Exception as e:
        logger.error(f"Error fixing duplicate files: {e}")
        return False
    finally:
        conn.close()

def restart_databases():
    """Restart the database services."""
    logger.info("Restarting database services...")
    try:
        subprocess.run(["./restart_databases.bat"],
                      cwd=os.path.dirname(os.path.abspath(__file__)),
                      check=True)
        logger.info("Database services restarted successfully.")
        return True
    except Exception as e:
        logger.error(f"Error restarting database services: {e}")
        return False

def restart_server():
    """Restart the MultiFileRAG server."""
    logger.info("Restarting MultiFileRAG server...")
    try:
        # Kill any existing server processes
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq MultiFileRAG*"],
                      shell=True,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)

        # Start the server
        subprocess.Popen(["python", "multifilerag_server.py"],
                         cwd=os.path.dirname(os.path.abspath(__file__)),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

        logger.info("MultiFileRAG server restarted successfully.")
        return True
    except Exception as e:
        logger.error(f"Error restarting MultiFileRAG server: {e}")
        return False

def main():
    """Main function."""
    logger.info("Starting MultiFileRAG fix script...")

    # Fix document status table schema
    if not fix_document_status_schema():
        logger.error("Failed to fix document status table schema.")
        sys.exit(1)

    # Fix document status records
    if not fix_document_status_records():
        logger.error("Failed to fix document status records.")
        sys.exit(1)

    # Fix duplicate files
    if not fix_duplicate_files():
        logger.error("Failed to fix duplicate files.")
        sys.exit(1)

    # Restart databases
    if not restart_databases():
        logger.error("Failed to restart databases.")
        sys.exit(1)

    # Restart server
    if not restart_server():
        logger.error("Failed to restart server.")
        sys.exit(1)

    logger.info("MultiFileRAG fix script completed successfully.")
    logger.info("Please clear your browser cache and reload the page to see the changes.")

if __name__ == "__main__":
    main()
