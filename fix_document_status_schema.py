#!/usr/bin/env python3
"""
Fix Document Status Table Schema

This script checks and fixes the schema of the lightrag_doc_status table
to ensure it has all the required columns with the correct types.
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

def check_and_fix_schema():
    """Check and fix the schema of the lightrag_doc_status table."""
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
            
            return True
    except Exception as e:
        logger.error(f"Error checking and fixing schema: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function."""
    logger.info("Checking and fixing document status table schema...")
    success = check_and_fix_schema()
    if success:
        logger.info("Document status table schema fixed successfully.")
    else:
        logger.error("Failed to fix document status table schema.")
        sys.exit(1)

if __name__ == "__main__":
    main()
