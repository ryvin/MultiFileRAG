#!/usr/bin/env python3
"""
Fix Document Status Records

This script updates the document status records in the database to ensure they have
the required content and content_summary fields.
"""

import os
import sys
import asyncio
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

def fix_document_status_records():
    """Fix document status records in the database."""
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
            
            return True
    except Exception as e:
        logger.error(f"Error fixing document status records: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function."""
    logger.info("Starting document status fix...")
    success = fix_document_status_records()
    if success:
        logger.info("Document status fix completed successfully.")
    else:
        logger.error("Document status fix failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
