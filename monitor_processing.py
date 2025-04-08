#!/usr/bin/env python3
"""
Script to monitor document processing performance in the MultiFileRAG system.
This script continuously checks the pipeline status and document counts.
It uses the multifilerag_utils module for API interaction.
"""

import sys
import time
from datetime import datetime
from multifilerag_utils import (
    get_pipeline_status, get_document_counts, get_server_url
)

def monitor_processing(interval=10, server_url=None):
    """Monitor document processing with periodic updates.

    Args:
        interval: Time between updates in seconds
        server_url: Server URL (default: from environment variables)
    """
    # Use default server URL if not provided
    if server_url is None:
        server_url = get_server_url()

    try:
        print(f"Monitoring document processing on {server_url}")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 80)

        while True:
            # Get current time
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Get pipeline status
            status = get_pipeline_status(server_url)

            # Get document counts
            counts = get_document_counts(server_url)

            # Print status
            print(f"\n[{now}] Pipeline Status:")

            if "error" in status:
                print(f"  Error: {status['error']}")
            else:
                busy = status.get("busy", False)
                job_name = status.get("job_name", "N/A")
                latest_message = status.get("latest_message", "N/A")

                print(f"  Busy: {busy}")
                print(f"  Job: {job_name}")
                print(f"  Latest Message: {latest_message}")

            # Print document counts
            print(f"\n[{now}] Document Counts:")

            if "error" in counts:
                print(f"  Error: {counts['error']}")
            else:
                pending = counts.get('PENDING', 0)
                processing = counts.get('PROCESSING', 0)
                processed = counts.get('PROCESSED', 0)
                failed = counts.get('FAILED', 0)
                total = counts.get('TOTAL', 0)

                print(f"  PENDING:    {pending}")
                print(f"  PROCESSING: {processing}")
                print(f"  PROCESSED:  {processed}")
                print(f"  FAILED:     {failed}")
                print(f"  TOTAL:      {total}")

            print("-" * 80)

            # Wait for the next update
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except ConnectionError as e:
        print(f"Connection error: {str(e)}")
    except TimeoutError as e:
        print(f"Timeout error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    # Get interval from command line argument or use default
    UPDATE_INTERVAL = 10
    if len(sys.argv) > 1:
        try:
            UPDATE_INTERVAL = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval: {sys.argv[1]}. Using default: 10 seconds.")

    # Get server URL from environment
    SERVER_URL = get_server_url()

    # Start monitoring
    monitor_processing(UPDATE_INTERVAL, SERVER_URL)
