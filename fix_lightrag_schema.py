#!/usr/bin/env python3
"""
Fix Lightrag Schema

This script checks and fixes the schema of the lightrag_doc_full, lightrag_doc_chunks, and lightrag_llm_cache tables
to ensure they have all the required columns with the correct types.
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

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name=%s AND column_name=%s
        );
    """, (table_name.lower(), column_name.lower()))
    exists = cursor.fetchone()[0]
    logger.info(f"Checked column '{column_name}' in table '{table_name}': exists={exists}")
    return exists

def add_column_if_missing(cursor, table_name, column_name, column_type):
    """Add a column to a table if it does not exist."""
    if not column_exists(cursor, table_name, column_name):
        logger.info(f"Adding column '{column_name}' to table '{table_name}'...")
        cursor.execute(f'ALTER TABLE "{table_name.lower()}" ADD COLUMN "{column_name.lower()}" {column_type};')
        logger.info(f"Column '{column_name}' added to table '{table_name}'.")
    else:
        logger.info(f"Column '{column_name}' already exists in table '{table_name}'.")

def check_and_fix_lightrag_schema():
    """Check and fix the schema of lightrag_doc_full, lightrag_doc_chunks, and lightrag_llm_cache tables."""
    conn = get_postgres_connection()
    if not conn:
        logger.error("Could not connect to the database.")
        sys.exit(1)
    try:
        with conn:
            with conn.cursor() as cursor:
                # Fix lightrag_doc_full
                add_column_if_missing(cursor, "lightrag_doc_full", "update_time", "TIMESTAMP")
                # Fix lightrag_doc_chunks
                add_column_if_missing(cursor, "lightrag_doc_chunks", "tokens", "INTEGER")
                add_column_if_missing(cursor, "lightrag_doc_chunks", "chunk_order_index", "INTEGER")
                # Fix lightrag_llm_cache
                add_column_if_missing(cursor, "lightrag_llm_cache", "original_prompt", "TEXT")
                add_column_if_missing(cursor, "lightrag_llm_cache", "return_value", "TEXT")
                add_column_if_missing(cursor, "lightrag_llm_cache", "mode", "VARCHAR(32)")
        logger.info("Schema check and fix completed successfully.")
    except Exception as e:
        logger.error(f"Error while fixing schema: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_fix_lightrag_schema()